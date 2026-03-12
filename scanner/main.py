import asyncio
import argparse
import core

async def main():
    parser = argparse.ArgumentParser(description = "asynchrous local network scanner")

    parser.add_argument("-i", "--ip", type = str, default = "127.0.0.1", help = "target ip address (default: 127.0.0.1)")
    parser.add_argument("-s", "--start", type = int, default = 1, help = "target starting port (default: 1)")
    parser.add_argument("-e", "--end", type = int, default = 1024, help = "target end port (default: 1024)")
    parser.add_argument("-t", "--timeout", type = float, default = 1.0, help = "connection with port timeout in seconds (default: 1.0)")
    args = parser.parse_args()

    print(f"Scanning on port {args.ip}, range: {args.start} - {args.end}, timeout: {args.timeout}.")

    found_ports = await core.scan_port_range(args.ip, args.start, args.end, args.timeout)
    
    if found_ports:
        print(f"Found open ports: {found_ports} on ip: {args.ip}")
    else:
        print(f"Not found any open ports on ip: {args.ip}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Aborted by user!")