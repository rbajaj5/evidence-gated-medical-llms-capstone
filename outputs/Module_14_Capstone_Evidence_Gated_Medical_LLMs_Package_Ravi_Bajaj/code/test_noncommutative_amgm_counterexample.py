from noncommutative_amgm_counterexample import run


def test_exact_rank_one_counterexample_violates_bound():
    summary = run()
    assert summary["dimension"] == 2
    assert summary["rank_one_projectors"] is True
    assert summary["dimension_one_scalar_case_satisfies_bound"] is True
    assert summary["original_rhs"] == "1/4"
    assert summary["original_lhs_exact"] == "(1 + sqrt(2)) / 4"
    assert summary["violation_factor_exact"] == "1 + sqrt(2)"
    assert summary["violation_factor_float"] > 2.4


def test_positive_definite_perturbation_still_violates_bound():
    summary = run()
    assert summary["positive_definite_epsilon"] == "1/10"
    assert summary["positive_definite_rhs"] == "324/625"
    assert summary["positive_definite_lhs_exact"] == "126/625 + 3*sqrt(2)/10"
    assert summary["positive_definite_margin_float"] > 0
