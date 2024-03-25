from rela.language.regularir import Prop, P, PNegSymbols, pDot, PSymbol, PPredicate, PConcat, PUnion, PStar, PIntersect, PComplement, preState, postState, pEmptySet, pEpsilon, PNetworkStateBefore, PNetworkStateAfter, PEmptySet, PEpsilon
from rela.language.regularir import Rel, REmptySet, REpsilon, rEmptySet, rEpsilon, RIdentity, I, RProduct, RConcat, RStar, RUnion, RPriorityUnion, RCompose
from rela.language.regularir import Spec, SEqual, SSubsetEq, SNot, SAnd, SOr, SPrefixITE
from rela.language.ip.guard import IPGuard

def test_prop_construction():
    s1 = PSymbol('ab')
    s2 = PSymbol('c')
    s3 = PNegSymbols('e', 'f')
    s4 = PNegSymbols()
    s5 = PPredicate('role', 'a')
    assert isinstance(s1, Prop)
    assert isinstance(s2, Prop)
    assert isinstance(s3, Prop)
    assert isinstance(s4, Prop)
    assert isinstance(s5, Prop)

    prop1 = PConcat(s1, s2)
    prop2 = PUnion(prop1, s3)
    prop3 = PStar(s4)
    prop4 = PIntersect(prop2, prop3)
    prop5 = PComplement(prop4)
    prop6 = PUnion(prop5, preState, postState, pEmptySet, pEpsilon)

    assert isinstance(prop1, Prop)
    assert isinstance(prop2, Prop)
    assert isinstance(prop3, Prop)
    assert isinstance(prop4, Prop)
    assert isinstance(prop5, Prop)
    assert isinstance(prop6, Prop)
    assert str(prop6) == '~(abc + [^ef] ∩ .*) + preState + postState + 0 + 1'

def test_rel_construction():
    r1 = RIdentity(PSymbol('a'))
    r2 = RProduct(PSymbol('a'), PSymbol('b'))
    r3 = RConcat(r1, r2)
    r4 = RUnion(r3, RIdentity(PSymbol('d')))
    r5 = RStar(r4)
    r6 = RConcat(r5, rEpsilon, rEmptySet)
    r7 = RPriorityUnion(r6, RIdentity(pDot))
    r8 = RCompose(RIdentity(PStar(pDot)), r6)

    assert isinstance(r1, Rel)
    assert isinstance(r2, Rel)
    assert isinstance(r3, Rel)
    assert isinstance(r4, Rel)
    assert isinstance(r5, Rel)
    assert isinstance(r6, Rel)
    assert isinstance(r7, Rel)
    assert isinstance(r8, Rel)
    assert str(r6) == '(I(a)(a x b) + I(d))*10'
    assert str(r7) == '(I(a)(a x b) + I(d))*10 // I(.)'
    assert str(r8) == 'I(.*) o (I(a)(a x b) + I(d))*10'

def test_spec_construction():
    s1 = SEqual(PSymbol('a'), PSymbol('b'))
    s2 = SSubsetEq(PSymbol('c'), PSymbol('d'))
    s3 = SNot(s2)
    s4 = SAnd(s1, s3)
    s5 = SOr(s4, SEqual(PSymbol('e'), PSymbol('f')))

    assert isinstance(s1, Spec)
    assert isinstance(s2, Spec)
    assert isinstance(s3, Spec)
    assert isinstance(s4, Spec)
    assert isinstance(s5, Spec)

def test_alias():
    p1 = PSymbol('a')
    p2 = P('a')
    assert isinstance(p2, PSymbol)

    p4 = pDot
    assert isinstance(p4, PNegSymbols)

    r1 = RIdentity(PSymbol('a'))
    r2 = I(P('a'))
    assert isinstance(r2, RIdentity)

def test_singletons():
    x1 = PNetworkStateBefore()
    x2 = PNetworkStateBefore()
    assert x1 is x2
    assert x1 is preState
    y1 = PNetworkStateAfter()
    y2 = PNetworkStateAfter()
    assert y1 is y2
    assert y1 is postState
    p0 = PEmptySet()
    p1 = PEpsilon()
    assert p0 is pEmptySet
    assert p1 is pEpsilon
    r0 = REmptySet()
    r1 = REpsilon()
    assert r0 is rEmptySet
    assert r1 is rEpsilon

def test_prop_operator_override():
    # rel1 = a x (a + b)
    rel1 = RProduct(PSymbol('a'), PUnion(PSymbol('a'), PSymbol('b')))
    assert str(rel1) == 'a x (a + b)'

    # rel2 = a x (a + b), constructed using alias and operator override
    rel2 = P('a') * (P('a') | P('b'))
    assert str(rel2) == 'a x (a + b)'

    rel3 = I(~pEmptySet)
    assert str(rel3) == 'I(~0)'

    # test PImage override with >> operator
    p1 = P('a') >> rel2 
    p2 = rel2 << P('a')
    assert str(p1) == 'a ▶ (a x (a + b))'
    assert str(p2) == '(a x (a + b)) ◀ a'

def test_rel_operator_override():
    # rel1 = 0 // 1
    rel1 = rEmptySet // rEpsilon
    assert str(rel1) == '0 // 1'

def test_spec_operator_override():
    s1 = SEqual(PSymbol('a'), PSymbol('b'))
    s2 = SSubsetEq(PSymbol('c'), PSymbol('d'))

    s3 = ~s1
    assert str(s3) == '~(a = b)'
    s4 = s1 & s2
    assert str(s4) == '(a = b) & (c ⊆ d)'
    s5 = s1 | s2
    assert str(s5) == '(a = b) | (c ⊆ d)'

def test_pspec_construction():
    s1 = SEqual(PSymbol('a'), PSymbol('b'))
    s2 = SSubsetEq(PSymbol('c'), PSymbol('d'))
    g = IPGuard('10.0.0.0/8', '192.168.0.0/24')
    s3 = SPrefixITE(s1, s2, g)

    assert isinstance(s1, Spec)
    assert isinstance(s2, Spec)
    assert isinstance(s3, Spec)
    assert str(s3) == 'IF (10.0.0.0/8 192.168.0.0/24) THEN a = b ELSE c ⊆ d'






