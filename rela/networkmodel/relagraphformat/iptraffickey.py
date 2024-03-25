from dataclasses import dataclass

@dataclass(frozen=True)
class IpTrafficKey:
    srcIp: str
    dstIp: str
    qos: int

    @staticmethod
    def parse(mapping: dict) -> 'IpTrafficKey':
        return IpTrafficKey(mapping['srcIp'], mapping['dstIp'], mapping['qos'])