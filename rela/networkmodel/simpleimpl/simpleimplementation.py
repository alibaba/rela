from dataclasses import dataclass
from typing import Any, Dict, Iterator, List, Union

from ..networkpath import NetworkPath
from ..fec import PathFEC
from ..networkchange import NetworkChange

"""
This file contains the default implementation of NetworkChange and related
data models.
"""

@dataclass
class SimplePathFEC(PathFEC):
    """
    A plain dictionary implementation of PathFEC. Its key is a string
    presenting the key of the slice, and its value is a PathFECs.
    """
    before_paths: List[NetworkPath]
    after_paths: List[NetworkPath]
    ip_traffic_key: str = '0.0.0.0'

    def get_before_state(self) -> List[NetworkPath]:
        return self.before_paths
    
    def get_after_state(self) -> List[NetworkPath]:
        return self.after_paths
    
    def get_ip_traffic_keys(self) -> Any:
        return self.ip_traffic_key
    
    def compute_alphabet(self) -> set:
        """
        Compute the alphabet of the FEC.
        """
        res = set()
        for path in self.before_paths + self.after_paths:
            for hop in path:
                if isinstance(hop, str):
                    res.add(hop)
                elif isinstance(hop, list):
                    res.update(hop)
        return res

@dataclass
class SimpleNC(NetworkChange):
    """
    A plain dictionary implementation of NetworkChange. Its key is a string
    presenting the key of the slice, and its value is a PathFECs.
    """
    state: Dict[str, SimplePathFEC]

    @staticmethod
    def from_single_fec(before_paths: List[NetworkPath], after_paths: List[NetworkPath]):
        return SimpleNC({"0": SimplePathFEC(before_paths, after_paths)})
    
    @staticmethod
    def duplicate_state(state: Dict[str, List[NetworkPath]]):
        return SimpleNC({key: SimplePathFEC(before_paths, before_paths) for key, before_paths in state.items()})
    
    def get_fec(self, key: str) -> Union[PathFEC, None]:
        return self.state.get(key, None)
    
    def iterate(self) -> Iterator[PathFEC]:
        for fec in self.state.values():
            yield fec

    def count_fec(self) -> int:
        return len(self.state)
    
    def get_name(self) -> str:
        return f'SimpleNC({self.count_fec()} FECs)'