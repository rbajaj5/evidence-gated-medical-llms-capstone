from event_algebra_experiment import run


def test_finite_event_algebra_identities_hold():
    summary = run()
    assert abs(summary["probability_mass_total"] - 1.0) < 1e-12
    assert summary["union_identity_error"] < 1e-12
    assert summary["complement_identity_error"] < 1e-12
    assert summary["monotonicity_holds"] is True


def test_runtime_events_are_nontrivial_and_trigger_safe_stop():
    summary = run()
    assert summary["sample_space_size"] > summary["unsafe_promotion_event_size"] > 0
    assert summary["audit_trigger_event_size"] > 0
    assert summary["safe_stop_event_size"] > 0
    assert summary["audit_trigger_probability"] > summary["safe_stop_probability"] > 0
