import asyncio
import ipaddress

from models import TargetHost

class CoreNetworkScanner:
    def __init__(self, host_limit : int = 50, port_limit : int = 20, timeout: float = 1.0):
        self.timeout = timeout
        self.host_semaphore = asyncio.Semaphore(host_limit)
        self.port_semaphore = asyncio.Semaphore(port_limit)


    async def scan_port(self, ip: str, port: int) -> bool:
        """
        Asynchronously checks if a port is open.
        """
        async with self.port_semaphore:
            try:
                conn = asyncio.open_connection(ip, port)
                reader, writer = await asyncio.wait_for(conn, self.timeout)

                # no error up to this moment -> connection is possible
                writer.close()
                await writer.wait_closed()
                return True
            except Exception:
                return False

    async def scan_port_range(self, ip: str, start_port: int, end_port: int):
        """
        Scans a range of ports using asyncio.
        """
        tasks = []
        for port in range(start_port, end_port + 1):
            tasks.append(self.scan_port(ip, port))
        
        results = await asyncio.gather(*tasks) # result is a list of bool values
        
        open_ports = []
        for port, is_open in zip(range(start_port, end_port + 1), results): # makes a pair (port_number, is_open)
            if is_open:
                open_ports.append(port)

        return open_ports

    async def scan_network(self, network: ipaddress.IPv4Network):
        """
        This function exists ONLY to fill the ARP table

        If a network is large - scanning every host at the same time would be a problem
        Semaphore in this function limits the number of hosts the program tries to reach at the same time
        """

        async def scan_host_with_limit(ip : str):
            async with self.host_semaphore:
                return await self.scan_port(ip, 443) # port number doesn't matter
            
        tasks = []

        for ip in network.hosts():
            tasks.append(scan_host_with_limit(str(ip)))
        
        await asyncio.gather(*tasks)

        return
    
    async def scan_live_hosts(self, live_hosts : list[TargetHost], start_port: int = 1, end_port : int = 100) -> list[TargetHost]:
        """
        function made to scan a range of ports on a specific, live hosts, as scanning all at once would be too much
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
            host.open_ports = open_ports[i]
        return live_hosts