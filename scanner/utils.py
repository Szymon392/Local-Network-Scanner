import subprocess
import re
import ipaddress
import socket
async def get_live_hosts_from_arp(ip: str) -> list:
    ip_parts = ip.split('.')
    network_prefix = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}."

    try:
        result = subprocess.run(['arp', '-a'], capture_output = True, text = True, check = True)
        #print(result)
    except subprocess.CalledProcessError:
        return[]
    
    live_hosts = []
    pattern = re.compile(r"([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+).*?([0-9a-fA-F\-]{17})")
    for line in result.stdout.splitlines():
        match = pattern.search(line)
        if match:
            ip_str = match.group(1)

            if not ip_str.startswith(network_prefix): # is it in the local network?
                continue

            if ip_str.endswith(".255"): # is it broadcast?
                continue
                

            live_hosts.append(ip_str)
    
    return list(set(live_hosts))

async def get_ip_address() -> str:
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
                prefix_length = "24"
            
            network_address = ipaddress.IPv4Address("f{my_ip}/{prefix_length}", strict = False)
            return str(network_address)
    except Exception as e:
        print("Cannot get a proper network address - it is pre-set: '192.168.50.0/24'")
        return "192.168.50.0/24"