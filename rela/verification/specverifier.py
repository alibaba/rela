from __future__ import annotations
from dataclasses import dataclass
import time
from typing import List, Tuple
import logging
from tqdm import tqdm
import multiprocessing

from ..automata.utils import fst_eq, fst_subseteq
from ..automata import FSTConstructor, FSA
from ..networkmodel.networkchange import NetworkChange, NetworkPath
from ..networkmodel.fec import FEC
from ..language.regularir.rirvisitor import SpecVisitor
from ..language.regularir import SEqual, SSubsetEq, Spec, SPrefixITE
from .verificationresult import VerificationResult


"""
@author: Xieyang Xu
@date: 2023.07.15
@description: This file implements the visitor pattern for checking
compliance for Rela RIR spec.
"""

@dataclass
class SpecVerifier(SpecVisitor):
    network_change: NetworkChange
    selected_indices: List[int] = None

    @staticmethod
    def _extract_alphabet(fec: FEC) -> set:
        """
        Extract the alphabet of given paths.
        """
        return fec.compute_alphabet()
    
    @staticmethod
    def verify(spec: Spec, network_change: NetworkChange) -> VerificationResult:
        """
        Verify the given spec on the given network change.
        """
        verifier = SpecVerifier(network_change)
        return spec.accept(verifier)
    
    def _verify_atomic_spec(self, expr: Spec) -> VerificationResult:
        res = True

        logger = logging.getLogger(__name__)
        logger.info(f'Verifying atomic spec: {expr}')
        N = self.network_change.count_fec()
        if N == 0:
            logger.warn(f'No FEC found, verification skipped')
            return True
        
        res = VerificationResult(
            data=self.network_change.get_name(),
            spec=str(expr),
            n_total=N,
            n_passed=0,
            n_failed=0,
            n_skipped=0,
            passed_cases=[],
            failed_cases=[],
            skipped_cases=[]
        )
        
        start = time.perf_counter()
        pid = multiprocessing.current_process()._identity[0] if multiprocessing.current_process()._identity else 0
        for i, fec in enumerate(tqdm(self.network_change.iterate(), total=N, position=pid, disable=(pid > 10), desc=self.network_change.get_name(), leave=False)):
            if self.selected_indices is not None and i not in self.selected_indices:
                res.n_skipped += 1
                res.skipped_cases.append(i)
                continue
            try:
                slice_res = SpecVerifier._verify_atomic_spec_single_fec(expr, fec)
            except Exception as e:
                #logger.warn(f'Exception raised when verifying FEC #{i}: {e}')
                #import traceback
                #traceback.print_exc()
                res.n_skipped += 1
                res.skipped_cases.append(i)
                continue
            res.n_failed += 1 if not slice_res else 0
            res.n_passed += 1 if slice_res else 0
            if slice_res:
                res.passed_cases.append(i)
            if not slice_res:
                res.failed_cases.append(i)
        end = time.perf_counter()

        logger.info(f'Verification completed, flow equivalent classes: {N}, time per FEC: {(end - start) / N:.6f}')
        return res
    
    @staticmethod
    def _construct_fsas(expr: Spec, alphabet: set, fec: FEC) -> Tuple[FSA, FSA]:
        """
        Construct the FSA for the left and right side of the spec.
        """
        constructor = FSTConstructor(alphabet, fec)
        left_fsa = expr.p.accept(constructor)
        right_fsa = expr.q.accept(constructor)
        return left_fsa, right_fsa

    @staticmethod
    def _verify_atomic_spec_single_fec(expr: Spec, fec: FEC) -> bool:
        """
        Verify an atomic spec on a single fec.
        """
        alphabet = SpecVerifier._extract_alphabet(fec)
        
        # selects a sub-spec by testing whether this FEC overlaps with the guard
        while isinstance(expr, SPrefixITE):
            ips = fec.get_ip_traffic_keys()
            then_branch = False
            for ip in ips:
                if expr.guard.contains(ip):
                    then_branch = True
                    break
            expr = expr.p if then_branch else expr.q
            

        # construct FSTs for the left and right side of the spec
        left_fsa, right_fsa = SpecVerifier._construct_fsas(expr, alphabet, fec)

        # check automata equivalence
        if isinstance(expr, SEqual):
            res = fst_eq(left_fsa, right_fsa)
        elif isinstance(expr, SSubsetEq):
            res = fst_subseteq(left_fsa, right_fsa)
        else:
            raise Exception('invalid set operator')
        
        return res


    def visit_s_equal(self, expr: Spec) -> VerificationResult:
        return self._verify_atomic_spec(expr)
    
    def visit_s_subset_eq(self, expr: Spec) -> VerificationResult:
        return self._verify_atomic_spec(expr)
    
    def visit_s_ite(self, expr):
        return self._verify_atomic_spec(expr)
    
    def visit_s_not(self, expr: Spec) -> VerificationResult:
        p_res = expr.p.accept(self)
        return VerificationResult(
            data=p_res.data,
            spec=str(expr),
            n_total=p_res.n_total,
            n_passed=p_res.n_failed,
            n_failed=p_res.n_passed,
            n_skipped=p_res.n_skipped,
            passed_cases=p_res.failed_cases,
            failed_cases=p_res.passed_cases,
            skipped_cases=p_res.skipped_cases
        )
    
    def visit_s_and(self, expr: Spec) -> VerificationResult:
        p_res = expr.p.accept(self)
        q_res = expr.q.accept(self)
        skipped_cases = set(p_res.skipped_cases) | set(q_res.skipped_cases)
        passed_cases = set(p_res.passed_cases) & set(q_res.passed_cases)
        passed_cases = passed_cases - skipped_cases
        failed_cases = set(p_res.failed_cases) | set(q_res.failed_cases)
        failed_cases = failed_cases - skipped_cases
        return VerificationResult(
            data=p_res.data,
            spec=str(expr),
            n_total=p_res.n_total,
            n_passed=len(passed_cases),
            n_failed=len(failed_cases),
            n_skipped=len(skipped_cases),
            passed_cases=list(passed_cases),
            failed_cases=list(failed_cases),
            skipped_cases=list(skipped_cases)
        )
    
    def visit_s_or(self, expr: Spec) -> VerificationResult:
        p_res = expr.p.accept(self)
        q_res = expr.q.accept(self)
        skipped_cases = set(p_res.skipped_cases) | set(q_res.skipped_cases)
        passed_cases = set(p_res.passed_cases) | set(q_res.passed_cases)
        passed_cases = passed_cases - skipped_cases
        failed_cases = set(p_res.failed_cases) & set(q_res.failed_cases)
        failed_cases = failed_cases - skipped_cases
        return VerificationResult(
            data=p_res.data,
            spec=str(expr),
            n_total=p_res.n_total,
            n_passed=len(passed_cases),
            n_failed=len(failed_cases),
            n_skipped=len(skipped_cases),
            passed_cases=list(passed_cases),
            failed_cases=list(failed_cases),
            skipped_cases=list(skipped_cases)
        )
    
    
