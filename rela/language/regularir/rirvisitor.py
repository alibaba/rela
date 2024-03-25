from abc import ABC, abstractmethod

"""
@author: Xieyang Xu
@date: 2023.07.05
@description: This file implements the visitor class for expressions.
"""

class PropVisitor(ABC):
    """Abstract base class for expression visitors."""
    @abstractmethod
    def visit_p_symbol(self, expr):
        raise NotImplementedError
    
    @abstractmethod
    def visit_p_predicate(self, expr):
        raise NotImplementedError
    
    @abstractmethod
    def visit_p_neg_symbols(self, expr):
        raise NotImplementedError
    
    @abstractmethod
    def visit_p_empty_set(self, expr):
        raise NotImplementedError
    
    @abstractmethod
    def visit_p_epsilon(self, expr):
        raise NotImplementedError
    
    @abstractmethod
    def visit_p_network_state_after(self, expr):
        raise NotImplementedError
    
    @abstractmethod
    def visit_p_network_state_before(self, expr):
        raise NotImplementedError
    
    @abstractmethod
    def visit_p_union(self, expr):
        raise NotImplementedError
    
    @abstractmethod
    def visit_p_concat(self, expr):
        raise NotImplementedError
    
    @abstractmethod
    def visit_p_star(self, expr):
        raise NotImplementedError
    
    @abstractmethod
    def visit_p_intersect(self, expr):
        raise NotImplementedError
    
    @abstractmethod
    def visit_p_complement(self, expr):
        raise NotImplementedError
    
    @abstractmethod
    def visit_p_image(self, expr):
        raise NotImplementedError
    
    @abstractmethod
    def visit_p_reverse_image(self, expr):
        raise NotImplementedError
    
class RelVisitor(ABC):
    @abstractmethod
    def visit_r_product(self, expr):
        raise NotImplementedError
    
    @abstractmethod
    def visit_r_identity(self, expr):
        raise NotImplementedError
    
    @abstractmethod
    def visit_r_union(self, expr):
        raise NotImplementedError
    
    @abstractmethod
    def visit_r_concat(self, expr):
        raise NotImplementedError
    
    @abstractmethod
    def visit_r_star(self, expr):
        raise NotImplementedError
    
    @abstractmethod
    def visit_r_compose(self, expr):
        raise NotImplementedError
    
    @abstractmethod
    def visit_r_priority_union(self, expr):
        raise NotImplementedError
    
    @abstractmethod
    def visit_r_empty_set(self, expr):
        raise NotImplementedError
    
    @abstractmethod
    def visit_r_epsilon(self, expr):
        raise NotImplementedError

class SpecVisitor(ABC):
    @abstractmethod
    def visit_s_equal(self, expr):
        raise NotImplementedError
    
    @abstractmethod
    def visit_s_subset_eq(self, expr):
        raise NotImplementedError
    
    @abstractmethod
    def visit_s_or(self, expr):
        raise NotImplementedError
    
    @abstractmethod
    def visit_s_and(self, expr):
        raise NotImplementedError
    
    @abstractmethod
    def visit_s_not(self, expr):
        raise NotImplementedError
    
    @abstractmethod
    def visit_s_ite(self, expr):
        raise NotImplementedError

    

   
    
    