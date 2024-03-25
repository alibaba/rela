import pytest
import hfst
from rela.automata.utils import fst_zero, fst_one, fst_from_symbol, fst_from_symbols, fst_intersect, fst_union, fst_concat, fst_from_fsa_product, fst_complement, fst_from_neg_symbols, fst_from_path_set, fst_image
from rela.automata import FSTConstructor
from rela.networkmodel import SimpleNC
from rela.language.regularir import PNegSymbols, RIdentity, RProduct, PSymbol, RConcat, PStar, PComplement, RUnion, PEmptySet, RStar, pDot

def test_single_symbol():
    t = fst_from_symbol('a')
    assert t.lookup('a')[0][0] == 'a'

    t = fst_from_symbol('ab')
    assert t.lookup('ab')[0][0] == 'ab'

    t = fst_from_symbol('a|b') # should escape metacharacters
    assert t.lookup('a|b')[0][0] == 'a|b'

    # should reject empty string
    with pytest.raises(Exception):
        t = fst_from_symbol('')

    # should reject None
    with pytest.raises(Exception):
        t = fst_from_symbol(None)

def test_from_symbols():
    t = fst_from_symbols({'a', 'b'})
    assert t.lookup('a')[0][0] == 'a'
    assert t.lookup('b')[0][0] == 'b'

def test_from_neg_symbols():
    alphabet = {'a', 'b', 'c', 'd'}
    t = fst_from_neg_symbols({'a', 'b'}, alphabet)
    assert len(t.lookup('a')) == 0
    assert len(t.lookup('b')) == 0
    assert len(t.lookup('c')) > 0
    assert len(t.lookup('d')) > 0
    assert len(t.lookup('')) == 0
    assert len(t.lookup('e')) == 0

    # should reject None alphabet
    with pytest.raises(Exception):
        t = fst_from_neg_symbols({'a', 'b'}, None)

    # should reject None symbols
    with pytest.raises(Exception):
        t = fst_from_neg_symbols(None, alphabet)

    # when symbols is superset of alphabet
    t = fst_from_neg_symbols({'a', 'b', 'c', 'd', 'e'}, {'a', 'b', 'c', 'd'})
    assert t.compare(fst_zero())

    # when symbols is empty
    t = fst_from_neg_symbols(set(), {'a', 'b'})
    assert len(t.lookup('a')) > 0
    assert len(t.lookup('b')) > 0

    # when symbols and alphabet are disjoint
    t = fst_from_neg_symbols({'a', 'b'}, {'c', 'd'})
    assert len(t.lookup('c')) > 0
    assert len(t.lookup('d')) > 0

def test_concat():
    p1 = hfst.regex('a')
    p2 = hfst.regex('b')

    t = fst_concat(p1, p2)
    t.lookup_optimize()
    assert t.lookup('ab')[0][0] == 'ab'

    # len(args) == 1
    t = fst_concat(p1)
    assert t.lookup('a')[0][0] == 'a'

    # len(args) == 0
    t = fst_concat()
    assert t.compare(fst_zero())

def test_union():
    p1 = hfst.regex('a')
    p2 = hfst.regex('b')

    t = fst_union(p1, p2)
    t.lookup_optimize()
    assert t.lookup('a')[0][0] == 'a'
    assert t.lookup('b')[0][0] == 'b'

    # len(args) == 1
    t = fst_union(p1)
    assert t.lookup('a')[0][0] == 'a'

    # len(args) == 0
    t = fst_union()
    assert t.compare(fst_zero())

def test_intersect():
    p1 = hfst.regex('a')
    p2 = hfst.regex('b')

    t = fst_intersect(p1, fst_union(p1, p2))
    assert len(t.lookup('a')) == 1
    assert len(t.lookup('b')) == 0

    # len(args) == 1
    t = fst_intersect(p1)
    assert t.lookup('a')[0][0] == 'a'

    # len(args) == 0
    t = fst_intersect()
    assert t.compare(fst_zero())


def test_complement():
    p = hfst.regex('a')

    alphabet = {'a', 'b', 'c'}
    t = fst_complement(p, alphabet)
    assert len(t.lookup('a')) == 0
    assert len(t.lookup('b')) > 0
    assert len(t.lookup('c')) > 0
    assert len(t.lookup('')) > 0
    assert len(t.lookup('d')) == 0
    assert len(t.lookup('abc')) > 0

    # should reject None alphabet
    with pytest.raises(Exception):
        t = fst_complement(p, None)

def test_from_path_set():
    paths = [['R1'], ['R2', 'R3'], ['R4']]
    p = fst_from_path_set(paths)
    assert len(p.lookup('R1')) > 0
    assert len(p.lookup('R2R3')) > 0
    assert len(p.lookup('R4')) > 0

def test_from_path_set_escape():
    paths = [['R1'], ['R2|3', 'R3'], ['R4?']]
    p = fst_from_path_set(paths)
    assert len(p.lookup('R1')) > 0
    assert len(p.lookup('R2|3R3')) > 0
    assert len(p.lookup('R4?')) > 0
    assert len(p.lookup('R23R3')) == 0
    assert len(p.lookup('R4')) == 0

def test_from_network_state_fattree():
    paths = [['L4', ['S3', 'S4'], 'L3'], [['L1', 'L2'], ['S1', 'S2'], ['B1', 'B2'], ['S3', 'S4'], 'L3'], ['WAN', ['B1', 'B2'], ['S3', 'S4'], 'L3']]
    p = fst_from_path_set(paths)

    assert len(p.lookup('L4S3L3')) > 0
    assert len(p.lookup('L1S1B1S3L3')) > 0
    assert len(p.lookup('WANB2S3L3')) > 0

def test_compose_relation():
    p1 = hfst.regex('a')
    p2 = hfst.regex('b')

    t = fst_from_fsa_product(p1, p2)
    t.lookup_optimize()
    assert t.lookup('a')[0][0] == 'b'

def test_apply_relation():
    p = hfst.regex('a')
    r = hfst.regex('a:b')

    res = fst_image(p, r)
    assert len(res.lookup('a')) == 0
    assert len(res.lookup('b')) > 0

def test_apply_relation_fattree():
    paths =  [['L2', ['S1', 'S2'], 'L1'], [['L3', 'L4'], ['S3', 'S4'], ['B1', 'B2'], ['S1', 'S2'], 'L1'], ['WAN', ['B1', 'B2'], ['S1', 'S2'], 'L1']]
    p = fst_from_path_set(paths)

    alphabet = {'WAN', 'B1', 'B2', 'S1', 'S2', 'S3', 'S4', 'L1', 'L2', 'L3', 'L4'}

    rel_unchange = RIdentity(PStar(PNegSymbols('B1')))

    constructor = FSTConstructor(alphabet, None)
    fst_unchange = rel_unchange.accept(constructor)

    res = fst_image(p, fst_unchange)
    assert len(res.lookup('WANB1S1L1')) == 0 # changed to B2, so not contained by res
    assert len(res.lookup('WANB2S1L1')) > 0 # unchanged

def test_pnegsymbols():
    alphabet = {'a', 'b', 'c', 'd'}
    prop = PNegSymbols('a', 'b')
    
    constructor = FSTConstructor(alphabet, None)
    p = prop.accept(constructor)
    assert str(prop) == '[^ab]'
    assert len(p.lookup('a')) == 0
    assert len(p.lookup('b')) == 0
    assert len(p.lookup('c')) == 1
    assert len(p.lookup('d')) == 1

def test_pstar():
    state = {'10.0.0.0/24': [['L2', ['S1', 'S2'], 'L1'], [['L3', 'L4'], ['S3', 'S4'], ['B1', 'B2'], ['S1', 'S2'], 'L1'], ['WAN', ['B1', 'B2'], ['S1', 'S2'], 'L1']], '10.0.1.0/24': [['L1', ['S1', 'S2'], 'L2'], [['L3', 'L4'], ['S3', 'S4'], ['B1', 'B2'], ['S1', 'S2'], 'L2'], ['WAN', ['B1', 'B2'], ['S1', 'S2'], 'L2']], '10.0.2.0/24': [['L4', ['S3', 'S4'], 'L3'], [['L1', 'L2'], ['S1', 'S2'], ['B1', 'B2'], ['S3', 'S4'], 'L3'], ['WAN', ['B1', 'B2'], ['S3', 'S4'], 'L3']], '10.0.3.0/24': [['L3', ['S3', 'S4'], 'L4'], [['L1', 'L2'], ['S1', 'S2'], ['B1', 'B2'], ['S3', 'S4'], 'L4'], ['WAN', ['B1', 'B2'], ['S3', 'S4'], 'L4']], '0.0.0.0/0': [[['L1', 'L2'], ['S1', 'S2'], ['B1', 'B2'], 'WAN'], [['L3', 'L4'], ['S3', 'S4'], ['B1', 'B2'], 'WAN']]}
    state = SimpleNC.duplicate_state(state)
    p = fst_from_path_set(state.get_fec('10.0.0.0/24').get_before_state())

    alphabet = {'WAN', 'B1', 'B2', 'S1', 'S2', 'S3', 'S4', 'L1', 'L2', 'L3', 'L4'}

    prop = PStar(PNegSymbols('B1'))
    constructor = FSTConstructor(alphabet, None)
    constructor.alphabet = alphabet
    p = prop.accept(constructor)

    assert len(p.lookup('B1')) == 0
    assert len(p.lookup('B2')) == 1
    assert len(p.lookup('B2B1')) == 0
    assert len(p.lookup('B1B1')) == 0
    assert len(p.lookup('B2WANS2L1')) == 1

def test_rstar():
    state = {'10.0.0.0/24': [['L2', ['S1', 'S2'], 'L1'], [['L3', 'L4'], ['S3', 'S4'], ['B1', 'B2'], ['S1', 'S2'], 'L1'], ['WAN', ['B1', 'B2'], ['S1', 'S2'], 'L1']], '10.0.1.0/24': [['L1', ['S1', 'S2'], 'L2'], [['L3', 'L4'], ['S3', 'S4'], ['B1', 'B2'], ['S1', 'S2'], 'L2'], ['WAN', ['B1', 'B2'], ['S1', 'S2'], 'L2']], '10.0.2.0/24': [['L4', ['S3', 'S4'], 'L3'], [['L1', 'L2'], ['S1', 'S2'], ['B1', 'B2'], ['S3', 'S4'], 'L3'], ['WAN', ['B1', 'B2'], ['S3', 'S4'], 'L3']], '10.0.3.0/24': [['L3', ['S3', 'S4'], 'L4'], [['L1', 'L2'], ['S1', 'S2'], ['B1', 'B2'], ['S3', 'S4'], 'L4'], ['WAN', ['B1', 'B2'], ['S3', 'S4'], 'L4']], '0.0.0.0/0': [[['L1', 'L2'], ['S1', 'S2'], ['B1', 'B2'], 'WAN'], [['L3', 'L4'], ['S3', 'S4'], ['B1', 'B2'], 'WAN']]}
    state = SimpleNC.duplicate_state(state)
    p = fst_from_path_set(state.get_fec('10.0.0.0/24').get_before_state())

    alphabet = {'WAN', 'B1', 'B2', 'S1', 'S2', 'S3', 'S4', 'L1', 'L2', 'L3', 'L4'}

    rel_id = RIdentity(PStar(pDot))
    rel_no_star = RConcat(rel_id, RProduct(PSymbol('B1'), PSymbol('B2')), rel_id)
    rel = RStar(RUnion(RIdentity(PNegSymbols('B1')), RProduct(PSymbol('B1'), PSymbol('B2'))))
    
    constructor = FSTConstructor(alphabet, None)
    constructor.alphabet = alphabet
    t = rel.accept(constructor)
    t_no_star = rel_no_star.accept(constructor)
    t_no_star.lookup_optimize()
    assert len(set(t_no_star.lookup('B1'))) == 1 and list(set(t_no_star.lookup('B1')))[0][0] == 'B2'
    assert len(set(t_no_star.lookup('B1B1'))) == 2 # B2B1 and B1B2
    t.lookup_optimize()
    assert len(set(t.lookup('B1B1'))) == 1 and list(set(t.lookup('B1B1')))[0][0] == 'B2B2'