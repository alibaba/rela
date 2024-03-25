from typing import Tuple

from ..language.regularir import Prop, Rel, Spec
from ..language.regularir import I, PComplement, PIntersect, P, RCompose, PSymbol, PNegSymbols, PPredicate, PUnion, PConcat, PStar, pEmptySet, pEpsilon, preState, postState
from ..language.frontend.fevisitor import RegexVisitor, FESpecVisitor
from ..language.frontend.frontend import AtomicSpec, ConcatSpec, ElseSpec, FESpec
from ..language.frontend.frontend import Preserve, Add, Remove, Replace, Drop, Any


"""
@author: Xieyang Xu
@date: 2024.01.30
@description: This file implements the visitor pattern for compiling FE 
expressions intoRIR expressions.
"""

class RelaCompiler(RegexVisitor, FESpecVisitor):
    """
    This class implements the visitor pattern for compiling FE expressions into
    RIR expressions.
    """
    def __init__(self) -> None:
        self.hash_cnt = 0

    @staticmethod
    def compile(fe_spec: FESpec) -> Spec:
        """
        Compile the given FE spec into RIR spec.
        """
        if not isinstance(fe_spec, FESpec):
            raise ValueError("Input to RelaCompiler must be a FESpec")
        compiler = RelaCompiler()
        pre, post, _ = fe_spec.accept(compiler)
        return (preState >> pre) == (postState >> post)
    
    def visit_atomic_spec(self, expr: AtomicSpec) -> Tuple[Rel, Rel, Prop]:
        if isinstance(expr.m, Preserve):
            d : Prop = expr.r.accept(self)
            return I(d), I(d), d
        elif isinstance(expr.m, Add):
            d : Prop = expr.r.accept(self)
            p : Prop = expr.m.p.accept(self)
            return I(d|p) | (d * p), I(d|p), d|p
        elif isinstance(expr.m, Remove):
            d : Prop = expr.r.accept(self)
            p : Prop = expr.m.p.accept(self)
            return I(PIntersect(d, ~p)), I(d), d
        elif isinstance(expr.m, Replace):
            d : Prop = expr.r.accept(self)
            p1 : Prop = expr.m.p1.accept(self)
            p2 : Prop = expr.m.p2.accept(self)
            return I(PIntersect(d|p2, ~p1)) | (PIntersect(d, p1) * p2), I(d|p2), d|p2
        elif isinstance(expr.m, Drop):
            d : Prop = expr.r.accept(self)
            drop = P('drop')
            return (d | drop) * drop, I(d|drop), d|drop
        elif isinstance(expr.m, Any):
            d : Prop = expr.r.accept(self)
            p : Prop = expr.m.p.accept(self)
            self.hash_cnt += 1
            sharp = P(f'#{self.hash_cnt}')
            return (d | p) * sharp, (p * sharp) | I(PIntersect(d, ~p)), d|p
        else:
            raise NotImplementedError
    
    def visit_concat_spec(self, expr: ConcatSpec) -> Tuple[Rel, Rel, Prop]:
        pre1, post1, dom1 = expr.s1.accept(self)
        pre2, post2, dom2 = expr.s2.accept(self)
        return pre1 + pre2, post1 + post2, dom1 + dom2
    
    def visit_else_spec(self, expr: ElseSpec) -> Tuple[Rel, Rel, Prop]:
        pre1, post1, dom1 = expr.s1.accept(self)
        pre2, post2, dom2 = expr.s2.accept(self)
        return pre1 | RCompose(I(~dom1), pre2), post1 | RCompose(I(~dom1), post2), dom1 | dom2
    
    def visit_p_symbol(self, expr) -> Prop:
        return PSymbol(expr.symbol)
    
    def visit_p_predicate(self, expr) -> Prop:
        return PPredicate(expr.field, expr.value)
    
    def visit_p_neg_symbols(self, expr) -> Prop:
        return PNegSymbols(*expr.neg_symbols)
    
    def visit_p_empty_set(self, expr) -> Prop:
        return pEmptySet
    
    def visit_p_epsilon(self, expr) -> Prop:
        return pEpsilon
    
    def visit_p_union(self, expr) -> Prop:
        return PUnion(*[arg.accept(self) for arg in expr.args])
    
    def visit_p_concat(self, expr) -> Prop:
        return PConcat(*[arg.accept(self) for arg in expr.args])
    
    def visit_p_star(self, expr) -> Prop:
        return PStar(expr.arg.accept(self))
    
    def visit_p_intersect(self, expr) -> Prop:
        return PIntersect(*[arg.accept(self) for arg in expr.args])
    
    def visit_p_complement(self, expr) -> Prop:
        return PComplement(expr.arg.accept(self))