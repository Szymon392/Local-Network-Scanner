import asyncio
import argparse
import core
import utils

async def main():
    parser = argparse.ArgumentParser(description = "asynchrous local network scanner")

    parser.add_argument("-i", "--ip", type = str, default = "127.0.0.1", help = "target ip address (default: 127.0.0.1)")
    parser.add_argument("-s", "--start", type = int, default = 1, help = "target starting port (default: 1)")
    parser.add_argument("-e", "--end", type = int, default = 1024, help = "target end port (default: 1024)")
    parser.add_argument("-t", "--timeout", type = float, default = 1.0, help = "connection with port timeout in seconds (default: 1.0)")
    parser.add_argument("-d", "--default", action = "store_true", help = "Starts scanning on default settings")
    args = parser.parse_args()

    #Validation here

    network_cidr = await utils.get_network_cidr()
    scanner = core.CoreNetworkScanner(host_limit = 20, port_limit = 50, timeout = args.timeout)

    if (args.default == True):
        """
        'Default' setting makes the most efficient way to scan the entire network; works in 3 steps:
        1) scans every host on some port (port number doesnt matter) -> it fills ARP table
        2) alive hosts list is taken from ARP table
        3) live hosts are being scanned once again, this time on a specific range of ports (1 to 100 by default)
        """
        await scanner.scan_network(network_cidr)
        live_hosts = await utils.get_live_hosts_from_arp(network_cidr)
        live_hosts = await scanner.scan_live_hosts(live_hosts, 1, 1000)

        for host in live_hosts:
            print(host)

    else:

        print(f"Scanning on port {args.ip}, range: {args.start} - {args.end}, timeout: {args.timeout}.")

        found_ports = await scanner.scan_port_range(args.ip, args.start, args.end)
        print(found_ports)
        
        if found_ports:
            print(f"Found open ports: {found_ports} on ip: {args.ip}")
        else:
            print(f"Not found any open ports on ip: {args.ip}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Aborted by user!")