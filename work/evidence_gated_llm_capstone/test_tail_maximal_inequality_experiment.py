from tail_maximal_inequality_experiment import run


def test_exact_crossing_probability_obeys_kolmogorov_bound():
    summary = run()
    assert summary["steps"] == 12
    assert summary["path_count"] == 4096
    assert summary["total_variance"] == 12
    assert summary["threshold"] == 6
    assert summary["kolmogorov_bound"] == "1/3"
    assert summary["bound_holds"] is True
    assert summary["exact_crossing_probability_float"] <= summary["kolmogorov_bound_float"]


def test_pathwise_crossing_can_be_missed_by_terminal_check():
    summary = run()
    assert summary["crossing_exceeds_terminal_check"] is True
    assert summary["exact_crossing_probability_float"] > summary["terminal_exceed_probability_float"]
    assert summary["returned_inside_after_crossing_probability_float"] > 0
