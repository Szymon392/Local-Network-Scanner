from dataclasses import dataclass, field

@dataclass
class TargetHost:
    ip: str
    mac: str
    vendor: str
    open_ports : list[int] = field(default_factory = list)