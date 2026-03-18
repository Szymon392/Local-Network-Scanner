import asyncio
import ipaddress

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

    async def scan_network(self, network: ipaddress.IPv4Network, start_port: int = 443, end_port: int = 443):
        """
        If a network is large - scanning every host at the same time would be a problem
        Semaphore in this function limits the number of hosts the program tries to reach at the same time
        """

        async def scan_host_with_limit(ip : str):
            async with self.host_semaphore:
                return await self.scan_port_range(ip, start_port, end_port)
            
        tasks = []

        for ip in network.hosts():
            tasks.append(scan_host_with_limit(str(ip)))
        
        ports = await asyncio.gather(*tasks)

        return list(zip(network.hosts(), ports))
