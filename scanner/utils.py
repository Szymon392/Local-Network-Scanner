import subprocess
import re
import ipaddress
import socket

from models import TargetHost

MAC_VENDORS = {
    "e8:9c:25": "Apple, Inc.",
    "00:1a:2b": "Samsung Electronics",
    "b8:27:eb": "Raspberry Pi Foundation",
    "dc:a6:32": "Raspberry Pi Trading",
    "00:50:56": "VMware, Inc.",
    "08:00:27": "Oracle VirtualBox",
    "00:14:22": "Dell Inc.",
    "f4:06:69": "Intel Corporate",
    "c0:25:e9": "TP-Link Technologies",
}

def get_vendor_by_mac(mac_address : str) -> str: # no need for async
    if not mac_address:
        return 
    if len(mac_address) >= 2 and mac_address[1].lower() in ['2', '6', 'a', 'e']:
        return "randomized"
    prefix = mac_address[:8]
    return MAC_VENDORS.get(prefix, "unknown")

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
                live_hosts.append(TargetHost(ip_str, mac_str, get_vendor_by_mac(mac_str)))

            except ValueError:
                continue
    
    return live_hosts

async def get_network_cidr() -> ipaddress.IPv4Network:
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