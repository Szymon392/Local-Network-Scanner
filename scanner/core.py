import asyncio
import ipaddress

from models import TargetHost, PortInfo

class CoreNetworkScanner:
    def __init__(self, host_limit : int = 20, port_limit : int = 50, timeout: float = 1.0):
        self.timeout = timeout
        self.host_semaphore = asyncio.Semaphore(host_limit)
        self.port_limit = port_limit

    async def scan_port_no_info(self, ip: str):
        """
        The purpose of this scan is to fulfill ARP table - NOT to grab any information
        """
        try:
            _, writer = await asyncio.wait_for(asyncio.open_connection(ip, 443), self.timeout)
            writer.close()
            await writer.wait_closed()
        except Exception:
            pass

    async def scan_network(self, network: ipaddress.IPv4Network):
        """
        This function exists ONLY to fill the ARP table

        If a network is large - scanning every host at the same time would be a problem
        Semaphore in this function limits the number of hosts the program tries to reach at the same time
        """

        async def scan_host_with_limit(ip : str):
            async with self.host_semaphore:
                return await self.scan_port_no_info(ip) # port number doesn't matter
            
        tasks = []

        for ip in network.hosts():
            tasks.append(scan_host_with_limit(str(ip)))
        
        await asyncio.gather(*tasks)

        return


    async def scan_port(self, ip: str, port: int) -> tuple[bool, str]:
        """
        The purpose of this function is to check if the port is open - if it is to grap banner
        """

        try:
            conn = asyncio.open_connection(ip, port)
            reader, writer = await asyncio.wait_for(conn, self.timeout)

            try:
                data = await asyncio.wait_for(reader.read(1024), timeout = 0.5)
                if not data:
                    raise asyncio.TimeoutError
            except asyncio.TimeoutError:
                writer.write(b"HEAD / HTTP/1.0\r\n\r\n")
                await writer.drain()
                
                try:
                    data = await asyncio.wait_for(reader.read(1024), timeout = 0.5)
                except asyncio.TimeoutError:
                    data = b""
            banner = ""

            if data:
                raw_banner = data.decode('utf-8', errors='ignore').strip()
                banner = raw_banner.split('\n')[0][:80]


            writer.close()
            await writer.wait_closed()
            return (True, banner)
        except Exception:
            return (False, "")

    async def scan_port_range(self, ip: str, start_port: int, end_port: int):
        """
        Scans a range of ports, uses wrapper to be able to limit the number of ports scanned in the same time.
        """
        port_semaphore = asyncio.Semaphore(self.port_limit)
        tasks = []
        async def scan_port_with_limit(ip, port):
            async with port_semaphore:
                return await self.scan_port(ip, port)

        for port in range(start_port, end_port + 1):
            tasks.append(scan_port_with_limit(ip, port))
        
        results = await asyncio.gather(*tasks) # result is a tuple of bool and str
        
        open_ports = []
        for port, (is_open, banner) in zip(range(start_port, end_port + 1), results): # makes a pair (port_number, is_open)
            if is_open:
                open_ports.append((port, banner))

        return open_ports
    
    async def scan_live_hosts(self, live_hosts : list[TargetHost], start_port: int = 1, end_port : int = 100) -> list[TargetHost]:
        """
        function made to scan a range of ports on a specific live hosts, as scanning all at once would be too much
        made a wrapper function and used semaphore (the same for this function and scan_netwrok)
        """

        async def scan_live_hosts_with_limit(ip : str, start_port: int, end_port: int):
            async with self.host_semaphore:
                return await self.scan_port_range(ip, start_port, end_port)
            
        tasks = []
        for host in live_hosts:
            tasks.append(scan_live_hosts_with_limit(host.ip, start_port, end_port))
        
        open_ports =  await asyncio.gather(*tasks)

        for i, host in enumerate(live_hosts):
            host.open_ports = [PortInfo(number = port_number, banner = banner) for port_number, banner in open_ports[i]]
        return live_hosts