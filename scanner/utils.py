import subprocess
import re
import ipaddress
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