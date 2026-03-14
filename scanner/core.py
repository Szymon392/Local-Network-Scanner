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
    sem = asyncio.Semaphore(10)
    for port in range(start_port, end_port + 1):
        tasks.append(scan_port(sem, ip, port, timeout))
    
    results = await asyncio.gather(*tasks) # result is a list of bool values
    
    open_ports = []
    for port, is_open in zip(range(start_port, end_port + 1), results): # makes a pair (port_number, is_open)
        if is_open:
            open_ports.append(port)

    return open_ports

async def scan_network(network_cidr: str, start_port: int, end_port: int): # 'cidr' -> 192.168.1.0/24
    network = ipaddress.ip_network(network_cidr, strict=False)
    tasks = []

    for ip in network.hosts():
        tasks.append(scan_port_range(str(ip), start_port, end_port))
    
    ports = await asyncio.gather(*tasks)

    return zip(network.hosts(), ports)