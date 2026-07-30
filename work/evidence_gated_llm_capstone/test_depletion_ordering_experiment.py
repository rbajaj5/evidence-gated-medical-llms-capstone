from depletion_ordering_experiment import (
    network_depletion_delta,
    residual_fraction_cost,
    run,
)


def test_small_first_minimizes_raw_residual_fraction_cost():
    summary = run()
    assert summary["permutation_count"] == 24
    assert summary["increasing_minimizes_raw_cost"] is True
    assert summary["decreasing_maximizes_raw_cost"] is True


def test_large_first_minimizes_convex_log_depletion_risk():
    summary = run()
    assert summary["decreasing_minimizes_convex_log_risk"] is True
    assert summary["increasing_maximizes_convex_log_risk"] is True


def test_multi_resource_context_reversal_is_observed():
    summary = run()
    assert summary["context_reversal_observed"] is True
    assert summary["low_tail_delta_cost_a_then_b_minus_b_then_a"] > 0
    assert summary["mixed_tail_delta_cost_a_then_b_minus_b_then_a"] < 0


def test_fixed_fifo_and_lifo_can_have_different_depletion_costs():
    loads = (1.0, 2.0, 5.0, 8.0)
    fifo = (0, 1, 2, 3)
    lifo = (3, 2, 1, 0)
    assert residual_fraction_cost(loads, fifo, reserve=3.0) < residual_fraction_cost(loads, lifo, reserve=3.0)


def test_network_delta_sign_convention_matches_preferred_order():
    a = (4.0, 1.0)
    b = (1.0, 3.0)
    assert network_depletion_delta(a, b, (1.0, 1.0), (1.0, 1.0)) > 0
    assert network_depletion_delta(a, b, (10.0, 1.0), (1.0, 1.0)) < 0
