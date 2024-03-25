from typing import Any, Dict
from dataclasses import dataclass
import hfst

from ..language.regularir import PNegSymbols, PSymbol, PPredicate, PConcat, PUnion, PStar, PIntersect, PComplement, PNetworkStateBefore, PNetworkStateAfter, PEmptySet, PEpsilon, PImage, PReverseImage
from ..language.regularir import REmptySet, REpsilon, RIdentity, RProduct, RConcat, RStar, RUnion, RPriorityUnion

from ..language.regularir.rirvisitor import PropVisitor, RelVisitor
from..networkmodel.fec import FEC, PathFEC, GraphFEC

from .utils import fst_zero, fst_one, fst_from_symbol, fst_from_symbols, fst_from_neg_symbols, fst_concat, fst_union, fst_star, fst_intersect, fst_complement, fst_priority_union, fst_compose
from .utils import fst_from_path_set, fst_from_forwarding_graph, fst_image, fst_reverse_image, fst_from_fsa_product
from .utils import FST, FSA


"""
@author: Xieyang Xu
@date: 2023.07.05
@description: This file implements the visitor pattern for constructing FSTs for
Prop and Rel expressions.
"""

@dataclass
class FSTConstructor(PropVisitor, RelVisitor):
    """
    This class implements the visitor pattern for constructing FSTs for Prop and
    Rel expressions.
    """
    
    """Global state for FST constructions."""

    # alphabet: the set of unique symbols (network locations)
    alphabet: set 

    # fec: the preState and postState to be used for FST construction
    fec: FEC


    def visit_p_symbol(self, expr: PSymbol) -> FSA:
        """Constructs an FST for a Prop symbol expression."""
        return fst_from_symbol(expr.symbol)
    
    def visit_p_predicate(self, expr: PPredicate) -> FSA:
        """Constructs an FST for a Prop predicate expression."""
        return fst_from_symbols({symbol for symbol in self.alphabet if expr.value in symbol})
    
    def visit_p_neg_symbols(self, expr: PNegSymbols) -> FSA:
        """Constructs an FST for a Prop negated symbol set expression."""
        if self.alphabet is None:
            raise Exception('alphabet is not set')
        return fst_from_neg_symbols(set(expr.neg_symbols), self.alphabet)

    def visit_p_concat(self, expr: PConcat) -> FSA:
        """Constructs an FST for a Prop concatenation expression."""
        return fst_concat(*[sub_expr.accept(self) for sub_expr in expr.args])

    def visit_p_union(self, expr: PUnion) -> FSA:
        """Constructs an FST for a Prop union expression."""
        return fst_union(*[sub_expr.accept(self) for sub_expr in expr.args])

    def visit_p_star(self, expr: PStar) -> FSA:
        """Constructs an FST for a Prop star expression."""
        return fst_star(expr.arg.accept(self))

    def visit_p_intersect(self, expr: PIntersect) -> FSA:
        """Constructs an FST for a Prop intersection expression."""
        return fst_intersect(*[sub_expr.accept(self) for sub_expr in expr.args])

    def visit_p_complement(self, expr: PComplement) -> FSA:
        """Constructs an FST for a Prop complement expression."""
        if self.alphabet is None:
            raise Exception('alphabet is not set')
        return fst_complement(expr.arg.accept(self), self.alphabet)
    
    def _fst_from_fec(self, fec: FEC, is_pre_state: bool) -> FSA:
        state = fec.get_before_state() if is_pre_state else fec.get_after_state()
        if isinstance(fec, PathFEC):
            return fst_from_path_set(state)
        elif isinstance(fec, GraphFEC):
            return fst_from_forwarding_graph(state)
        else:
            raise Exception('Unsupported FEC type')

    def visit_p_network_state_before(self, expr: PNetworkStateBefore) -> FSA:
        """Constructs an FST for a Prop preState expression."""
        if self.fec is None:
            raise Exception('fec is not set')
        return self._fst_from_fec(self.fec, is_pre_state=True)

    def visit_p_network_state_after(self, expr: PNetworkStateAfter) -> FSA:
        """Constructs an FST for a Prop postState expression."""
        if self.fec is None:
            raise Exception('fec is not set')
        return self._fst_from_fec(self.fec, is_pre_state=False)

    def visit_p_empty_set(self, expr: PEmptySet) -> FSA:
        """Constructs an FST for a Prop empty set expression."""
        return fst_zero()

    def visit_p_epsilon(self, expr: PEpsilon) -> FSA:
        """Constructs an FST for a Prop epsilon expression."""
        return fst_one()

    def visit_p_image(self, expr: PImage) -> FSA:
        """Constructs an FST for a Prop image expression."""
        return fst_image(expr.prop.accept(self), expr.rel.accept(self))

    def visit_p_reverse_image(self, expr: PReverseImage) -> FSA:
        """Constructs an FST for a Prop reverse image expression."""
        return fst_reverse_image(expr.prop.accept(self), expr.rel.accept(self))

    def visit_r_empty_set(self, expr: REmptySet) -> FST:
        """Constructs an FST for a Rel empty set expression."""
        return fst_zero()

    def visit_r_epsilon(self, expr: REpsilon) -> FST:
        """Constructs an FST for a Rel epsilon expression."""
        return fst_one()

    def visit_r_identity(self, expr: RIdentity) -> FST:
        """Constructs an FST for a Rel identity expression."""
        return expr.arg.accept(self)

    def visit_r_product(self, expr: RProduct) -> FST:
        """Constructs an FST for a Rel product expression."""
        return fst_from_fsa_product(expr.p.accept(self), expr.q.accept(self))

    def visit_r_concat(self, expr: RConcat) -> FST:
        """Constructs an FST for a Rel concatenation expression."""
        return fst_concat(*[sub_expr.accept(self) for sub_expr in expr.args])

    def visit_r_union(self, expr: RUnion) -> FST:
        """Constructs an FST for a Rel union expression."""
        return fst_union(*[sub_expr.accept(self) for sub_expr in expr.args])

    def visit_r_star(self, expr: RStar) -> FST:
        """Constructs an FST for a Rel star expression."""
        return fst_star(expr.arg.accept(self))
    
    def visit_r_compose(self, expr: RUnion) -> FST:
        """Constructs an FST for a Rel union expression."""
        return fst_compose(*[sub_expr.accept(self) for sub_expr in expr.args])
    
    def visit_r_priority_union(self, expr: RPriorityUnion) -> FST:
        """Constructs an FST for a Rel priority union expression."""
        return fst_priority_union(*[sub_expr.accept(self) for sub_expr in expr.args])
