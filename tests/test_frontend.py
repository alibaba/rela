from rela.language.frontend import *

def test_fe_construction():
    a = PSymbol('a')
    b = PSymbol('b')
    any = PStar(pDot)

    spec = ((a|b) % Remove(b)) \
        +  (any % Preserve()) 
    spec = spec \
        | (any % Preserve())
    assert str(spec) == 'a + b : remove(b);\n.* : preserve;\nelse .* : preserve;'