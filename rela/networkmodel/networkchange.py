from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Iterator, List, Union, Any

from .networkpath import NetworkPath
from .fec import FEC


class NetworkChange(ABC):
    """
    Abstract class for network changes. A network change is a pair of network
    states before and after the change. Each network state contains the
    forwarding paths/graph of all flows in the network.
    For the sake of verification, we organize the network change as a set of 
    forwarding equivalence classes (FECs). Each FEC represents one or multiple 
    multiple packets that have the same forwarding behavior before and after 
    a network change.
    """
    @abstractmethod
    def get_fec(self, key: Any) -> Union[FEC, None]:
        """
        Get a FEC indicated by a key.
        The result should be a tuple of two lists of paths.
        """
        raise NotImplementedError
    
    @abstractmethod
    def iterate(self) -> Iterator[FEC]:
        """
        Iterate all FECs of the network state.
        """
        raise NotImplementedError
    
    @abstractmethod
    def count_fec(self) -> int:
        """
        Get the number of FECs in the network change.
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the name of the network change.
        """
        raise NotImplementedError