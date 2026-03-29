import subprocess
import re
import ipaddress
import socket
import asyncio

from models import TargetHost

from mac_vendor_lookup import AsyncMacLookup

mac_lookup_service = AsyncMacLookup()

async def get_vendor_by_mac(mac_address : str) -> str:
    """
    Function uses mac_vendor_lookup function - local-made library was inefficient adn too small,
    connecting to some API would be time-consuming
    """
    if not mac_address:
        return 
    
    mac_normalized = mac_address.replace("-", ":").lower()
    if len(mac_address) >= 2 and mac_address[1].lower() in ['2', '6', 'a', 'e']:
        return "randomized"
    
    try:
        return await mac_lookup_service.lookup(mac_normalized)
    except Exception:
        return "unknown"

async def get_live_hosts_from_arp(network_cidr: ipaddress.IPv4Network) -> list[TargetHost]:

    """
    - read information from ARP table
    - check for the 'ip-like' results
    - if match check if it really is a device in local network
    """

    try:
        result = subprocess.run(['arp', '-a'], capture_output = True, text = True, check = True)
        #print(result)
    except subprocess.CalledProcessError:
        return[]
    
    live_hosts = []
    ip_pattern = re.compile(r"([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+).*?([0-9a-fA-F\-]{17})")
    for line in result.stdout.splitlines():
        match = ip_pattern.search(line)
        if match:
            try:
                ip_str = match.group(1)
                mac_str = match.group(2)
                ip_object = ipaddress.ip_address(ip_str)

                if not ip_object in network_cidr:
                    continue

                if ip_object == network_cidr.network_address or ip_object == network_cidr.broadcast_address:
                        continue
                live_hosts.append(TargetHost(ip_str, mac_str, await get_vendor_by_mac(mac_str)))

            except ValueError:
                continue
    
    return live_hosts

def get_network_cidr() -> ipaddress.IPv4Network: # subprocess.run inside -> async would not help at all
    """
        - set the connection via UDP (just set not send anything) - it is connectionless but it will be prepared for connection (with proper ip)
        - read an ip from a proper network adapter - this way multiple number of virtual adapters (like from VMWare) is not a problem
        - make a powershell command to get a network prefix - so that it is not pre-set for /24
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            my_ip = s.getsockname()[0]
            ps_command = f"(Get-NetIPAddress -IPAddress '{my_ip}').PrefixLength"
            result = subprocess.run (
            ["powershell", "-NoProfile", "-Command", ps_command], capture_output = True, text = True, check = True
            )
            prefix_length = result.stdout.strip() 
            if not prefix_length:
                prefix_length = "24" # 99% of home networks
            
            network_cidr = ipaddress.IPv4Network(f"{my_ip}/{prefix_length}", strict = False)
            return network_cidr
    except Exception as e:
        print("Cannot get a proper network address - it is pre-set: '192.168.50.0/24'")
        return ipaddress.IPv4Network("192.168.50.0/24")
    
async def get_local_name(hosts_list : list[TargetHost]) -> list[TargetHost]:
    """
    The funcyion uses reverse DNS to get a localname of each host. it asks router using an ip address and receives a response
    As the 'gethostbyaddr' is not async function '.to_thread' was used.
    """
    dns_semaphore = asyncio.Semaphore(50)
    async def get_local_name_wrapper(dns_semaphore, ip):
        async with dns_semaphore:
            try:
                result =  await asyncio.to_thread(socket.gethostbyaddr, ip)
                return result[0]
            except Exception:
                return "Unknown"
    tasks = []
    for host in hosts_list:
        tasks.append(get_local_name_wrapper(dns_semaphore, host.ip))
    
    results = await asyncio.gather(*tasks)
    for i, host in enumerate(hosts_list):
        host.local_name = results[i]

    return hosts_list