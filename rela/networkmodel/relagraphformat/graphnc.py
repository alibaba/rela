from __future__ import annotations
from dataclasses import dataclass
import functools
import json
import os
import logging
from typing import List, Union, Iterator

from ..networkchange import NetworkChange

from .graphfec import RelaGraphFEC
from .iptraffickey import IpTrafficKey
from .devicegrouplevel import RelaDeviceGroupLevelForwardingGraph
from .devicelevel import RelaDeviceLevelForwardingGraph
from .linklevel import RelaLinkLevelForwardingGraph



@dataclass
class RelaGraphNC(NetworkChange):
    """
    An implementation of NetworkChange for Rela format. It assumes that each
    FEC is given as a list of IpTrafficKey, and the before/after forwarding
    graphs.
    """
    slices: List[RelaGraphFEC]
    name: str
    
    def get_fec(self, key: IpTrafficKey) -> Union[RelaGraphFEC, None]:
        # TODO
        raise NotImplementedError
    
    def iterate(self) -> Iterator[RelaGraphFEC]:
        for slice in self.slices:
            yield slice

    def count_fec(self) -> int:
        return len(self.slices)
    
    def get_name(self) -> str:
        return self.name

    @staticmethod
    def from_json(json_file: str, precision: str = 'interface', mapping_file: str = None) -> RelaGraphNC:
        if precision == 'interface':
            graph_parser = RelaLinkLevelForwardingGraph.parse
        elif precision == 'device':
            graph_parser = RelaDeviceLevelForwardingGraph.parse
        elif precision == 'devicegroup':
            if mapping_file is None:
                raise ValueError("Mapping file is required for devicegroup level forwarding graph")
            with open(mapping_file) as f:
                mapping = json.load(f)
            graph_parser = functools.partial(RelaDeviceGroupLevelForwardingGraph.parse, mapping)
        else:
            raise ValueError(f"Unknown precision for Hoyan Graph: {precision}, should be 'interface' or 'device'")
        
        with open(json_file) as f:
            data = json.load(f)

        slices = []
        for i, slice in enumerate(data):
            try:
                fec = RelaGraphFEC(
                    ip_traffic_keys=[IpTrafficKey.parse(key) for key in slice['ipTrafficKeys']],
                    graph_before=graph_parser(slice['graphBefore']),
                    graph_after=graph_parser(slice['graphAfter'])
                )
            except Exception as e:
                logging.getLogger(__name__).warn(f"Error parsing FEC #{i} in {json_file}: {e}")
                fec = None # placeholder to keep the same number of FECs

            slices.append(fec)
        
        name = os.path.basename(json_file)
        return RelaGraphNC(slices, name)

