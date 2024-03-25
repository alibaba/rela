from typing import List
import json
import dataclasses

from .networkmodel.relagraphformat.graphnc import RelaGraphNC
from .verification.specverifier import SpecVerifier
from .verification.verificationresult import VerificationResult
from .counterexample.counterexample import CounterExampleGenerationResult, CounterExampleGenerator
from .language.regularir import Spec

def verify_network_change(spec: Spec, file: str, format: str = 'graph', precision: str = 'device', alg: str = 'default', mapping_file: str = None, selected_indices: list=None) -> VerificationResult:
    if format == 'graph':
        state = RelaGraphNC.from_json(file, precision, mapping_file)
    else:
        raise ValueError(f"Input format {format} not implemented")

    if alg == 'default':
        verifier = SpecVerifier(state, selected_indices)
    else:
        raise ValueError(f"Verification alg {alg} not implemented")

    return spec.accept(verifier)


def generate_counterexamples(spec: Spec, file: str, format: str = 'graph', precision: str = 'device', indices: List[int] = [], out_file: str = None, mapping_file: str = None) -> CounterExampleGenerationResult:
    """
    Generate counter examples for failed cases in a single file.
    """
    if format == 'graph':
        state = RelaGraphNC.from_json(file, precision, mapping_file)

    failed_cases = {(file, i) : state.slices[i] for i in indices}
    generator = CounterExampleGenerator(failed_cases)

    result = spec.accept(generator)

    if out_file is not None:
        with open(out_file, 'w') as f:
            json.dump([dataclasses.asdict(c) for c in result.counter_examples], f, indent=2)

    return result
