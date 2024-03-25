from dataclasses import dataclass
from ipaddress import IPv4Network, IPv4Address

@dataclass(frozen=True, eq=False, init=False)
class IPGuard:
    prefix_list: tuple

    def __init__(self, *args):
        for arg in args:
            if not isinstance(arg, str):
                raise ValueError("IPGuard arguments must be valid IPv4 prefix strings")
            try:
                network = IPv4Network(arg, strict=False)
            except ValueError:
                raise ValueError("IPGuard arguments must be valid IPv4 prefix strings")

        object.__setattr__(self, 'prefix_list', tuple(args))

    def contains(self, dip: str) -> bool:
        try:
            ip = IPv4Address(dip)
            for prefix in self.prefix_list:
                network = IPv4Network(prefix, strict=False)
                if ip in network:
                    return True
            return False
        except ValueError:
            return False
    
    def __str__(self):
        return f"({' '.join(self.prefix_list)})"