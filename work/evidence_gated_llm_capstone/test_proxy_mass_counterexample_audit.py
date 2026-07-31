from proxy_mass_counterexample_audit import run


def row_by_id(summary, case_id):
    return next(row for row in summary["rows"] if row["case_id"] == case_id)


def test_vanishing_proxy_does_not_imply_zero_residual_risk():
    summary = run()
    row = row_by_id(summary, "Z01")
    assert row["local_proxy"] == 0.0
    assert row["residual_mass"] == 1.0
    assert row["counterexample_shape"] is True
    assert row["action"] == "BLOCK_ZERO_PROXY_TO_ZERO_RISK"


def test_positive_proxy_routes_to_warning_not_reassurance():
    summary = run()
    row = row_by_id(summary, "Z02")
    assert row["local_proxy"] > 0
    assert row["action"] == "ALLOW_POSITIVE_PROXY_WARNING"


def test_added_structure_can_bound_reassurance():
    summary = run()
    row = row_by_id(summary, "Z03")
    assert row["added_structure"] is True
    assert row["residual_mass"] == 0.0
    assert row["action"] == "ALLOW_REASSURANCE_WITH_STRUCTURE"


def test_low_proxy_with_material_mass_requires_residual_audit():
    summary = run()
    row = row_by_id(summary, "Z04")
    assert row["local_proxy"] < 0.05
    assert row["residual_mass"] > 0.10
    assert row["action"] == "REQUIRE_RESIDUAL_MASS_AUDIT"


def test_low_risk_language_depends_on_audit_and_structure():
    summary = run()
    row = row_by_id(summary, "Z05")
    assert row["residual_mass"] <= 0.05
    assert row["added_structure"] is True
    assert row["action"] == "ALLOW_REASSURANCE_WITH_STRUCTURE"


def test_summary_preserves_zero_mass_counterexample_source():
    summary = run()
    assert summary["source"] == "https://arxiv.org/abs/2607.26549"
    assert summary["case_count"] == 5
