from abc import ABC, abstractmethod
from typing import Any, Set, Dict

class ForwardingGraph(ABC):
    """
    Abstract class for forwarding graphs.
    """
    @abstractmethod
    def get_alphabet(self) -> set:
        """
        Get the alphabet of the forwarding graph.
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_nodes(self) -> set:
        """
        Get the nodes of the forwarding graph.
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_out_edges(self, node: Any) -> Dict[Any, Set[str]]:
        """
        Get the outedges of a node.
        """
        raise NotImplementedError
    
    @abstractmethod
    def is_source(self, node: Any) -> bool:
        """
        Check if a node is a source.
        """
        raise NotImplementedError
    
    @abstractmethod
    def is_sink(self, node: Any) -> bool:
        """
        Check if a node is a sink.
        """
        raise NotImplementedError
    

    
