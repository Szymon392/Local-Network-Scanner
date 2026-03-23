from dataclasses import dataclass, field
import socket

@dataclass
class TargetHost:
    ip: str
    mac: str
    vendor: str
    os: str = ""
    open_ports : list[PortInfo] = field(default_factory = list)

    def guess_os(self) -> str:
        port_numbers = {port.number for port in self.open_ports}
        if not port_numbers:
            return "Unknown (Firewall/Stealth)"
            
        if {135, 139, 445} & port_numbers:
            return "Windows"
            
        if {22, 111} & port_numbers:
            return "Linux / Unix"
            
        if {62078, 7000} & port_numbers:
            return "Apple (iOS/macOS)"
            
        if {515, 631, 9100} & port_numbers:
            return "Network Printer"
            
        if {53, 80, 443} & port_numbers:
            return "Network Device / Router"
            
        return "Unknown"

@dataclass
class PortInfo:
    number : int
    banner : str = ""
    service : str = ""

    def __post_init__(self):
        if not self.service:
            try:
                self.service = socket.getservbyport(self.number, 'tcp'.upper())
            except OSError:
                self.service = "UNKNOWN"