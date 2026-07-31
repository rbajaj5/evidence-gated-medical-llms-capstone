from coordination_benchmark_audit import audit_case, run


def row_by_id(summary, case_id):
    return next(row for row in summary["rows"] if row["case_id"] == case_id)


def test_high_state_coverage_alone_is_not_coordination_evidence():
    summary = run()
    row = row_by_id(summary, "C01")
    assert row["state_coverage"] > 0.95
    assert row["structural_coordination_score"] == 0
    assert row["action"] == "DO_NOT_TREAT_AS_COORDINATION_BENCHMARK"


def test_protocol_formation_requires_runtime_protocol_assurance():
    summary = run()
    row = row_by_id(summary, "C03")
    assert row["state_coverage"] > 0.95
    assert row["test_time_protocol"] is True
    assert row["action"] == "REQUIRE_PROTOCOL_ASSURANCE"


def test_implicit_clinician_action_demo_is_a_structural_coordination_case():
    summary = run()
    row = row_by_id(summary, "C04")
    assert row["implicit_action_demo"] is True
    assert row["structural_coordination_score"] > row_by_id(summary, "C02")["structural_coordination_score"]
    assert row["action"] == "REQUIRE_PROTOCOL_ASSURANCE"


def test_low_coverage_without_asymmetry_routes_to_state_coverage_stress_test():
    summary = run()
    row = row_by_id(summary, "C05")
    assert row["state_coverage"] < 0.9
    assert row["structural_coordination_score"] == 0
    assert row["action"] == "STRESS_TEST_STATE_COVERAGE"


def test_audit_summary_preserves_source_and_case_count():
    summary = run()
    assert summary["source"] == "https://arxiv.org/abs/2503.17821"
    assert summary["case_count"] == 5
    assert summary["action_counts"]["REQUIRE_PROTOCOL_ASSURANCE"] == 3
