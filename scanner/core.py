import asyncio

async def scan_port(ip: str, port: int, timeout: float = 1.0) -> bool:
    """
    Asynchronously checks if a port is open.
    """
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
    for port in range(start_port, end_port + 1):
        tasks.append(scan_port(ip, port, timeout))
    
    results = await asyncio.gather(*tasks) # result is a list of bool values
    
    open_ports = []
    for port, is_open in zip(range(start_port, end_port + 1), results): # makes a pair (port_number, is_open)
        if is_open:
            open_ports.append(port)

    return open_ports