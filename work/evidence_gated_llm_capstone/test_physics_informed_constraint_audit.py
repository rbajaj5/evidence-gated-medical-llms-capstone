from physics_informed_constraint_audit import run


def row_by_id(summary, case_id):
    return next(row for row in summary["rows"] if row["case_id"] == case_id)


def test_high_fit_without_constraint_is_not_assurance():
    summary = run()
    row = row_by_id(summary, "P01")
    assert row["empirical_fit"] > 0.9
    assert row["linear_constraint"] is False
    assert row["action"] == "REQUIRE_STRUCTURAL_CONSTRAINT"


def test_large_residual_blocks_physics_informed_claim():
    summary = run()
    row = row_by_id(summary, "P02")
    assert row["linear_constraint"] is True
    assert row["residual_within_budget"] is False
    assert row["action"] == "BLOCK_HIGH_RESIDUAL"


def test_universal_kernel_linear_case_allows_bounded_consistency_claim():
    summary = run()
    row = row_by_id(summary, "P03")
    assert row["universal_kernel"] is True
    assert row["constraint_residual"] <= summary["constraint_residual_budget"]
    assert row["action"] == "ALLOW_CONSTRAINT_CONSISTENCY_CLAIM"


def test_misspecified_target_routes_to_stress_test_not_outcome_claim():
    summary = run()
    row = row_by_id(summary, "P04")
    assert row["misspecified_target"] is True
    assert row["action"] == "ALLOW_WITH_MISSPECIFICATION_STRESS_TEST"


def test_boundary_data_case_requires_boundary_audit():
    summary = run()
    row = row_by_id(summary, "P05")
    assert row["boundary_data_only"] is True
    assert row["action"] == "ALLOW_METHOD_CLAIM_WITH_BOUNDARY_AUDIT"


def test_nonlinear_unmodeled_case_abstains_on_scope():
    summary = run()
    row = row_by_id(summary, "P06")
    assert row["nonlinear_or_unmodeled_constraint"] is True
    assert row["action"] == "ABSTAIN_CONSTRAINT_SCOPE"


def test_summary_preserves_piks_source_and_case_count():
    summary = run()
    assert summary["source"] == "https://arxiv.org/abs/2607.27062"
    assert summary["case_count"] == 6
