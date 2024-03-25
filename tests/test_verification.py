from rela.networkmodel import SimpleNC
from rela.verification.specverifier import SpecVerifier
from rela.language.regularir import *

def test_verification_basic():
    before_paths= [['a'], ['b']]
    after_paths = [['a'], ['c']]
    after_paths2 = [['a'], ['d']]
    after_paths3 = [['a'], ['b'], ['c']]

    change = P('b') * P('c') | I(~P('b'))
    spec = preState >> change == postState
    assert str(spec) == "preState ▶ ((b x c) + I(~b)) = postState"

    assert SpecVerifier.verify(spec, SimpleNC.from_single_fec(before_paths, after_paths)).is_passed() == True
    assert SpecVerifier.verify(spec, SimpleNC.from_single_fec(before_paths, after_paths2)).is_passed() == False
    assert SpecVerifier.verify(spec, SimpleNC.from_single_fec(before_paths, after_paths3)).is_passed() == False

    change1 = (P('b') * P('c')) // I(PStar(pDot))
    spec1 = preState >> change1 == postState
    assert str(spec1) == "preState ▶ (b x c) // I(.*) = postState"
    assert SpecVerifier.verify(spec1, SimpleNC.from_single_fec(before_paths, after_paths)).is_passed() == True
    assert SpecVerifier.verify(spec1, SimpleNC.from_single_fec(before_paths, after_paths2)).is_passed() == False
    assert SpecVerifier.verify(spec1, SimpleNC.from_single_fec(before_paths, after_paths3)).is_passed() == False

    change3 = RCompose(I(P('a') | P('b')), P('b') * P('c') | I(~P('b')))
    spec3 = preState >> change3 == postState
    assert str(spec3) == "preState ▶ I(a + b) o (b x c) + I(~b) = postState"
    assert SpecVerifier.verify(spec3, SimpleNC.from_single_fec(before_paths, after_paths)).is_passed() == True
    assert SpecVerifier.verify(spec3, SimpleNC.from_single_fec(before_paths, after_paths2)).is_passed() == False
    assert SpecVerifier.verify(spec3, SimpleNC.from_single_fec(before_paths, after_paths3)).is_passed() == False

    spec_inv = ~spec
    assert str(spec_inv) == "~(preState ▶ ((b x c) + I(~b)) = postState)"
    assert SpecVerifier.verify(spec_inv, SimpleNC.from_single_fec(before_paths, after_paths)).is_passed() == False
    assert SpecVerifier.verify(spec_inv, SimpleNC.from_single_fec(before_paths, after_paths2)).is_passed() == True
    assert SpecVerifier.verify(spec_inv, SimpleNC.from_single_fec(before_paths, after_paths3)).is_passed() == True

    change2 = P('b') * P('d') | I(~P('b'))
    spec2 = preState >> change2 == postState
    spec_disj = spec | spec2
    assert str(spec_disj) == "(preState ▶ ((b x c) + I(~b)) = postState) | (preState ▶ ((b x d) + I(~b)) = postState)"
    assert SpecVerifier.verify(spec_disj, SimpleNC.from_single_fec(before_paths, after_paths)).is_passed() == True
    assert SpecVerifier.verify(spec_disj, SimpleNC.from_single_fec(before_paths, after_paths2)).is_passed() == True

    spec_conj = spec & spec2
    assert str(spec_conj) == "(preState ▶ ((b x c) + I(~b)) = postState) & (preState ▶ ((b x d) + I(~b)) = postState)"
    assert SpecVerifier.verify(spec_conj, SimpleNC.from_single_fec(before_paths, after_paths)).is_passed() == False
    assert SpecVerifier.verify(spec_conj, SimpleNC.from_single_fec(before_paths, after_paths2)).is_passed() == False

def test_verification_subpath_replace():
    before_paths = [['r1', 'r2', 'r3']]
    after_paths = [['r1', 'r4', 'r3']]

    change = I(PStar(pDot)) + (P('r2') * P('r4')) + I(PStar(pDot))
    spec = preState >> change == postState
    assert str(spec) == "preState ▶ I(.*)(r2 x r4)I(.*) = postState"

    assert SpecVerifier.verify(spec, SimpleNC.from_single_fec(before_paths, after_paths)).is_passed() == True

def test_verification_link_expansion():
    before_paths = [['r1', 'r2', 'r3']]
    after_paths = [['r1', 'r2', 'r3'], ['r1', 'r4', 'r3']]

    change = I(PStar(pDot)) + (P('r2') * (P('r2') | P('r4'))) + I(PStar(pDot))
    spec = preState >> change == postState
    assert str(spec) == "preState ▶ I(.*)(r2 x (r2 + r4))I(.*) = postState"
    assert SpecVerifier.verify(spec, SimpleNC.from_single_fec(before_paths, after_paths)).is_passed() == True

    before_paths = [['r1', 'r2', 'r3']]
    after_paths = [['r1', 'r2', 'r3'], ['r1', 'r4', 'r3'], ['r1', 'r5', 'r3']]
    assert SpecVerifier.verify(spec, SimpleNC.from_single_fec(before_paths, after_paths)).is_passed() == False

    before_paths = [['r1', 'r2', 'r3']]
    after_paths = [['r1', 'r2', 'r3'], ['r1', 'r4', 'r3'], ['r1', 'r5', 'r3']]
    spec = preState >> change <= postState
    assert SpecVerifier.verify(spec, SimpleNC.from_single_fec(before_paths, after_paths)).is_passed() == True

    before_paths = [['r1', 'r2', 'r3'], ['r1', 'r5', 'r3']]
    after_paths = [['r1', 'r2', 'r3'], ['r1', 'r4', 'r3'], ['r1', 'r5', 'r3']]
    unchange = I(PStar(PNegSymbols('r2')))
    spec = preState >> (change | unchange) == postState
    assert str(spec) == "preState ▶ (I(.*)(r2 x (r2 + r4))I(.*) + I([^(r2)]*)) = postState"
    assert SpecVerifier.verify(spec, SimpleNC.from_single_fec(before_paths, after_paths)).is_passed() == True

def test_verification_example_1():
    change = P('a') * (P('a') | P('b')) + I(PStar(pDot)) + (P('c') * (P('c') | P('d')))
    spec = preState >> change == postState

    before_paths = [['a', 'c']]
    after_paths = [['a', 'c'], ['a', 'd'], ['b', 'c'], ['b', 'd']]
    assert SpecVerifier.verify(spec, SimpleNC.from_single_fec(before_paths, after_paths)).is_passed() == True

    before_paths = [['a', 'x', 'c']]
    after_paths = [['a', 'x', 'c'], ['a', 'x', 'd'], ['b', 'x', 'c'], ['b', 'x', 'd']]
    assert SpecVerifier.verify(spec, SimpleNC.from_single_fec(before_paths, after_paths)).is_passed() == True

    before_paths = [['a', 'x', 'c']]
    after_paths = [['a', 'x', 'c'], ['a', 'x', 'd'], ['b', 'x', 'c']]
    assert SpecVerifier.verify(spec, SimpleNC.from_single_fec(before_paths, after_paths)).is_passed() == False

    before_paths = [['a', 'x', 'c']]
    after_paths = [['a', 'x', 'c'], ['a', 'x', 'd'], ['b', 'x', 'c'], ['b', 'x', 'd'], ['b', 'y', 'd']]
    assert SpecVerifier.verify(spec, SimpleNC.from_single_fec(before_paths, after_paths)).is_passed() == False

    before_paths = [['a', 'c'], ['a', 'x', 'c']]
    after_paths = [['a', 'c'], ['a', 'd'], ['b', 'c'], ['b', 'd'], ['a', 'x', 'c'], ['a', 'x', 'd'], ['b', 'x', 'c'], ['b', 'x', 'd']]
    assert SpecVerifier.verify(spec, SimpleNC.from_single_fec(before_paths, after_paths)).is_passed() == True

def test_verification_example_2():
    change = I(PStar(pDot)) + (P('a') * (P('a') | P('b'))) + I(PStar(pDot))
    spec = preState | (preState >> change) == postState

    before_paths = [['a']]
    after_paths = [['a'], ['b']]
    assert SpecVerifier.verify(spec, SimpleNC.from_single_fec(before_paths, after_paths)).is_passed() == True

    before_paths = [['a']]
    after_paths = [['a']]
    assert SpecVerifier.verify(spec, SimpleNC.from_single_fec(before_paths, after_paths)).is_passed() == False

    before_paths = [['a'], ['c']]
    after_paths = [['a'], ['b'], ['c']]
    assert SpecVerifier.verify(spec, SimpleNC.from_single_fec(before_paths, after_paths)).is_passed() == True

    before_paths = [['a'], ['c']]
    after_paths = [['a'], ['b']]
    assert SpecVerifier.verify(spec, SimpleNC.from_single_fec(before_paths, after_paths)).is_passed() == False

    before_paths = [['c']]
    after_paths = [['c']]
    assert SpecVerifier.verify(spec, SimpleNC.from_single_fec(before_paths, after_paths)).is_passed() == True

def test_verification_example_3():
    domain = PIntersect(preState, (I(PStar(pDot)) + (P('a') * P('b')) + I(PStar(pDot))) << preState)
    change = I(PStar(pDot)) + (P('a') * P('c')) + I(PStar(pDot))
    spec = preState | (domain >> change) == postState
    assert str(spec) == "preState + (preState ∩ I(.*)(a x b)I(.*) ◀ preState) ▶ I(.*)(a x c)I(.*) = postState"

    before_paths = [['a'], ['b']]
    after_paths = [['a'], ['b'], ['c']]
    assert SpecVerifier.verify(spec, SimpleNC.from_single_fec(before_paths, after_paths)).is_passed() == True

    before_paths = [['a']]
    after_paths = [['a']]
    assert SpecVerifier.verify(spec, SimpleNC.from_single_fec(before_paths, after_paths)).is_passed() == True

    before_paths = [['a']]
    after_paths = [['a'], ['c']]
    assert SpecVerifier.verify(spec, SimpleNC.from_single_fec(before_paths, after_paths)).is_passed() == False
