from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Set

from ..forwardinggraph import ForwardingGraph

@dataclass
class RelaDeviceGroupLevelForwardingGraph(ForwardingGraph):
    """
    An implementation of ForwardingGraph for Rela format. It represents a
    set of device-group-level forwarding paths.
    """
    graph: Dict[str, Set[str]]
    sources: Set[str]
    sinks: Set[str]

    def get_alphabet(self) -> Set[str]:
        return set(self.graph.keys()).union(self.sinks)
    
    def get_nodes(self) -> Set[str]:
        return set(self.graph.keys()).union(self.sinks)
    
    def get_out_edges(self, node: str) -> Dict[str, Set[str]]:
        """
        Represent the out edges of a node as a dictionary of 
        {next_node: edges_from_node_to_next_node)}.
        """
        next_nodes = self.graph.get(node, set())
        return {next_node: set([next_node]) for next_node in next_nodes}
    
    def is_source(self, node: str) -> bool:
        return node in self.sources
    
    def is_sink(self, node: str) -> bool:
        return node in self.sinks
    
    @staticmethod
    def parse(mapping: dict, input: dict) -> RelaDeviceGroupLevelForwardingGraph:
        # extract device-level graph
        graph = {}
        for node, out_edges in input["nodeToOutEdgesMap"].items():
            graph[node] = set(out_edges.keys())

        def replace(node: str) -> str:
            """
            Replace device names with device group names, while keeping the
            VRF name.
            """
            words = node.split('|')
            if len(words) != 2:
                return node
            device = words[0]
            return f"{mapping.get(device, device)}|{words[1]}"

        # rewrite device names to device group names
        rewritten_graph = {}
        for node, out_edges in graph.items():
            old = rewritten_graph.get(replace(node), set())
            rewritten_graph[replace(node)] = set([replace(next_node) for next_node in out_edges]).union(old)
        return RelaDeviceGroupLevelForwardingGraph(
            graph=rewritten_graph,
            sources=set([replace(node) for node in input["sourceNodes"]]),
            sinks=set([replace(node) for node in input["sinkNodes"]])
        )