from picture_language_diagram_audit import DIAGRAMS, permission_counts, run


def test_diagram_audit_has_expected_source_coverage():
    summary = run()
    assert summary["diagram_count"] == 9
    assert any("Jaffe-Liu" in source for source in summary["source_families"])
    assert any("Axelrod" in source for source in summary["source_families"])
    assert any("Bourgade-Huang" in source for source in summary["source_families"])


def test_no_diagram_authorizes_hard_outcome_claim():
    summary = run()
    assert summary["hard_outcome_permission_count"] == 0
    assert summary["all_diagrams_audit_or_stress_only"] is True
    assert not any(item.permission == "ALLOW_CAUTIOUS_CLINICIAN_SUMMARY" for item in DIAGRAMS)


def test_simulation_clock_resets_validation():
    summary = run()
    assert summary["simulation_clock_resets_validation"] is True
    clock = next(item for item in DIAGRAMS if item.diagram_id == "simulation_clock")
    assert "resets" in clock.medical_runtime_lesson


def test_virtual_and_noise_warnings_are_explicit():
    summary = run()
    assert summary["feynman_virtual_state_warning"] is True
    assert summary["prisoners_dilemma_noise_note"] is True


def test_loop_equation_row_is_universality_audit_only():
    loop = next(item for item in DIAGRAMS if item.diagram_id == "loop_equation_hierarchy")
    assert loop.permission == "UNIVERSALITY_AUDIT_ONLY"
    assert loop.transfer_resets_validation is True
    assert "hierarchy" in loop.required_gate
    assert permission_counts()["UNIVERSALITY_AUDIT_ONLY"] == 1
