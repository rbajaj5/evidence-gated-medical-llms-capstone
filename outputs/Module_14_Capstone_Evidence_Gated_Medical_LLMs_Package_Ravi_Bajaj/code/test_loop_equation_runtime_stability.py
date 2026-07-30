from loop_equation_runtime_stability import (
    REQUIRED_GATES,
    discrete_gronwall_trace,
    run,
    single_entry_resolvent_bound,
    switching_cumulant_budget_check,
)


def test_gronwall_probe_separates_stable_and_unstable_chains():
    summary = run()
    assert summary["chain_count"] == 2
    assert summary["stable_chain_passes"] is True
    assert summary["unstable_chain_passes"] is False
    assert summary["stable_final_error"] <= summary["stable_budget"]
    assert summary["unstable_final_error"] > summary["unstable_budget"]


def test_single_entry_resolvent_bound_is_inside_budget():
    bound = single_entry_resolvent_bound()
    assert bound["gamma_below_one_twelfth"] is True
    assert bound["single_entry_stable"] is True
    assert bound["single_entry_bound"] < bound["single_entry_budget"]


def test_required_loop_equation_gate_hierarchy_is_present():
    summary = run()
    assert summary["required_gate_count"] == len(REQUIRED_GATES)
    assert "local_law_or_calibration" in summary["required_gates"]
    assert "integration_by_parts_or_switching_identity" in summary["required_gates"]
    assert "gronwall_growth_budget" in summary["required_gates"]
    assert summary["permission"] == "UNIVERSALITY_AUDIT_ONLY"


def test_error_trace_is_monotone_for_unstable_case():
    summary = run()
    unstable = next(row for row in summary["rows"] if row["name"] == "unstable_missing_provenance_transfer")
    trace = unstable["trace"]
    assert trace == sorted(trace)


def test_switching_cumulant_budget_controls_main_cancellation_and_bad_event():
    check = switching_cumulant_budget_check()
    assert check["main_cancellation_passes"] is True
    assert check["main_cancellation"]["net"] == 0.0
    assert check["bad_event_negligible"] is True
    assert check["replacement_error_inside_budget"] is True


def test_switching_cumulant_budget_keeps_derivative_exponent_decaying():
    check = switching_cumulant_budget_check()
    assert check["gamma_below_one_twelfth"] is True
    assert check["derivative_error_decays"] is True
    assert check["requires_que_or_spatial_profile_gate"] is True
