from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Set

from ..forwardinggraph import ForwardingGraph


@dataclass
class RelaLinkLevelForwardingGraph(ForwardingGraph):
    """
    An implementation of ForwardingGraph for Rela format. It represents a
    set of link-level forwarding paths.
    """
    graph: Dict[str, Dict[str, List[str]]]
    sources: Set[str]
    sinks: Set[str]

    def get_alphabet(self) -> Set[str]:
        alphabet = set()
        for node in self.graph.keys():
            for next_node in self.graph[node].keys():
                for interface_name in self.graph[node][next_node]:
                    alphabet.add(f"{next_node}|{interface_name}")
                # Handle sink nodes with no interface name
                if len(self.graph[node][next_node]) == 0:
                    alphabet.add(next_node)
        
        # First hop in Rela format is Device|Vrf, no need to add interface name
        alphabet.update(self.sources)           
        return alphabet
    
    def get_nodes(self) -> Set[str]:
        return set(self.graph.keys()).union(self.sinks)
    
    def get_out_edges(self, node: str) -> Dict[str, Set[str]]:
        """
        Represent the out edges of a node as a dictionary of
        {next_node: edges_from_node_to_next_node)}.
        Edge label format: {next_node}|{interface_name}
        """
        next_nodes = self.graph.get(node, set())
        res = {}
        for next_node in next_nodes:
            interface_names = self.graph[node][next_node]
            edges_to_next_node = {f"{next_node}|{interface_name}" for interface_name in interface_names}
            # Handle sink nodes with no interface name
            if len(interface_names) == 0:
                edges_to_next_node = {next_node}
            res[next_node] = edges_to_next_node
        return res
    
    def is_source(self, node: str) -> bool:
        return node in self.sources
    
    def is_sink(self, node: str) -> bool:
        return node in self.sinks
    
    @staticmethod
    def parse(input: dict) -> RelaLinkLevelForwardingGraph:
        return RelaLinkLevelForwardingGraph(
            graph=input["nodeToOutEdgesMap"],
            sources=set(input["sourceNodes"]),
            sinks=set(input["sinkNodes"])
        )
