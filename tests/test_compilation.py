from rela.language.frontend import *
from rela.compilation.compiler import RelaCompiler

def test_fe_compilation_atomic():
    any = PStar(pDot)
    spec1 = any % Preserve()
    assert str(spec1) == '.* : preserve;'
    compiled1 = RelaCompiler.compile(spec1)
    assert str(compiled1) == 'preState ▶ I(.*) = postState ▶ I(.*)'
    
    a = P('a')
    b = P('b')
    spec2 = a % Add(b)
    assert str(spec2) == 'a : add(b);'
    compiled2 = RelaCompiler.compile(spec2)
    assert str(compiled2) == 'preState ▶ (I(a + b) + (a x b)) = postState ▶ I(a + b)'

    c = P('c')
    spec3 = (a|b) % Replace(b, c)
    assert str(spec3) == 'a + b : replace(b, c);'
    compiled3 = RelaCompiler.compile(spec3)
    assert str(compiled3) == 'preState ▶ (I(a + b + c ∩ ~b) + ((a + b ∩ b) x c)) = postState ▶ I(a + b + c)'

    spec4 = (a|b) % Remove(b)
    assert str(spec4) == 'a + b : remove(b);'
    compiled4 = RelaCompiler.compile(spec4)
    assert str(compiled4) == 'preState ▶ I(a + b ∩ ~b) = postState ▶ I(a + b)'

    spec5 = (a) % Drop()
    assert str(spec5) == 'a : drop;'
    compiled5 = RelaCompiler.compile(spec5)
    assert str(compiled5) == 'preState ▶ ((a + drop) x drop) = postState ▶ I(a + drop)'

    spec6 = (a|b) % Any(b)
    assert str(spec6) == 'a + b : any(b);'
    compiled6 = RelaCompiler.compile(spec6)
    assert str(compiled6) == 'preState ▶ ((a + b + b) x #1) = postState ▶ ((b x #1) + I(a + b ∩ ~b))'

def test_fe_compilation_concat():
    any = PStar(pDot)
    spec1 = any % Preserve()
    a = P('a')
    b = P('b')
    spec2 = a % Add(b)
    
    spec = spec1 + spec2
    assert str(spec) == '.* : preserve;\na : add(b);'
    compiled = RelaCompiler.compile(spec)
    assert str(compiled) == 'preState ▶ I(.*)(I(a + b) + (a x b)) = postState ▶ I(.*)I(a + b)'

def test_fe_compilation_else():
    any = PStar(pDot)
    spec1 = any % Preserve()
    a = P('a')
    b = P('b')
    spec2 = a % Add(b)
    
    spec = spec2 | spec1
    assert str(spec) == 'a : add(b);\nelse .* : preserve;'
    compiled = RelaCompiler.compile(spec)
    assert str(compiled) == 'preState ▶ (I(a + b) + (a x b) + I(~(a + b)) o I(.*)) = postState ▶ (I(a + b) + I(~(a + b)) o I(.*))'
