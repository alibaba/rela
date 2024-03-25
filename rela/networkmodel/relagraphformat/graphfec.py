from __future__ import annotations
from dataclasses import dataclass
from typing import List

from ..fec import GraphFEC
from ..forwardinggraph import ForwardingGraph
from .iptraffickey import IpTrafficKey

@dataclass
class RelaGraphFEC(GraphFEC):
    """
    Base class of FEC in Rela format. Each FEC contains a list of ip traffic
    keys and two forwarding graphs. The forwarding graphs can have different
    granularities.
    """
    ip_traffic_keys: List[IpTrafficKey]
    graph_before: ForwardingGraph
    graph_after: ForwardingGraph

    def get_before_state(self) -> ForwardingGraph:
        return self.graph_before
    
    def get_after_state(self) -> ForwardingGraph:
        return self.graph_after
    
    def compute_alphabet(self) -> set:
        return self.graph_before.get_alphabet().union(self.graph_after.get_alphabet())
    
    def get_ip_traffic_keys(self) -> List[str]:
        return [key.dstIp for key in self.ip_traffic_keys]