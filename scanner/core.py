import asyncio
import ipaddress

async def scan_port(semaphore: asyncio.Semaphore, ip: str, port: int, timeout: float = 1.0) -> bool:
    """
    Asynchronously checks if a port is open.
    """
    async with semaphore:
        try:
            conn = asyncio.open_connection(ip, port)
            reader, writer = await asyncio.wait_for(conn, timeout=timeout)
            # no error up to this moment -> connection is possible
            writer.close()
            await writer.wait_closed()
            return True
        except:
            return False

async def scan_port_range(ip: str, start_port: int, end_port: int, timeout: float = 1.0):
    """
    Scans a range of ports using asyncio.
    """
    tasks = []
    sem = asyncio.Semaphore(20)
    for port in range(start_port, end_port + 1):
        tasks.append(scan_port(sem, ip, port, timeout))
    
    results = await asyncio.gather(*tasks) # result is a list of bool values
    
    open_ports = []
    for port, is_open in zip(range(start_port, end_port + 1), results): # makes a pair (port_number, is_open)
        if is_open:
            open_ports.append(port)

    return open_ports

async def scan_network(network_cidr: str, start_port: int = 443, end_port: int = 443):
    """
    If a network is large - scanning every host at the same time would be a problem
    Semaphore in this function limits the number of hosts the program tries to reach at the same time
    """
    network = ipaddress.ip_network(network_cidr, strict=False)

    host_semaphore = asyncio.Semaphore(50)

    async def scan_host_with_limit(ip : str):
        async with host_semaphore:
            return await scan_port_range(ip, start_port, end_port)
        
    tasks = []

    for ip in network.hosts():
        tasks.append(scan_host_with_limit(ip))
    
    ports = await asyncio.gather(*tasks)

    return zip(network.hosts(), ports)
