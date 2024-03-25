from abc import ABC, abstractmethod

"""
@author: Xieyang Xu
@date: 2024.01.30
@description: This file implements the visitor class for expressions.
"""

class RegexVisitor(ABC):
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
    
class FESpecVisitor(ABC):
    @abstractmethod
    def visit_atomic_spec(self, expr):
        raise NotImplementedError
    
    @abstractmethod
    def visit_concat_spec(self, expr):
        raise NotImplementedError
    
    @abstractmethod
    def visit_else_spec(self, expr):
        raise NotImplementedError