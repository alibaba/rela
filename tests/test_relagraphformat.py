from rela.networkmodel.relagraphformat import RelaGraphNC, RelaGraphFEC, RelaLinkLevelForwardingGraph, RelaDeviceLevelForwardingGraph
from rela.verification.specverifier import SpecVerifier
from rela.language.regularir import *

    

def test_load_rela_graph_format_interface_level():
    state = RelaGraphNC.from_json('tests/data/example_rela_graph_network_state.json')
    assert isinstance(state, RelaGraphNC)
    assert isinstance(state.slices, list)
    assert len(state.slices) == 1

    # check fec format
    fec = state.slices[0]
    assert isinstance(fec, RelaGraphFEC)
    assert isinstance(fec.get_before_state(), RelaLinkLevelForwardingGraph)
    assert isinstance(fec.get_after_state(), RelaLinkLevelForwardingGraph)

    # check forwarding graph format
    before_graph = fec.get_before_state()
    # check alphabet
    assert before_graph.get_alphabet() == set(
        ['SPINE-3.DC3|vrf', 
         'BORDER-1.DC1|vrf|GigabitEthernet3/1/1', 
         'BORDER-2.DC1|vrf|GigabitEthernet3/0/1', 
         'drop'])
    # check nodes
    assert before_graph.get_nodes() == set(
        ['SPINE-3.DC3|vrf',
         'BORDER-1.DC1|vrf',
         'BORDER-2.DC1|vrf',
         'drop'])
    # check out edges
    assert before_graph.get_out_edges('SPINE-3.DC3|vrf') == {
        'BORDER-1.DC1|vrf': set(['BORDER-1.DC1|vrf|GigabitEthernet3/1/1']),
        'BORDER-2.DC1|vrf': set(['BORDER-2.DC1|vrf|GigabitEthernet3/0/1']),
    }
    assert before_graph.get_out_edges('BORDER-1.DC1|vrf') == {
        'drop': set(['drop']),
    }
    assert before_graph.get_out_edges('BORDER-2.DC1|vrf') == {
        'drop': set(['drop']),
    }
    # check sink
    assert before_graph.is_sink('drop') == True
    assert before_graph.is_sink('BORDER-1.DC1|vrf') == False
    assert before_graph.is_sink('BORDER-2.DC1|vrf') == False
    assert before_graph.is_sink('SPINE-3.DC3|vrf') == False
    assert before_graph.is_sink('') == False
    # check source
    assert before_graph.is_source('drop') == False
    assert before_graph.is_source('BORDER-1.DC1|vrf') == False
    assert before_graph.is_source('BORDER-2.DC1|vrf') == False
    assert before_graph.is_source('SPINE-3.DC3|vrf') == True
    assert before_graph.is_source('') == False

def test_load_rela_graph_format_device_level():
    state = RelaGraphNC.from_json('tests/data/example_rela_graph_network_state.json', precision='device')
    assert isinstance(state, RelaGraphNC)
    assert isinstance(state.slices, list)
    assert len(state.slices) == 1

    # check fec format
    fec = state.slices[0]
    assert isinstance(fec, RelaGraphFEC)
    assert isinstance(fec.get_before_state(), RelaDeviceLevelForwardingGraph)
    assert isinstance(fec.get_after_state(), RelaDeviceLevelForwardingGraph)

    # check forwarding graph format
    before_graph = fec.get_before_state()
    # check alphabet
    assert before_graph.get_alphabet() == set(
        ['SPINE-3.DC3|vrf',
            'BORDER-1.DC1|vrf',
            'BORDER-2.DC1|vrf',
            'drop'])
    # check nodes
    assert before_graph.get_nodes() == set(
        ['SPINE-3.DC3|vrf',
            'BORDER-1.DC1|vrf',
            'BORDER-2.DC1|vrf',
            'drop'])
    # check out edges
    assert before_graph.get_out_edges('SPINE-3.DC3|vrf') == {
        'BORDER-1.DC1|vrf': set(['BORDER-1.DC1|vrf']),
        'BORDER-2.DC1|vrf': set(['BORDER-2.DC1|vrf']),
    }
    assert before_graph.get_out_edges('BORDER-1.DC1|vrf') == {
        'drop': set(['drop']),
    }
    assert before_graph.get_out_edges('BORDER-2.DC1|vrf') == {
        'drop': set(['drop']),
    }
    # check sink
    assert before_graph.is_sink('drop') == True
    assert before_graph.is_sink('BORDER-1.DC1|vrf') == False
    assert before_graph.is_sink('BORDER-2.DC1|vrf') == False
    assert before_graph.is_sink('SPINE-3.DC3|vrf') == False
    assert before_graph.is_sink('') == False
    # check source
    assert before_graph.is_source('drop') == False
    assert before_graph.is_source('BORDER-1.DC1|vrf') == False
    assert before_graph.is_source('BORDER-2.DC1|vrf') == False
    assert before_graph.is_source('SPINE-3.DC3|vrf') == True
    assert before_graph.is_source('') == False


def test_verify_rela_graph_format_interface_level():
    state = RelaGraphNC.from_json('tests/data/example_rela_graph_network_state.json', precision='interface')
    verifier = SpecVerifier(state)

    two_links = P('BORDER-1.DC1|vrf|GigabitEthernet3/1/1') | P('BORDER-2.DC1|vrf|GigabitEthernet3/0/1')
    three_links = P('BORDER-1.DC1|vrf|GigabitEthernet3/1/1') | P('BORDER-2.DC1|vrf|GigabitEthernet3/0/1') | P('NEW-DEVICE|vrf|NEW-INTERFACE')
    change = I(PStar(pDot)) + (two_links * three_links) + I(PStar(pDot))
    unchange = I(PStar(PNegSymbols('BORDER-1.DC1|vrf|GigabitEthernet3/1/1', 'BORDER-2.DC1|vrf|GigabitEthernet3/0/1')))
    spec = preState >> (change | unchange) == postState

    assert spec.accept(verifier).is_passed() == True

def test_verify_rela_graph_format_device_level():
    state = RelaGraphNC.from_json('tests/data/example_rela_graph_network_state.json', precision='device')
    verifier = SpecVerifier(state)

    two_devices = P('BORDER-1.DC1|vrf') | P('BORDER-2.DC1|vrf')
    three_devices = P('BORDER-1.DC1|vrf') | P('BORDER-2.DC1|vrf') | P('NEW-DEVICE|vrf')
    change = I(PStar(pDot)) + (two_devices * three_devices) + I(PStar(pDot))
    unchange = I(PStar(PNegSymbols('BORDER-1.DC1|vrf', 'BORDER-2.DC1|vrf')))
    spec = preState >> (change | unchange) == postState

    assert spec.accept(verifier).is_passed() == True
def test_verify_rela_graph_format_device_level_pspec():

    state = RelaGraphNC.from_json('tests/data/example_rela_graph_network_state.json', precision='device')
    verifier = SpecVerifier(state)

    two_devices = P('BORDER-1.DC1|vrf') | P('BORDER-2.DC1|vrf')
    three_devices = P('BORDER-1.DC1|vrf') | P('BORDER-2.DC1|vrf') | P('NEW-DEVICE|vrf')
    change = I(PStar(pDot)) + (two_devices * three_devices) + I(PStar(pDot))
    unchange = I(PStar(PNegSymbols('BORDER-1.DC1|vrf', 'BORDER-2.DC1|vrf')))
    spec = preState >> (change | unchange) == postState
    assert spec.accept(verifier).is_passed() == True

    guard = IPGuard('10.0.0.0/8')
    spec1 = SPrefixITE(spec, preState == postState, guard)
    assert spec1.accept(verifier).is_passed() == False

    spec2 = SPrefixITE(preState == postState, spec, guard)
    assert spec2.accept(verifier).is_passed() == True

    guard2= IPGuard('11.0.0.0/8')
    spec3 = SPrefixITE(preState == postState, spec2, guard2)
    assert spec3.accept(verifier).is_passed() == True

    spec4 = SPrefixITE(spec2, preState == postState, guard2)
    assert spec4.accept(verifier).is_passed() == False
    

def test_verify_rela_graph_format_device_group_level():
    state = RelaGraphNC.from_json(
        json_file='tests/data/example_rela_graph_network_state.json', 
        precision='devicegroup',
        mapping_file='tests/data/example_rela_device_group_mapping.json')
    verifier = SpecVerifier(state)

    change = I(PStar(pDot)) + (P('BORDER.DC1|vrf') * (P('BORDER.DC1|vrf') | P('NEW-DEVICE|vrf'))) + I(PStar(pDot))
    unchange = I(PStar(PNegSymbols('BORDER.DC1|vrf')))
    spec = preState >> (change | unchange) == postState

    assert spec.accept(verifier).is_passed() == True

