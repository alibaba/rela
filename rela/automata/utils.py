from __future__ import annotations
from typing import Set, List
import hfst

from ..networkmodel.forwardinggraph import ForwardingGraph
from ..networkmodel.networkpath import NetworkPath

"""
@author: Xieyang Xu
@date: 2023.07.05
@description: This file implements FST operations for the construction of
Prop and Rel expressions. It is based on the HFST library.
"""

# type alias
FST = hfst.HfstTransducer
FSA = hfst.HfstTransducer

def fst_zero() -> hfst.HfstTransducer:
    """
    Construct the zero FST/FSA.
    Contains only the initial (non-accepting) state.
    """
    return hfst.HfstTransducer()

def fst_one() -> hfst.HfstTransducer:
    """
    Construct the one FST/FSA.
    Contains only the initial state, set to be accepting.
    """
    t = hfst.HfstBasicTransducer()
    t.set_final_weight(0, 0)
    return hfst.HfstTransducer(t)

_meta_char_set = set(['%', '_', '@', '#', '~', '\\', '&', '-', '$', '^', '*', '+', '?', '(', ')', '[', ']', '{', '}', '|', '<', '>', '.', '!', '=', ':', ';', '/', '`'])
def _escape(symbol: str) -> str:
    """
    Escape a symbol for use in Xerox transuder regular expressions.
    Using % as escape character.
    E.g., escape 'GROUP_ROUTER_城市|VRF' to 'GROUP%_ROUTER%_城市%|VRF'.
    """
    chars = ['%' + c if c in _meta_char_set else c for c in symbol]
    return ''.join(chars)

def fst_from_symbol(symbol: str) -> hfst.HfstTransducer:
    """
    Construct the FST/FSA that recognizes a single-symbol string.
    Contains two states and one transition:
    0 --symbol/symbol--> (1)
    """
    if not isinstance(symbol, str):
        raise Exception('symbol must be a string')
    
    t = hfst.regex(f'[{_escape(symbol)}]')

    # sanity check
    if t is None or t.number_of_states() != 2 or t.number_of_arcs() != 1:
        raise Exception(f'invalid symbol: {symbol}')
    
    return t

def fst_from_symbols(symbols: Set[str]) -> hfst.HfstTransducer:
    """
    Construct the FST/FSA that recognizes a set of symbols.
    Equivalent to the union of single-symbol FSTs for all symbols in the given
    symbol set.
    """
    if not isinstance(symbols, set):
        raise Exception('symbols must be a set')
    t = hfst.HfstBasicTransducer()
    t.add_state()
    t.set_final_weight(1, 0)
    for symbol in symbols:
        t.add_transition(0, 1, symbol, symbol)
    return hfst.HfstTransducer(t)

def fst_from_neg_symbols(symbols: Set[str], alphabet: Set[str]) -> hfst.HfstTransducer:
    """
    Construct the FST/FSA that recognizes negtive symbol groups such as [^ab].
    Equavalent to the union of single-symbol FSTs for all symbols not in the
    given symbol set.
    """
    if not isinstance(symbols, set):
        raise Exception('symbols must be a set')
    if not isinstance(alphabet, set):
        raise Exception('alphabet must be a set')
    pos_symbols = alphabet - symbols
    
    # res = fst_union(*[fst_from_symbol(symbol) for symbol in pos_symbols])
    # return res

    t = hfst.HfstBasicTransducer()
    t.add_state()
    t.set_final_weight(1, 0)
    for symbol in pos_symbols:
        t.add_transition(0, 1, symbol, symbol)
    return hfst.HfstTransducer(t)

def fst_concat(*args: hfst.HfstTransducer) -> hfst.HfstTransducer:
    """
    Implements the FST/FSA concatenation operation.
    """
    if len(args) == 0:
        return fst_zero()
    t = hfst.HfstTransducer(args[0])
    for arg in args[1:]:
        t.concatenate(arg)
    # t.remove_epsilons()
    return t

def fst_union(*args: hfst.HfstTransducer) -> hfst.HfstTransducer:
    """
    Implements the FST/FSA union operation.
    """
    if len(args) == 0:
        return fst_zero()
    t = hfst.HfstTransducer(args[0])
    for arg in args[1:]:
        t.disjunct(arg)
    #t.remove_epsilons()
    return t

def fst_priority_union(*args: hfst.HfstTransducer) -> hfst.HfstTransducer:
    """
    Implements the FST/FSA priority union operation.
    """
    if len(args) == 0:
        return fst_zero()
    t = hfst.HfstTransducer(args[0])
    for arg in args[1:]:
        t.priority_union(arg)
    #t.remove_epsilons()
    return t

def fst_compose(*args: hfst.HfstTransducer) -> hfst.HfstTransducer:
    """
    Implements the FST/FSA composition operation.
    """
    if len(args) == 0:
        return fst_zero()
    t = hfst.HfstTransducer(args[0])
    for arg in args[1:]:
        t.compose(arg)
    #t.remove_epsilons()
    return t

def fst_intersect(*args: hfst.HfstTransducer) -> hfst.HfstTransducer:
    """
    Implements the FST/FSA intersection operation.
    """
    if len(args) == 0:
        return fst_zero()
    t = hfst.HfstTransducer(args[0])
    for arg in args[1:]:
        t.intersect(arg)
    #t.remove_epsilons()
    return t

def fst_star(t: hfst.HfstTransducer) -> hfst.HfstTransducer:
    """
    Implements the FST/FSA Kleene star operation.
    """
    t = hfst.HfstTransducer(t)
    t.repeat_star()
    #t.remove_epsilons()
    return t


def _complete_fst(t: hfst.HfstBasicTransducer, alphabet: Set[str]) -> hfst.HfstBasicTransducer:
    """
    Complete the FST/FSA by adding all missing transitions to a sink state.
    Assume that the FST/FSA is already deterministic.
    The modification is done in-place.
    """
    if not isinstance(alphabet, set):
        raise Exception('alphabet must be a set')
    sink = t.add_state()
    for s, arcs in enumerate(t):
        exist_symbols = set([arc.get_input_symbol() for arc in arcs])
        for symbol in alphabet:
            if symbol not in exist_symbols:
                t.add_transition(s, sink, symbol, symbol)
    return t

def fst_complement(t: hfst.HfstTransducer, alphabet: Set[str]) -> hfst.HfstTransducer:
    """
    Implements the FST/FSA complement operation.
    """
    if not isinstance(alphabet, set):
        raise Exception('alphabet must be a set')

    # determination is necessary for complement algorithm
    t.determinize()
    t.minimize()
    t = hfst.HfstBasicTransducer(t)

    # complete the automaton by adding all missing transitions to a sink state
    t = _complete_fst(t, alphabet)

    # revert final states and non-final states
    for s in t.states():
        if t.is_final_state(s):
            t.remove_final_weight(s)
        else:
            t.set_final_weight(s, 0)
    return hfst.HfstTransducer(t)

def fst_from_path_set(paths: List[NetworkPath]) -> hfst.HfstTransducer:
    """
    Construct the FST/FSA from the network state.
    Equivalent to the union of all paths that start with the given prefix.
    """
    if paths is None or len(paths) == 0:
        return fst_zero()

    path_reprs = []
    for path in paths:
        hop_reprs = []
        for hop in path:
            if isinstance(hop, str):
                hop_reprs.append(f'[{_escape(hop)}]')
            elif isinstance(hop, list):
                hop_reprs.append(f'[{"|".join([f"[{_escape(node)}]" for node in hop])}]')
            else:
                raise Exception('invalid hop: {hop}')
        path_reprs.append(''.join(hop_reprs))
    network_state_repr = '|'.join(path_reprs)

    t = hfst.regex(network_state_repr)

    return t

def fst_from_forwarding_graph(graph: ForwardingGraph) -> hfst.HfstTransducer:
    """
    Construct the FST/FSA from the forwarding graph.
    """
    t = hfst.HfstBasicTransducer()
    states = {}

    # add states
    for node in graph.get_nodes():
        states[node] = t.add_state()
        # set sink nodes as final states
        if graph.is_sink(node):
            t.set_final_weight(states[node], 0)

    # add transitions
    for node in graph.get_nodes():
        for next_node, edges in graph.get_out_edges(node).items():
            for edge in edges:
                t.add_transition(states[node], states[next_node], edge, edge)

        # point the initial state to the source nodes
        if graph.is_source(node):
            t.add_transition(0, states[node], node, node)

    return hfst.HfstTransducer(t)

def fst_from_fsa_product(l: hfst.HfstTransducer, r: hfst.HfstTransducer) -> hfst.HfstTransducer:
    """
    Construct the FST that accepts all string pairs (x, y) where x is accepted
    by the left FSA and y is accepted by the right FSA.
    """
    t = hfst.HfstBasicTransducer()
    l = hfst.HfstTransducer(l)
    r = hfst.HfstTransducer(r)
    l.remove_epsilons()
    r.remove_epsilons()
    l = hfst.HfstBasicTransducer(l)
    r = hfst.HfstBasicTransducer(r)

    states = {(0, 0): 0} # mapping from (s_l, s_r) to state id in composed automata
    for s1 in l.states():
        for s2 in r.states():
            if s1 == 0 and s2 == 0: 
                s = states[(0, 0)]
            else:
                s = t.add_state() # skip initial state
                states[(s1, s2)] = s
            if l.is_final_state(s1) and r.is_final_state(s2):
                t.set_final_weight(s, 0)

    for s1, arcs1 in enumerate(l):
        for s2, arcs2 in enumerate(r):
            # 0. only DFA1 moves forward
            for arc1 in arcs1:
                t.add_transition(
                    states[(s1, s2)],
                    states[(arc1.get_target_state(), s2)],
                    arc1.get_input_symbol(),
                    hfst.EPSILON,
                    0)

            # 1. only DFA2 moves forward
            for arc2 in arcs2:
                t.add_transition(
                    states[(s1, s2)],
                    states[(s1, arc2.get_target_state())],
                    hfst.EPSILON,
                    arc2.get_input_symbol(),
                    0)

            # 2. both DFAs move forward
            for arc1 in arcs1:
                for arc2 in arcs2:
                    t.add_transition(
                        states[(s1, s2)],
                        states[(arc1.get_target_state(), arc2.get_target_state())], 
                        arc1.get_input_symbol(), 
                        arc2.get_input_symbol(), 
                        0)
    return hfst.HfstTransducer(t)

def fst_image(p: hfst.HfstTransducer, r: hfst.HfstTransducer) -> hfst.HfstTransducer:
    """
    Construct the FSA that represents the image of the given FSA under the 
    given relation.
    """
    p0 = p.copy()
    p0.compose(r)
    p0.output_project()
    return p0

def fst_reverse_image(p: hfst.HfstTransducer, r: hfst.HfstTransducer) -> hfst.HfstTransducer:
    """
    Construct the FSA that represents the reverse image of the given FSA under 
    the given relation.
    """
    r = hfst.HfstTransducer(r)
    r.invert()
    return fst_image(p, r)

def fst_minus(p: hfst.HfstTransducer, q: hfst.HfstTransducer) -> hfst.HfstTransducer:
    """
    Construct the FSA that represents the difference of the given FSAs (p - q).
    """
    t = p.copy()
    t.minus(q)
    return t

def fst_eq(p: hfst.HfstTransducer, q: hfst.HfstTransducer) -> bool:
    """
    Check whether two FSTs are equivalent.
    """
    return p.compare(q)

def fst_subseteq(p: hfst.HfstTransducer, q: hfst.HfstTransducer) -> bool:
    """
    Check whether the language of the first FST is a subset of the language of
    the second FST.
    """
    p0 = p.copy()
    p.intersect(q)
    return p0.compare(p)

def fst_lookup_optimize(t: hfst.HfstTransducer) -> hfst.HfstTransducer:
    """
    Optimize the given FST by converting it to a lookup FST. This operation is
    in-place.
    """
    t.lookup_optimize() # in-place
    return t

def fst_determinize(t: hfst.HfstTransducer) -> hfst.HfstTransducer:
    """
    Determinize the given FST. This operation is in-place.
    """
    t.determinize() # in-place
    return t

def fst_minimize(t: hfst.HfstTransducer) -> hfst.HfstTransducer:
    """
    Minimize the given FST. This operation is in-place.
    """
    t.minimize() # in-place
    return t

def fst_input_project(t: hfst.HfstTransducer) -> hfst.HfstTransducer:
    """
    Project the input of the given FST.
    """
    t0 = t.copy()
    t0.input_project()
    return t0

def fst_invert(t: hfst.HfstTransducer) -> hfst.HfstTransducer:
    """
    Invert the given FST.
    """
    t0 = t.copy()
    t0.invert()
    return t0

def fst_extract_paths(t: hfst.HfstTransducer) -> List[List[str]]:
    """
    Extract all paths from the given FST.
    """
    raw = t.extract_paths(output='raw', max_cycles=0)
    return [[hop[0] for hop in path[1]] for path in raw]

    


    

    

