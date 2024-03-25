from __future__ import annotations
from dataclasses import dataclass

from .fevisitor import RegexVisitor, FESpecVisitor


"""
@author: Xieyang Xu
@date: 2024.01.29
@description: This file contains the definition of the Rela front-end (FE)
language.
"""

class Regex():
    """
    Regex is the subset of the Prop language in RIR. They can be
    used to represent a set of network paths.
    The syntax of Regex expressions is defined as follows:
        Regex ::= PSymbol (str)
            | PNegSymbols (*list[str])
            | PPredicate (field, value)
            | PEmptySet
            | PEpsilon
            | PUion (Regex, Regex)
            | PConcat (Regex, Regex)
            | PStar (Regex)
            | PIntersect (Regex, Regex)
            | PComplement (Regex)
    """
    def __init__(self):
        pass

    def __add__(self, other):
        """
        Overload + operator for concatination.
        type: Regex + Regex -> Regex
        """
        if isinstance(other, Regex):
            return PConcat(self, other)
        else:
            return NotImplemented
        
    def __or__(self, other):
        """
        Overload | operator for union.
        type: Regex | Regex -> Regex
        """
        if isinstance(other, Regex):
            return PUnion(self, other)
        else:
            return NotImplemented
        
    def __invert__(self):
        """
        Overload ~ operator for complement.
        type: ~Regex -> Regex
        """
        return PComplement(self)
    
    def __mod__(self, other):
        """
        Overload % operator for AtomicSpec.
        type: Regex % Modifier -> AtomicSpec
        """
        if isinstance(other, Modifier):
            return AtomicSpec(self, other)
        else:
            return NotImplemented

class Modifier():
    """
    Base class for all Modifier expressions. 
    The syntax of Modifier expressions is defined as follows:
        Modifier ::= Preserve
            | Add (Regex)
            | Remove (Regex)
            | Replace (Regex, Regex)
            | Drop
            | Any (Regex)
            
    """
    def __init__(self):
        pass

class FESpec():
    """
    Base class for all FESpec expressions. 
    The syntax of FESpec expressions is defined as follows:
        FESpec ::= AtomicSpec (Regex, Modifier)
            | ConcatSpec (FESpec, FESpec)
            | ElseSpec (FESpec, FESpec)
    """
    def __init__(self):
        pass

    def __add__(self, other):
        """
        Overload + operator for concatination.
        type: FESpec + FESpec -> FESpec
        """
        if isinstance(other, FESpec):
            return ConcatSpec(self, other)
        else:
            return NotImplemented
        
    def __or__(self, other):
        """
        Overload | operator for concatination.
        type: FESpec + FESpec -> FESpec
        """
        if isinstance(other, FESpec):
            return ElseSpec(self, other)
        else:
            return NotImplemented
        
@dataclass(frozen=True, eq=False)
class PSymbol(Regex):
    """
    PSymbol is a Regex expression that represents a single network location.
    """
    symbol: str

    def __post_init__(self):
        if not isinstance(self.symbol, str):
            raise ValueError("PSymbol argument must be a string.")
        if self.symbol == "":
            raise ValueError("PSymbol argument cannot be an empty string.")

    def __str__(self):
        return self.symbol
    
    def accept(self, visitor: RegexVisitor):
        return visitor.visit_p_symbol(self)

# create an alias for PSymbol class called P
P = PSymbol

@dataclass(frozen=True, eq=False)
class PPredicate(Regex):
    """
    PPredicate is a Regex expression that represents a predicate over all locations
    in the network. It is used to represent a set of network locations that satisfy
    a certain predicate.
    """
    field: str
    value: str

    def __post_init__(self):
        if not isinstance(self.value, str):
            raise ValueError("PPredicate value must be a string.")
        if self.value == "":
            raise ValueError("PPredicate value cannot be an empty string.")

    def __str__(self):
        return f"{{{self.field}={self.value}}}"
    
    def accept(self, visitor: RegexVisitor):
        return visitor.visit_p_predicate(self)
    
# create an alias for PPredicate class called Pred
Pred = PPredicate
    
@dataclass(frozen=True, eq=False, init=False)
class PNegSymbols(Regex):
    """
    PNegSymbols is a Regex expression that represents a set of network
    locations that are not allowed to appear in a network path. It mimics the
    [^...] syntax in regular expressions.
    """
    neg_symbols: tuple[str]

    def __init__(self, *args):
        for arg in args:
            if not isinstance(arg, str):
                raise ValueError("PNegSymbols arguments must be strings.")
        object.__setattr__(self, 'neg_symbols', tuple(args))

    def __str__(self):
        if len(self.neg_symbols) == 0:
            return '.'
        symbol_strs = [sym if len(sym) == 1 else f"({sym})" for sym in self.neg_symbols]
        return f"[^{''.join(symbol_strs)}]"
    
    def accept(self, visitor: RegexVisitor):
        return visitor.visit_p_neg_symbols(self)
    
# create an alias for PNegSymbols() called pDot
pDot = PNegSymbols()

@dataclass(frozen=True, eq=False, init=False)
class PConcat(Regex):
    """
    PConcat is a Regex expression that represents the concatenation of two
    Regex expressions. This implementation supports concatenation of multiple
    Regex expressions.
    """
    args: tuple[Regex]

    def __init__(self, *args):
        if len(args) < 2:
            raise ValueError("PConcat must have at least two arguments.")
        for arg in args:
            if not isinstance(arg, Regex):
                raise ValueError("PConcat arguments must be Regex expressions.")
        object.__setattr__(self, 'args', tuple(args))

    def __str__(self):
        strs = []
        for arg in self.args:
            if isinstance(arg, PUnion) or isinstance(arg, PIntersect) or\
                isinstance(arg, PComplement) or (isinstance(arg, PSymbol) and len(arg.symbol) > 1):
                strs.append(f"({arg})")
            else:
                strs.append(str(arg))
        return ''.join(map(str, self.args))
    
    def accept(self, visitor: RegexVisitor):
        return visitor.visit_p_concat(self)

@dataclass(frozen=True, eq=False, init=False)
class PUnion(Regex):
    """
    PUnion is a Regex expression that represents the union of two Regex
    expressions. This implementation supports union of multiple Regex
    expressions.
    """
    args: tuple[Regex]

    def __init__(self, *args):
        if len(args) < 2:
            raise ValueError("PUnion must have at least two arguments.")
        for arg in args:
            if not isinstance(arg, Regex):
                raise ValueError("PUnion arguments must be Regex expressions.")
        object.__setattr__(self, 'args', tuple(args))

    def __str__(self):
        strs = []
        for arg in self.args:
            if isinstance(arg, PIntersect):
                strs.append(f"({arg})")
            else:
                strs.append(str(arg))
        return ' + '.join(map(str, self.args))
    
    def accept(self, visitor: RegexVisitor):
        return visitor.visit_p_union(self)

@dataclass(frozen=True, eq=False)
class PStar(Regex):
    """
    PStar is a Regex expression that represents the Kleene star of a Regex
    expression.
    """
    arg: Regex

    def __post_init__(self):
        if not isinstance(self.arg, Regex):
            raise ValueError("PStar argument must be a Regex expression.")

    def __str__(self):
        if isinstance(self.arg, PSymbol) or isinstance(self.arg, PNegSymbols):
            return str(self.arg) + '*'
        return '(' + str(self.arg) + ')*'
    
    def accept(self, visitor: RegexVisitor):
        return visitor.visit_p_star(self)

@dataclass(frozen=True, eq=False, init=False)
class PIntersect(Regex):
    """
    PIntersect is a Regex expression that represents the intersection of two
    Regex expressions. This implementation supports intersection of multiple
    Regex expressions.
    """
    args: tuple[Regex]

    def __init__(self, *args):
        if len(args) < 2:
            raise ValueError("PIntersect must have at least two arguments.")
        for arg in args:
            if not isinstance(arg, Regex):
                raise ValueError("PIntersect arguments must be Regex expressions.")
        object.__setattr__(self, 'args', tuple(args))

    def __str__(self):
        strs = []
        for arg in self.args:
            if isinstance(arg, PUnion) or isinstance(arg, PComplement):
                strs.append(f"({arg})")
            else:
                strs.append(str(arg))
        return ' ∩ '.join(map(str, self.args))
    
    def accept(self, visitor: RegexVisitor):
        return visitor.visit_p_intersect(self)

@dataclass(frozen=True, eq=False)
class PComplement(Regex):
    """
    PComplement is a Regex expression that represents the complement of a Regex
    expression (with respect to the free monoid generated by the alphabet).
    """
    arg: Regex

    def __post_init__(self):
        if not isinstance(self.arg, Regex):
            raise ValueError("PComplement argument must be a Regex expression.")

    def __str__(self):
        if isinstance(self.arg, PUnion) or isinstance(self.arg, PIntersect):
            return f"~({self.arg})"
        return f"~{self.arg}"
    
    def accept(self, visitor: RegexVisitor):
        return visitor.visit_p_complement(self)
    
class PEmptySet(Regex):
    """
    PEmptySet is a Regex expression that represents the empty set. PEmptySet is 
    implemented as a singleton.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PEmptySet, cls).__new__(cls)
        return cls._instance

    def __str__(self) -> str:
        return '0'
    
    def accept(self, visitor: RegexVisitor):
        return visitor.visit_p_empty_set(self)

# Instantiate pEmptySet as a singleton
pEmptySet = PEmptySet()

class PEpsilon(Regex):
    """
    PEpsilon is a Regex expression that represents the epsilon-string, ie, empty
    string. PEpsilon is implemented as a singleton.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PEpsilon, cls).__new__(cls)
        return cls._instance

    def __str__(self) -> str:
        return '1'
    
    def accept(self, visitor: RegexVisitor):
        return visitor.visit_p_epsilon(self)

# Instantiate pEpsilon as a singleton
pEpsilon = PEpsilon()
    
@dataclass(frozen=True, eq=False)
class Preserve(Modifier):

    def __str__(self):
        return 'preserve'

@dataclass(frozen=True, eq=False)
class Add(Modifier):
    p: Regex

    def __post_init__(self):
        if not isinstance(self.p, Regex):
            raise ValueError("Add argument must be a Regex expression.")

    def __str__(self):
        return f'add({self.p})'
    
@dataclass(frozen=True, eq=False)
class Remove(Modifier):
    p: Regex

    def __post_init__(self):
        if not isinstance(self.p, Regex):
            raise ValueError("Remove argument must be a Regex expression.")

    def __str__(self):
        return f'remove({self.p})'
    
@dataclass(frozen=True, eq=False)
class Replace(Modifier):
    p1: Regex
    p2: Regex

    def __post_init__(self):
        if not isinstance(self.p1, Regex):
            raise ValueError("Replace argument 1 must be a Regex expression.")
        if not isinstance(self.p2, Regex):
            raise ValueError("Replace argument 2 must be a Regex expression.")

    def __str__(self):
        return f'replace({self.p1}, {self.p2})'
    
@dataclass(frozen=True, eq=False)
class Drop(Modifier):

    def __str__(self):
        return 'drop'
    
@dataclass(frozen=True, eq=False)
class Any(Modifier):
    p: Regex

    def __post_init__(self):
        if not isinstance(self.p, Regex):
            raise ValueError("Any argument must be a Regex expression.")

    def __str__(self):
        return f'any({self.p})'
    
@dataclass(frozen=True, eq=False)
class AtomicSpec(FESpec):
    r: Regex
    m: Modifier

    def __post_init__(self):
        if not isinstance(self.r, Regex):
            raise ValueError("AtomicSpec argument 1 must be a Regex expression.")
        if not isinstance(self.m, Modifier):
            raise ValueError("AtomicSpec argument 2 must be a Modifier expression.")

    def __str__(self):
        return f'{self.r} : {self.m};'
    
    def accept(self, visitor: FESpecVisitor):
        return visitor.visit_atomic_spec(self)
    
@dataclass(frozen=True, eq=False)
class ConcatSpec(FESpec):
    s1: FESpec
    s2: FESpec

    def __post_init__(self):
        if not isinstance(self.s1, FESpec):
            raise ValueError("ConcatSpec argument 1 must be a FESpec expression.")
        if not isinstance(self.s2, FESpec):
            raise ValueError("ConcatSpec argument 2 must be a FESpec expression.")

    def __str__(self):
        return '\n'.join([str(self.s1), str(self.s2)])
    
    def accept(self, visitor: FESpecVisitor):
        return visitor.visit_concat_spec(self)
    
@dataclass(frozen=True, eq=False)
class ElseSpec(FESpec):
    s1: FESpec
    s2: FESpec

    def __post_init__(self):
        if not isinstance(self.s1, FESpec):
            raise ValueError("ElseSpec argument 1 must be a FESpec expression.")
        if not isinstance(self.s2, FESpec):
            raise ValueError("ElseSpec argument 2 must be a FESpec expression.")

    def __str__(self):
        return '\nelse '.join([str(self.s1), str(self.s2)])
    
    def accept(self, visitor: FESpecVisitor):
        return visitor.visit_else_spec(self)
    

    



    