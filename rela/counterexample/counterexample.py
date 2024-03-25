from __future__ import annotations
from dataclasses import dataclass
from typing import Any, List, Dict, Set, Tuple
import multiprocessing
import logging

from ..language.regularir.rirvisitor import SpecVisitor
from ..language.regularir.alphabet_scanner import AlphabetScanner
from ..language.regularir import SEqual, SSubsetEq, Spec, SNot, SAnd, SOr, preState, postState, P, PStar, pDot, PIntersect
from ..automata import FSTConstructor, FSA
from ..automata.utils import fst_minus, fst_intersect, fst_extract_paths
from ..networkmodel.fec import FEC


"""
@author: Xieyang Xu
@date: 2023.07.25
@description: This file implements the visitor pattern for generating
counterexamples for Rela RIR spec.
"""

@dataclass
class CounterExample:
    fec_id: Any
    spec: str
    before_paths: Tuple[Tuple[str, ...], ...]
    after_paths: Tuple[Tuple[str, ...], ...]
    left_paths: Tuple[Tuple[str, ...], ...]
    right_paths: Tuple[Tuple[str, ...], ...]

    def __repr__(self) -> str:
        res = []
        # res.append(f"Before paths:")
        # for path in self.before_paths:
        #     res.append(f"  {path}" )
        # res.append(f"After paths:")
        # for path in self.after_paths:
        #     res.append(f"  {path}" )
        res.append(f"Reason of violation (left side ≠ right side):")
        res.append(f"  left side = ")
        for path in self.left_paths:
            res.append(f"    {path}" )
        res.append(f"  right side =")
        for path in self.right_paths:
            res.append(f"    {path}" )
        return '\n'.join(res)

@dataclass()
class CounterExampleGenerationResult:
    n_cases: int
    error_cases: List[Any]
    counter_examples: List[CounterExample]

    def __add__(self, other: CounterExampleGenerationResult):
        """
        Merge two CounterExampleGenerationResult.
        """
        if not isinstance(other, CounterExampleGenerationResult):
            return NotImplemented
        if self.n_cases != other.n_cases:
            raise ValueError('Cannot merge CounterExampleGenerationResult with different n_cases')
        return CounterExampleGenerationResult(
            n_cases=self.n_cases,
            error_cases=list(set(self.error_cases + other.error_cases)), # remove duplicates
            counter_examples=self.counter_examples + other.counter_examples
        )
    
    def __repr__(self) -> str:
        res = ['CounterExampleGenerationResult:']
        n = len(self.counter_examples)
        lim = min(10, n)
        for i, counterexample in enumerate(self.counter_examples[:lim]):
            res.append(f"Case {i+1} " + str(counterexample))
        if lim < n:
            res.append(f'...omitting additional {n - 10} cases')
        return '\n'.join(res)




@dataclass
class CounterExampleGenerator(SpecVisitor):
    failed_cases: Dict[Any, FEC]


    def _generate_counter_examples(self, expr: Spec) -> CounterExampleGenerationResult:
        res = CounterExampleGenerationResult(
            n_cases=len(self.failed_cases),
            error_cases=[],
            counter_examples=[]
        )
        for fec_id, fec in self.failed_cases.items():
            try:
                counter_examples = self._generate_counter_example_single_fec(expr, fec, fec_id)
            except Exception as e:
                if multiprocessing.current_process()._identity: # if not main process
                    res.error_cases.append(fec_id)
                else:
                    # if main process, print error message for debugging
                    res.error_cases.append(fec_id)
                    logger = logging.getLogger(__name__)
                    logger.error(f'Exception raised when generating counterexample for FEC {fec_id}:')
                    logger.error("Exception:", type(e).__name__)
                    logger.error("Arguments:", e.args)
                    logger.error("Traceback:", e.__traceback__)
                    import traceback
                    traceback.print_tb(e.__traceback__)
                continue
            res.counter_examples.extend(counter_examples)
        return res
    
    @staticmethod
    def _compute_start_locations(paths: List[List[str]]) -> Set[str]:
        """
        Compute the start locations of a list of paths.
        """
        alphabet = set()
        for path in paths:
            alphabet.add(path[0])
        return alphabet
    
    @staticmethod
    def _group_paths_by_first_symbol(paths: List[List[str]]) -> Dict[str, List[List[str]]]:
        """
        Group paths by their first symbol.
        """
        res = {}
        for path in paths:
            if path[0] not in res:
                res[path[0]] = []
            res[path[0]].append(path)
        return res
    
    @staticmethod
    def _to_hashable(paths: List[List[str]]) -> Tuple[Tuple[str, ...], ...]:
        """
        Convert a list of paths to be hashable, i.e., a tuple of tuple of strings.
        """
        return tuple(tuple(path) for path in paths)
    
    @staticmethod
    def _generate_counter_example_single_fec(expr: Spec, fec: FEC, fec_id: Any) -> List[CounterExample]:
        """
        Generate counter examples for a single FEC.
        """
        # 1. compute flows (start locations) that violates the spec
        alphabet = fec.compute_alphabet()
        alphabet.update(expr.accept(AlphabetScanner()))
        constructor = FSTConstructor(alphabet, fec)
        left_fsa = expr.p.accept(constructor)
        right_fsa = expr.q.accept(constructor)
        
        extra_fsa = fst_minus(left_fsa, right_fsa)
        extra_paths = fst_extract_paths(extra_fsa)

        if isinstance(expr, SEqual):
            missing_fsa = fst_minus(right_fsa, left_fsa)
            missing_paths = fst_extract_paths(missing_fsa)
        else:
            missing_paths = []

        #matched_fsa = fst_intersect(left_fsa, right_fsa)
        #matched_paths = fst_extract_paths(matched_fsa)
        diff_start_locations = CounterExampleGenerator._compute_start_locations(extra_paths + missing_paths)

        # 2. for violated flows, display paths in X, Y, left side, right side
        res = []
        before_fsa = preState.accept(constructor)
        after_fsa = postState.accept(constructor)

        for symbol in diff_start_locations:
            # extract paths with this start location in 4 automata: X, Y, left, right
            flow_filter = P(symbol) + PStar(pDot)
            filter_fsa = flow_filter.accept(constructor)
            before_paths = fst_extract_paths(fst_intersect(before_fsa, filter_fsa))
            after_paths = fst_extract_paths(fst_intersect(after_fsa, filter_fsa))
            left_paths = fst_extract_paths(fst_intersect(left_fsa, filter_fsa))
            right_paths = fst_extract_paths(fst_intersect(right_fsa, filter_fsa))
            res.append(CounterExample(
                fec_id=fec_id,
                spec=str(expr),
                before_paths=CounterExampleGenerator._to_hashable(before_paths),
                after_paths=CounterExampleGenerator._to_hashable(after_paths),
                left_paths=CounterExampleGenerator._to_hashable(left_paths),
                right_paths=CounterExampleGenerator._to_hashable(right_paths)
            ))

        return res


    def visit_s_equal(self, expr: SEqual) -> CounterExampleGenerationResult:
        return self._generate_counter_examples(expr)
    
    def visit_s_subset_eq(self, expr: SSubsetEq) -> CounterExampleGenerationResult:
        return self._generate_counter_examples(expr)
    
    def visit_s_not(self, expr: SNot) -> CounterExampleGenerationResult:
        return self._generate_counter_examples(expr.p)
    
    def visit_s_and(self, expr: SAnd) -> CounterExampleGenerationResult:
        return expr.p.accept(self) + expr.q.accept(self)
    
    def visit_s_or(self, expr: SOr) -> CounterExampleGenerationResult:
        p_res = expr.p.accept(self)
        q_res = expr.q.accept(self)
        # compute unique fec_ids in p_res.counter_examples and q_res.counter_examples
        p_fec_ids = set([c.fec_id for c in p_res.counter_examples])
        q_fec_ids = set([c.fec_id for c in q_res.counter_examples])
        # counterexample is meaningful only if it appears in both p_res and q_res
        meaningful_fec_ids = p_fec_ids & q_fec_ids
        # filter out counterexamples that are not meaningful
        p_res.counter_examples = [c for c in p_res.counter_examples if c.fec_id in meaningful_fec_ids]
        q_res.counter_examples = [c for c in q_res.counter_examples if c.fec_id in meaningful_fec_ids]
        return p_res + q_res
    
    def visit_s_ite(self, expr: SAnd) -> CounterExampleGenerationResult:
        return expr.p.accept(self) + expr.q.accept(self)
    