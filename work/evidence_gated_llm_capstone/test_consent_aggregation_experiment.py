from consent_aggregation_experiment import run


def test_ranked_family_consent_cycle_triggers_boundary_preservation():
    summary = run()
    assert summary["condorcet_cycle_detected"] is True
    assert summary["safe_runtime_action"] == "PRESERVE_CONSENT_BOUNDARY"


def test_individual_caps_block_full_raw_release_but_allow_audit_only():
    summary = run()
    assert summary["full_raw_release_allowed"] is False
    assert summary["partial_inclusion_allowed"] is True
    assert summary["audit_only_allowed"] is True
    assert summary["full_raw_release_runtime_safe"] is False
    assert summary["partial_inclusion_runtime_safe"] is True
    assert summary["audit_only_runtime_safe"] is True


def test_boltzmann_allocation_respects_feasible_support():
    summary = run()
    for row in summary["boltzmann_beta_rows"]:
        assert set(row["allocation"]) == {"trait_specific_partial_inclusion", "audit_only_no_reuse"}
        if row["beta"] > 0:
            assert row["allocation"]["trait_specific_partial_inclusion"] > row["allocation"]["audit_only_no_reuse"]
    assert summary["entropy_decreases_with_beta"] is True


def test_differential_privacy_budget_composes_and_group_bound_is_recorded():
    summary = run()
    composed = summary["partial_plus_audit_composed_loss"]
    assert composed["epsilon"] == 0.8500000000000001
    assert composed["delta"] == 1e-07
    group_bound = summary["group_privacy_bound_for_partial_three_relatives"]
    assert group_bound["epsilon"] == 2.4000000000000004
    assert group_bound["delta_linear_upper_bound"] == 3e-07
