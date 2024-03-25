from abc import ABC, abstractmethod
from typing import List, Any

from .networkpath import NetworkPath
from .forwardinggraph import ForwardingGraph


class FEC(ABC):
    """
    Abstract class for forwarding equivalence classes (FECs) in network changes.
    A FEC represents one or multiple packets that have the same forwarding
    behavior before and after a network change. It is represented by a tuple of
    two forwarding graphs or two set of forwarding paths.
    """
    @abstractmethod
    def get_before_state(self) -> Any:
        raise NotImplementedError
    
    @abstractmethod
    def get_after_state(self) -> Any:
        raise NotImplementedError
    
    @abstractmethod
    def get_ip_traffic_keys(self) -> Any:
        raise NotImplementedError
    
    @abstractmethod
    def compute_alphabet(self) -> set:
        """
        Compute the alphabet of the FEC.
        """
        raise NotImplementedError


class PathFEC(FEC):
    """
    Abstract class for FECs represented by forwarding paths.
    """
    @abstractmethod
    def get_before_state(self) -> List[NetworkPath]:
        """
        Get the paths before the change.
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_after_state(self) -> List[NetworkPath]:
        """
        Get the paths after the change.
        """
        raise NotImplementedError
    

class GraphFEC(FEC):
    """
    Abstract class for FECs represented by forwarding graphs.
    """
    @abstractmethod
    def get_before_state(self) -> ForwardingGraph:
        """
        Get the forwarding graph before the change.
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_after_state(self) -> ForwardingGraph:
        """
        Get the forwarding graph after the change.
        """
        raise NotImplementedError