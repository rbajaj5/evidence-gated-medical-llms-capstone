from kelly_runtime_budget_experiment import kelly_fraction, log_growth, run


def test_kelly_fraction_is_zero_for_unfavorable_signal():
    assert kelly_fraction(0.49) == 0.0
    assert kelly_fraction(0.50) == 0.0


def test_two_thirds_signal_gets_one_third_fraction():
    assert abs(kelly_fraction(2 / 3) - (1 / 3)) < 1e-12


def test_kelly_fraction_maximizes_local_log_growth_for_two_thirds():
    optimal = log_growth(2 / 3, kelly_fraction(2 / 3))
    smaller = log_growth(2 / 3, 0.20)
    larger = log_growth(2 / 3, 0.60)
    assert optimal > smaller
    assert optimal > larger


def test_capped_policy_limits_high_confidence_claim_exposure():
    summary = run()
    assert summary["zero_exposure_for_unfavorable_or_uncertain_signal"] is True
    assert summary["capped_policy_limits_high_confidence_signal"] is True
    assert summary["all_in_ruin_probability"] > 0.99
