from __future__ import annotations
from typing import Union
from dataclasses import dataclass

from .rirvisitor import PropVisitor, RelVisitor, SpecVisitor
from ..ip.guard import IPGuard

"""
@author: Xieyang Xu
@date: 2023.06.28
@description: This file contains the definition of the NetPR network change
specification language. This language models network states as set of paths,
and network changes as path transformations. It has the following syntax 
groups:
    - Prop: regular expressions over the alphabet of network locations that 
    recognize set of network paths.
    - Rel: "rational relations" over two sets of network paths. It can 
    represent a function that maps a set of network paths to another set of
    network paths.
    - Spec: an expression that represents what network paths transformations
    are allowed/expected in a network chenge. It incorporates both Prop and 
    Rel expressions. For example, the following expression
        preState ▶ change = postState
    specifies that by applying a Rel (change) on the pre-change network state,
    denoted by a Prop (preState), the resulted path set should be equal to the
    post-change network state, denoted by another Prop (postState).
This file contains the definition of the Prop, Rel, and Spec classes to present
NetPR as an embeded language in Python. An NetPR expression can be constructed
by instantiating one of these classes or composing multiple expressions using
overloaded operators. Expressions are represented in the abstract syntax tree
(AST) format, where each non-leaf node is an expression class denoting its root
operator and contains references to its child expressions.
"""

class Prop():
    """
    Prop is the base class for all Prop expressions. Prop expressions are
    regular expressions over the alphabet of network locations. They can be
    used to represent a set of network paths.
    The syntax of Prop expressions is defined as follows:
        Prop ::= PSymbol (str)
            | PNegSymbols (*list[str])
            | PPredicate (field, value)
            | PEmptySet
            | PEpsilon
            | PNetworkStateBefore
            | PNetworkStateAfter
            | PUion (Prop, Prop)
            | PConcat (Prop, Prop)
            | PStar (Prop)
            | PIntersect (Prop, Prop)
            | PComplement (Prop)
            | PImage (Prop, Rel)
            | PReverseImage (Prop, Rel)
    """
    def __init__(self):
        pass
    
    def __add__(self, other):
        """
        Overload + operator for concatination.
        type: Prop + Prop -> Prop
        """
        if isinstance(other, Prop):
            return PConcat(self, other)
        else:
            return NotImplemented
        
    def __or__(self, other):
        """
        Overload | operator for union.
        type: Prop | Prop -> Prop
        """
        if isinstance(other, Prop):
            return PUnion(self, other)
        else:
            return NotImplemented
        
    def __invert__(self):
        """
        Overload ~ operator for complement.
        type: ~Prop -> Prop
        """
        return PComplement(self)
        
    def __mul__(self, other):
        """
        Overload * operator for RProduct.
        type: Prop * Prop -> Rel
        """
        if isinstance(other, Prop):
            return RProduct(self, other)
        else:
            return NotImplemented
        
    def __rshift__(self, other):
        """
        Overload >> operator for PImage.
        type: Prop >> Rel -> Prop
        """
        if isinstance(other, Rel):
            return PImage(self, other)
        else:
            return NotImplemented
        
    def __eq__(self, other):
        """
        Overload == operator for SEqual.
        type: Prop == Prop -> Spec
        """
        if isinstance(other, Prop):
            return SEqual(self, other)
        else:
            return NotImplemented
        
    def __le__(self, other):
        """
        Overload <= operator for SSubsetEq.
        type: Prop <= Prop -> Spec
        """
        if isinstance(other, Prop):
            return SSubsetEq(self, other)
        else:
            return NotImplemented
        
    def accept(self, visitor: PropVisitor):
        raise NotImplementedError
        
class Rel():
    """
    Rel is the base class for all Rel expressions. Rel expressions are
    "rational relations" over two sets of network paths. They can be used to
    represent a function that maps a set of network paths to another set of
    network paths.
    The syntax of Rel expressions is defined as follows:
        Rel ::= RProdect (Prop, Prop)
            | REmptySet
            | REpsilon
            | RUnion (Rel, Rel)
            | RConcat (Rel, Rel)
            | RCompose (Rel, Rel)
            | RPriorityUnion(Rel, Rel)
            | RStar (Rel)
            | RIdentity (Prop)
    """
    def __init__(self):
        pass

    def __or__(self, other):
        """
        Overload | operator for union.
        type: Rel | Rel -> Rel
        """
        if isinstance(other, Rel):
            return RUnion(self, other)
        else:
            return NotImplemented
        
    def __add__(self, other):
        """
        Overload + operator for RConcat.
        type: Rel + Rel -> Rel
        """
        if isinstance(other, Rel):
            return RConcat(self, other)
        else:
            return NotImplemented
        
    def __floordiv__(self, other):
        """
        Overload // operator for RPriorityUnion.
        type: Rel // Rel -> Rel
        """
        if isinstance(other, Rel):
            return RPriorityUnion(self, other)
        else:
            return NotImplemented

    def __lshift__(self, other):
        """
        Overload << operator for PReverseImage.
        type: Rel << Prop -> Prop
        """
        if isinstance(other, Prop):
            return PReverseImage(other, self)
        else:
            return NotImplemented
        
    def accept(self, visitor: RelVisitor):
        raise NotImplementedError

class Spec():
    """
    Spec is the base class for all Spec expressions. Spec expressions are
    composed of Prop and Rel expressions. They can be used to represent
    network path transformations.
    The syntax of Spec expressions is defined as follows:
        Spec ::= SEqual (Prop, Prop)
            | SSubsetEq (Prop, Prop)
            | SOr (Spec, Spec)
            | SAnd (Spec, Spec)
            | SNot (Spec)
    """
    def accept(self, visitor: SpecVisitor):
        raise NotImplementedError
    
    def __or__(self, other):
        """
        Overload | operator for SOr.
        type: Spec | Spec -> Spec
        """
        if isinstance(other, Spec):
            return SOr(self, other)
        else:
            return NotImplemented
        
    def __and__(self, other):
        """
        Overload & operator for SAnd.
        type: Spec & Spec -> Spec
        """
        if isinstance(other, Spec):
            return SAnd(self, other)
        else:
            return NotImplemented
        
    def __invert__(self):
        """
        Overload ~ operator for SNot.
        type: ~Spec -> Spec
        """
        return SNot(self)


@dataclass(frozen=True, eq=False)
class PSymbol(Prop):
    """
    PSymbol is a Prop expression that represents a single network location.
    """
    symbol: str

    def __post_init__(self):
        if not isinstance(self.symbol, str):
            raise ValueError("PSymbol argument must be a string.")
        if self.symbol == "":
            raise ValueError("PSymbol argument cannot be an empty string.")

    def __str__(self):
        return self.symbol
    
    def accept(self, visitor: PropVisitor):
        return visitor.visit_p_symbol(self)

# create an alias for PSymbol class called P
P = PSymbol

@dataclass(frozen=True, eq=False)
class PPredicate(Prop):
    """
    PPredicate is a Prop expression that represents a predicate over all locations
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
    
    def accept(self, visitor: PropVisitor):
        return visitor.visit_p_predicate(self)
    
# create an alias for PPredicate class called Pred
Pred = PPredicate
    
@dataclass(frozen=True, eq=False, init=False)
class PNegSymbols(Prop):
    """
    PNegSymbols is a Prop expression that represents a set of network
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
    
    def accept(self, visitor: PropVisitor):
        return visitor.visit_p_neg_symbols(self)
    
# create an alias for PNegSymbols() called pDot
pDot = PNegSymbols()

@dataclass(frozen=True, eq=False, init=False)
class PConcat(Prop):
    """
    PConcat is a Prop expression that represents the concatenation of two
    Prop expressions. This implementation supports concatenation of multiple
    Prop expressions.
    """
    args: tuple[Prop]

    def __init__(self, *args):
        if len(args) < 2:
            raise ValueError("PConcat must have at least two arguments.")
        for arg in args:
            if not isinstance(arg, Prop):
                raise ValueError("PConcat arguments must be Prop expressions.")
        object.__setattr__(self, 'args', tuple(args))

    def __str__(self):
        strs = []
        for arg in self.args:
            if isinstance(arg, PUnion) or isinstance(arg, PIntersect) or\
                isinstance(arg, PComplement) or isinstance(arg, PImage) or\
                isinstance(arg, PReverseImage) or (isinstance(arg, PSymbol) and len(arg.symbol) > 1):
                strs.append(f"({arg})")
            else:
                strs.append(str(arg))
        return ''.join(map(str, self.args))
    
    def accept(self, visitor: PropVisitor):
        return visitor.visit_p_concat(self)

@dataclass(frozen=True, eq=False, init=False)
class PUnion(Prop):
    """
    PUnion is a Prop expression that represents the union of two Prop
    expressions. This implementation supports union of multiple Prop
    expressions.
    """
    args: tuple[Prop]

    def __init__(self, *args):
        if len(args) < 2:
            raise ValueError("PUnion must have at least two arguments.")
        for arg in args:
            if not isinstance(arg, Prop):
                raise ValueError("PUnion arguments must be Prop expressions.")
        object.__setattr__(self, 'args', tuple(args))

    def __str__(self):
        strs = []
        for arg in self.args:
            if isinstance(arg, PIntersect) or isinstance(arg, PImage) or\
                isinstance(arg, PReverseImage):
                strs.append(f"({arg})")
            else:
                strs.append(str(arg))
        return ' + '.join(map(str, self.args))
    
    def accept(self, visitor: PropVisitor):
        return visitor.visit_p_union(self)

@dataclass(frozen=True, eq=False)
class PStar(Prop):
    """
    PStar is a Prop expression that represents the Kleene star of a Prop
    expression.
    """
    arg: Prop

    def __post_init__(self):
        if not isinstance(self.arg, Prop):
            raise ValueError("PStar argument must be a Prop expression.")

    def __str__(self):
        if isinstance(self.arg, PSymbol) or isinstance(self.arg, PNegSymbols):
            return str(self.arg) + '*'
        return '(' + str(self.arg) + ')*'
    
    def accept(self, visitor: PropVisitor):
        return visitor.visit_p_star(self)

@dataclass(frozen=True, eq=False, init=False)
class PIntersect(Prop):
    """
    PIntersect is a Prop expression that represents the intersection of two
    Prop expressions. This implementation supports intersection of multiple
    Prop expressions.
    """
    args: tuple[Prop]

    def __init__(self, *args):
        if len(args) < 2:
            raise ValueError("PIntersect must have at least two arguments.")
        for arg in args:
            if not isinstance(arg, Prop):
                raise ValueError("PIntersect arguments must be Prop expressions.")
        object.__setattr__(self, 'args', tuple(args))

    def __str__(self):
        strs = []
        for arg in self.args:
            if isinstance(arg, PUnion) or isinstance(arg, PComplement) or\
             isinstance(arg, PImage) or isinstance(arg, PReverseImage):
                strs.append(f"({arg})")
            else:
                strs.append(str(arg))
        return ' ∩ '.join(map(str, self.args))
    
    def accept(self, visitor: PropVisitor):
        return visitor.visit_p_intersect(self)

@dataclass(frozen=True, eq=False)
class PComplement(Prop):
    """
    PComplement is a Prop expression that represents the complement of a Prop
    expression (with respect to the free monoid generated by the alphabet).
    """
    arg: Prop

    def __post_init__(self):
        if not isinstance(self.arg, Prop):
            raise ValueError("PComplement argument must be a Prop expression.")

    def __str__(self):
        if isinstance(self.arg, PUnion) or isinstance(self.arg, PIntersect)\
            or isinstance(self.arg, PImage) or isinstance(self.arg, PReverseImage):
            return f"~({self.arg})"
        return f"~{self.arg}"
    
    def accept(self, visitor: PropVisitor):
        return visitor.visit_p_complement(self)
    
class PNetworkStateBefore(Prop):
    """
    PNetworkStateBefore is a Prop expression that represents the set of all 
    network paths in the network state before a change. PNetworkStateBefore 
    is implemented as a singleton.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PNetworkStateBefore, cls).__new__(cls)
        return cls._instance

    def __str__(self):
        return 'preState'
    
    def accept(self, visitor: PropVisitor):
        return visitor.visit_p_network_state_before(self)

# Instantiate preState as a singleton
preState = PNetworkStateBefore()

class PNetworkStateAfter(Prop):
    """
    PNetworkStateAfter is a Prop expression that represents the set of all 
    network paths in the network state after a change. PNetworkStateAfter 
    is implemented as a singleton.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PNetworkStateAfter, cls).__new__(cls)
        return cls._instance

    def __str__(self) -> str:
        return 'postState'
    
    def accept(self, visitor: PropVisitor):
        return visitor.visit_p_network_state_after(self)

# Instantiate postState as a singleton
postState = PNetworkStateAfter()

class PEmptySet(Prop):
    """
    PEmptySet is a Prop expression that represents the empty set. PEmptySet is 
    implemented as a singleton.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PEmptySet, cls).__new__(cls)
        return cls._instance

    def __str__(self) -> str:
        return '0'
    
    def accept(self, visitor: PropVisitor):
        return visitor.visit_p_empty_set(self)

# Instantiate pEmptySet as a singleton
pEmptySet = PEmptySet()

class PEpsilon(Prop):
    """
    PEpsilon is a Prop expression that represents the epsilon-string, ie, empty
    string. PEpsilon is implemented as a singleton.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PEpsilon, cls).__new__(cls)
        return cls._instance

    def __str__(self) -> str:
        return '1'
    
    def accept(self, visitor: PropVisitor):
        return visitor.visit_p_epsilon(self)

# Instantiate pEpsilon as a singleton
pEpsilon = PEpsilon()

@dataclass(frozen=True, eq=False)
class PImage(Prop):
    """
    PImage is a Prop expression that represents the image of a Prop expression
    under a Rel expression.
    """
    prop: Prop
    rel: Rel

    def __post_init__(self):
        if not isinstance(self.prop, Prop):
            raise ValueError("PImage argument 1 must be a Prop expression.")
        if not isinstance(self.rel, Rel):
            raise ValueError("PImage argument 2 must be a Rel expression.")

    def __str__(self):
        if isinstance(self.prop, PUnion) or isinstance(self.prop, PIntersect)\
            or isinstance(self.prop, PImage) or isinstance(self.prop, PReverseImage):
            p_str = f"({self.prop})"
        else:
            p_str = str(self.prop)
        if isinstance(self.rel, RUnion) or isinstance(self.rel, RProduct):
            r_str = f"({self.rel})"
        else:
            r_str = str(self.rel)
            
        return f"{p_str} ▶ {r_str}"
    
    def accept(self, visitor: PropVisitor):
        return visitor.visit_p_image(self)

@dataclass(frozen=True, eq=False)
class PReverseImage(Prop):
    """
    PReverseImage is a Prop expression that represents the reverse image of a
    Prop expression under a Rel expression.
    """
    prop: Prop
    rel: Rel

    def __post_init__(self):
        if not isinstance(self.prop, Prop):
            raise ValueError("PReverseImage argument 2 must be a Prop expression.")
        if not isinstance(self.rel, Rel):
            raise ValueError("PReverseImage argument 1 must be a Rel expression.")

    def __str__(self):
        if isinstance(self.prop, PUnion) or isinstance(self.prop, PIntersect)\
            or isinstance(self.prop, PImage) or isinstance(self.prop, PReverseImage):
            p_str = f"({self.prop})"
        else:
            p_str = str(self.prop)
        if isinstance(self.rel, RUnion) or isinstance(self.rel, RProduct):
            r_str = f"({self.rel})"
        else:
            r_str = str(self.rel)

        return f"{r_str} ◀ {p_str}"
    
    def accept(self, visitor: PropVisitor):
        return visitor.visit_p_reverse_image(self)
    
@dataclass(frozen=True, eq=False)
class RProduct(Rel):
    """
    RProduct is a Rel expression that represents the product of two Prop
    expressions. It defines the relation that recognizes pairs of network paths
    (p1, p2) such that p1 is in the first Prop expression and p2 is in the
    second Prop expression.
    """
    p: Prop
    q: Prop

    def __post_init__(self):
        if not isinstance(self.p, Prop) or not isinstance(self.q, Prop):
            raise ValueError("RProduct arguments must be Prop expressions.")

    def __str__(self):
        if isinstance(self.p, PUnion) or isinstance(self.p, PIntersect) or\
            isinstance(self.p, PImage) or isinstance(self.p, PReverseImage):
            p_str = f"({self.p})"
        else:
            p_str = str(self.p)
        if isinstance(self.q, PUnion) or isinstance(self.q, PIntersect) or\
            isinstance(self.q, PImage) or isinstance(self.q, PReverseImage):
            q_str = f"({self.q})"
        else:
            q_str = str(self.q)
        return f"{p_str} x {q_str}"
    
    def accept(self, visitor: RelVisitor):
        return visitor.visit_r_product(self)
    
@dataclass(frozen=True, eq=False)
class RIdentity(Rel):
    """
    RIdentity is a Rel expression that represents the identity relation of a
    Prop expression. It defines the relation that recognizes pairs of network
    paths (p1, p1) such that p1 is in the Prop expression.
    """
    arg: Prop

    def __str__(self):
        return str(f"I({self.arg})")
    
    def accept(self, visitor: RelVisitor):
        return visitor.visit_r_identity(self)
    
# create an alias for RIdentity class called I
I = RIdentity

@dataclass(frozen=True, eq=False, init=False)
class RConcat(Rel):
    """
    RConcat is a Rel expression that represents the concatenation of two Rel
    expressions, denoted as r1 and r2. It defines the relation that recognizes
    pairs of network paths (p1p2, p3p4) such that (p1, p3) is in r1 and 
    (p2, p4) is in r2. This implementation supports concatenation of multiple
    Rel expressions.
    """
    args: tuple[Rel]

    def __init__(self, *args):
        if len(args) < 2:
            raise ValueError("RConcat requires at least two Rel arguments")
        for arg in args:
            if not isinstance(arg, Rel):
                raise ValueError("RConcat arguments must be Rel expressions")
        object.__setattr__(self, 'args', tuple(args))
        
    def __str__(self):
        strs = []
        for arg in self.args:
            if isinstance(arg, RUnion) or isinstance(arg, RProduct):
                strs.append(f"({arg})")
            else:
                strs.append(str(arg))
        return ''.join(strs)
    
    def accept(self, visitor: RelVisitor):
        return visitor.visit_r_concat(self)

@dataclass(frozen=True, eq=False, init=False)
class RUnion(Rel):
    """
    RUnion is a Rel expression that represents the union of two Rel expressions,
    denoted as r1 and r2. It defines the relation that recognizes pairs of
    network paths (p1, p2) such that (p1, p2) is in r1 or (p1, p2) is in r2.
    This implementation supports union of multiple Rel expressions.
    """
    args: tuple[Rel]

    def __init__(self, *args):
        if len(args) < 2:
            raise ValueError("RUnion requires at least two Rel arguments")
        for arg in args:
            if not isinstance(arg, Rel):
                raise ValueError("RUnion arguments must be Rel expressions")
        object.__setattr__(self, 'args', tuple(args))

    def __str__(self):
        strs = []
        for arg in self.args:
            if isinstance(arg, RProduct):
                strs.append(f"({arg})")
            else:
                strs.append(str(arg))
        return ' + '.join(strs)
    
    def accept(self, visitor: RelVisitor):
        return visitor.visit_r_union(self)
    
@dataclass(frozen=True, eq=False, init=False)
class RCompose(Rel):
    """
    RCompose is a Rel expression that represents the composition of 
    two Rel expressions. 
    This implementation supports union of multiple Rel expressions.
    """
    args: tuple[Rel]

    def __init__(self, *args):
        if len(args) < 2:
            raise ValueError("RCompose requires at least two Rel arguments")
        for arg in args:
            if not isinstance(arg, Rel):
                raise ValueError("RCompose arguments must be Rel expressions")
        object.__setattr__(self, 'args', tuple(args))

    def __str__(self):
        strs = []
        for arg in self.args:
            if isinstance(arg, RProduct):
                strs.append(f"({arg})")
            else:
                strs.append(str(arg))
        return ' o '.join(strs)
    
    def accept(self, visitor: RelVisitor):
        return visitor.visit_r_compose(self)
    
@dataclass(frozen=True, eq=False, init=False)
class RPriorityUnion(Rel):
    """
    RPriorityUnion is a Rel expression that represents the priority union of 
    two Rel expressions. Priority union is similar to unioin except that when
    an input string is accepted by both r1 and r2, the output is given by r2.
    This implementation supports union of multiple Rel expressions.
    """
    args: tuple[Rel]

    def __init__(self, *args):
        if len(args) < 2:
            raise ValueError("RPriorityUnion requires at least two Rel arguments")
        for arg in args:
            if not isinstance(arg, Rel):
                raise ValueError("RPriorityUnion arguments must be Rel expressions")
        object.__setattr__(self, 'args', tuple(args))

    def __str__(self):
        strs = []
        for arg in self.args:
            if isinstance(arg, RProduct):
                strs.append(f"({arg})")
            else:
                strs.append(str(arg))
        return ' // '.join(strs)
    
    def accept(self, visitor: RelVisitor):
        return visitor.visit_r_priority_union(self)

@dataclass(frozen=True, eq=False)
class RStar(Rel):
    """
    RStar is a Rel expression that represents the Kleene star of a Rel
    expression.
    """
    arg: Rel

    def __post_init__(self):
        if not isinstance(self.arg, Rel):
            raise ValueError("RStar argument must be a Rel expression")

    def __str__(self):
        if isinstance(self.arg, RConcat) or isinstance(self.arg, RUnion) or\
            isinstance(self.arg, RProduct):
            return '(' + str(self.arg) + ')*'
        return str(self.arg) + '*'
    
    def accept(self, visitor: RelVisitor):
        return visitor.visit_r_star(self)
    
class REmptySet(Rel):
    """
    REmptySet is a Rel expression that represents the empty relation. REmptySet
    is implemented as a singleton class.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(REmptySet, cls).__new__(cls)
        return cls._instance

    def __str__(self):
        return '0'
    
    def accept(self, visitor: RelVisitor):
        return visitor.visit_r_empty_set(self)

# initialize rEmptySet as a singleton
rEmptySet = REmptySet()

class REpsilon(Rel):
    """
    REpsilon is a Rel expression that recognizes any path pairs. REpsilon is
    implemented as a singleton class.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(REpsilon, cls).__new__(cls)
        return cls._instance

    def __str__(self):
        return '1'
    
    def accept(self, visitor: RelVisitor):
        return visitor.visit_r_epsilon(self)

# initialize rEpsilon as a singleton
rEpsilon = REpsilon()

@dataclass(frozen=True, eq=False)
class SEqual(Spec):
    """
    SEqual is a Spec expression that represents the equality of two Prop
    expressions.
    """
    p: Prop
    q: Prop

    def __post_init__(self):
        if not isinstance(self.p, Prop) or not isinstance(self.q, Prop):
            raise ValueError("SEqual arguments must be Prop expressions")

    def __str__(self):
        return f"{self.p} = {self.q}"
    
    def accept(self, visitor: SpecVisitor):
        return visitor.visit_s_equal(self)

@dataclass(frozen=True, eq=False)
class SSubsetEq(Spec):
    """
    SSubsetEq is a Spec expression that represents the subset relation of two
    Prop expressions.
    """
    p: Prop
    q: Prop

    def __post_init__(self):
        if not isinstance(self.p, Prop) or not isinstance(self.q, Prop):
            raise ValueError("SSubsetEq arguments must be Prop expressions")

    def __str__(self):
        return f"{self.p} ⊆ {self.q}"
    
    def accept(self, visitor: SpecVisitor):
        return visitor.visit_s_subset_eq(self)
    
@dataclass(frozen=True, eq=False)
class SOr(Spec):
    """
    SOr is a Spec expression that represents the disjunction of two Spec
    expressions.
    """
    p: Spec
    q: Spec

    def __post_init__(self):
        if not isinstance(self.p, Spec) or not isinstance(self.q, Spec):
            raise ValueError("SOr arguments must be Spec expressions")

    def __str__(self):
        return f"({self.p}) | ({self.q})"
    
    def accept(self, visitor: SpecVisitor):
        return visitor.visit_s_or(self)
    
@dataclass(frozen=True, eq=False)
class SAnd(Spec):
    """
    SAnd is a Spec expression that represents the conjunction of two Spec
    expressions.
    """
    p: Spec
    q: Spec

    def __post_init__(self):
        if not isinstance(self.p, Spec) or not isinstance(self.q, Spec):
            raise ValueError("SAnd arguments must be Spec expressions")

    def __str__(self):
        return f"({self.p}) & ({self.q})"
    
    def accept(self, visitor: SpecVisitor):
        return visitor.visit_s_and(self)
    
@dataclass(frozen=True, eq=False)
class SNot(Spec):
    """
    SNot is a Spec expression that represents the negation of a Spec expression.
    """
    p: Spec

    def __post_init__(self):
        if not isinstance(self.p, Spec):
            raise ValueError("SNot argument must be a Spec expression")

    def __str__(self):
        return f"~({self.p})"
    
    def accept(self, visitor: SpecVisitor):
        return visitor.visit_s_not(self)
    
@dataclass(frozen=True, eq=False)
class SPrefixITE(Spec):
    """
    SPrefixITE is a Spec expression that represents an If-Then-Else
    structure:
    IF dip in prefix:
    THEN p
    ELSE q
    """
    p: Spec
    q: Spec
    guard: IPGuard

    def __post_init__(self):
        if not isinstance(self.p, Spec) or not isinstance(self.q, Spec):
            raise ValueError("SPrefixITE arguments 1 & 2 must be Spec expressions")
        if not isinstance(self.guard, IPGuard):
            raise ValueError("SPrefixITE arguments 3 must be IPGuard")

    def __str__(self):
        return f"IF {self.guard} THEN {self.p} ELSE {self.q}"
    
    def accept(self, visitor: SpecVisitor):
        return visitor.visit_s_ite(self)