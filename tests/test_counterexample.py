from rela.networkmodel.relagraphformat import RelaGraphNC
from rela.verification.specverifier import SpecVerifier
from rela.counterexample.counterexample import CounterExampleGenerator
from rela.language.regularir import *

def test_generate_counterexample_graph_format_device_level():
    state = RelaGraphNC.from_json('tests/data/example_rela_graph_network_state.json', precision='device')
    verifier = SpecVerifier(state)

    spec1 = preState >> I(PStar(pDot)) == postState

    two_devices = P('BORDER-1.DC1|vrf') | P('BORDER-2.DC1|vrf')
    three_devices = P('BORDER-1.DC1|vrf') | P('BORDER-2.DC1|vrf') | P('NEW-DEVICE-1|vrf')
    change = I(PStar(pDot)) + (two_devices * three_devices) + I(PStar(pDot))
    unchange = I(PStar(PNegSymbols('BORDER-1.DC1|vrf', 'BORDER-2.DC1|vrf')))
    spec2 = preState >> (change | unchange) == postState

    spec = spec1 | spec2
    verification_result = spec.accept(verifier)

    failed_cases = {i : state.slices[i] for i in verification_result.failed_cases}
    generator = CounterExampleGenerator(failed_cases)

    res = spec.accept(generator)
    assert res.n_cases == 1

    case_0 = res.counter_examples[0]
    case_1 = res.counter_examples[1]
    spec1_str = 'preState ▶ I(.*) = postState'
    spec2_str = str(spec2)
    assert set([case_0.spec, case_1.spec]) == set([spec1_str, spec2_str])

    if case_0.spec == spec2_str:
        case_0, case_1 = case_1, case_0
    assert case_0.fec_id == 0
    assert case_0.spec == 'preState ▶ I(.*) = postState'
    assert len(case_0.before_paths) == 2
    assert len(case_0.after_paths) == 3
    assert len(case_0.left_paths) == 2
    assert len(case_0.right_paths) == 3
    assert set(case_0.before_paths) == set((('SPINE-3.DC3|vrf', 'BORDER-1.DC1|vrf', 'drop'), ('SPINE-3.DC3|vrf', 'BORDER-2.DC1|vrf', 'drop')))
    assert set(case_0.after_paths) == set((('SPINE-3.DC3|vrf', 'NEW-DEVICE|vrf', 'drop'), ('SPINE-3.DC3|vrf', 'BORDER-1.DC1|vrf', 'drop'), ('SPINE-3.DC3|vrf', 'BORDER-2.DC1|vrf', 'drop')))
    assert set(case_0.left_paths) == set((('SPINE-3.DC3|vrf', 'BORDER-1.DC1|vrf', 'drop'), ('SPINE-3.DC3|vrf', 'BORDER-2.DC1|vrf', 'drop')))
    assert set(case_0.right_paths) == set((('SPINE-3.DC3|vrf', 'NEW-DEVICE|vrf', 'drop'), ('SPINE-3.DC3|vrf', 'BORDER-1.DC1|vrf', 'drop'), ('SPINE-3.DC3|vrf', 'BORDER-2.DC1|vrf', 'drop')))
    

    case_1 = res.counter_examples[1]
    assert case_1.fec_id == 0
    assert case_1.spec == spec2_str
    assert len(case_1.before_paths) == 2
    assert len(case_1.after_paths) == 3
    assert len(case_1.left_paths) == 3
    assert len(case_1.right_paths) == 3
    assert set(case_1.before_paths) == set((('SPINE-3.DC3|vrf', 'BORDER-1.DC1|vrf', 'drop'), ('SPINE-3.DC3|vrf', 'BORDER-2.DC1|vrf', 'drop')))
    assert set(case_1.after_paths) == set((('SPINE-3.DC3|vrf', 'NEW-DEVICE|vrf', 'drop'), ('SPINE-3.DC3|vrf', 'BORDER-1.DC1|vrf', 'drop'), ('SPINE-3.DC3|vrf', 'BORDER-2.DC1|vrf', 'drop')))
    assert set(case_1.left_paths) == set((('SPINE-3.DC3|vrf', 'NEW-DEVICE-1|vrf', 'drop'), ('SPINE-3.DC3|vrf', 'BORDER-1.DC1|vrf', 'drop'), ('SPINE-3.DC3|vrf', 'BORDER-2.DC1|vrf', 'drop')))
    assert set(case_1.right_paths) == set((('SPINE-3.DC3|vrf', 'NEW-DEVICE|vrf', 'drop'), ('SPINE-3.DC3|vrf', 'BORDER-1.DC1|vrf', 'drop'), ('SPINE-3.DC3|vrf', 'BORDER-2.DC1|vrf', 'drop')))

