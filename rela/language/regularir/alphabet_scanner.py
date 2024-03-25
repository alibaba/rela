from .rirvisitor import PropVisitor, RelVisitor, SpecVisitor


class AlphabetScanner(PropVisitor, RelVisitor, SpecVisitor):
    """
    Visitor that finds all symbols introduced by a expression.
    """

    def visit_s_equal(self, expr):
        return expr.p.accept(self) | expr.q.accept(self)
    
    def visit_s_subset_eq(self, expr):
        return expr.p.accept(self) | expr.q.accept(self)
    
    def visit_s_or(self, expr):
        return expr.p.accept(self) | expr.q.accept(self)
    
    def visit_s_and(self, expr):
        return expr.p.accept(self) | expr.q.accept(self)
    
    def visit_s_not(self, expr):
        return expr.p.accept(self)
    
    def visit_s_ite(self, expr):
        return expr.p.accept(self) | expr.q.accept(self)
    
    def visit_p_symbol(self, expr):
        return set([expr.symbol])
    
    def visit_p_predicate(self, expr):
        return set()
    
    def visit_p_neg_symbols(self, expr):
        return set(expr.neg_symbols)
    
    def visit_p_empty_set(self, expr):
        return set()
    
    def visit_p_epsilon(self, expr):
        return set()
    
    def visit_p_network_state_after(self, expr):
        return set()
    
    def visit_p_network_state_before(self, expr):
        return set()
    
    def visit_p_union(self, expr):
        return set.union(*[arg.accept(self) for arg in expr.args])
    
    def visit_p_concat(self, expr):
        return set.union(*[arg.accept(self) for arg in expr.args])
    
    def visit_p_star(self, expr):
        return expr.arg.accept(self)
    
    def visit_p_intersect(self, expr):
        return set.union(*[arg.accept(self) for arg in expr.args])
    
    def visit_p_complement(self, expr):
        return expr.arg.accept(self)
    
    def visit_p_image(self, expr):
        return expr.rel.accept(self) | expr.prop.accept(self)
    
    def visit_p_reverse_image(self, expr):
        return expr.rel.accept(self) | expr.prop.accept(self)
    
    def visit_r_product(self, expr):
        return expr.p.accept(self) | expr.q.accept(self)
    
    def visit_r_identity(self, expr):
        return expr.arg.accept(self)
    
    def visit_r_union(self, expr):
        return set.union(*[arg.accept(self) for arg in expr.args])
    
    def visit_r_concat(self, expr):
        return set.union(*[arg.accept(self) for arg in expr.args])
    
    def visit_r_star(self, expr):
        return expr.arg.accept(self)
    
    def visit_r_union(self, expr):
        return set.union(*[arg.accept(self) for arg in expr.args])
    
    def visit_r_empty_set(self, expr):
        return set()
    
    def visit_r_epsilon(self, expr):
        return set()
    
    def visit_r_compose(self, expr):
        return set.union(*[arg.accept(self) for arg in expr.args])
    
    def visit_r_priority_union(self, expr):
        return set.union(*[arg.accept(self) for arg in expr.args])