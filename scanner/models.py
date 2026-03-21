from dataclasses import dataclass, field

@dataclass
class TargetHost:
    ip: str
    mac: str
    vendor: str
    open_ports : list[PortInfo] = field(default_factory = list)

    def guess_os(self) -> str:
        port_numbers = {port.number for port in self.open_ports}

        if not port_numbers:
            return "Unknown (not a port open)"
        
        if {135, 445}.issubset(port_numbers):
            return "Windows"
        
        if {22}.issubset(port_numbers):
            return "Linux / Unix / MacOS"
        
        if ({80, 443}.intersection(port_numbers) and len(port_numbers) <= 3):
            return "Network device"
        
        return "unkown"

@dataclass
class PortInfo:
    number : int
    banner : str = ""