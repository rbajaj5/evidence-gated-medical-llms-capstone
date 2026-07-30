from branch_factor_path_stability import CASES, choose_sectorial_directions, path_metrics, run, separation_scale


def test_separated_branch_preserves_half_planes_and_phase_gap():
    summary = run()
    assert summary["stable_branch_passes"] is True
    assert summary["stable_min_separation_ratio"] > 0
    assert summary["stable_min_scaled_phase_margin"] > 0
    stable = next(row for row in summary["rows"] if row["name"] == "separated_multimodal_branch")
    assert stable["half_plane_preserved"] is True
    assert stable["phase_gap_positive"] is True


def test_near_collision_branch_is_blocked():
    summary = run()
    assert summary["near_collision_branch_passes"] is False
    assert summary["near_collision_separation_passes"] is False
    assert summary["permission"] == "BRANCH_STABILITY_AUDIT_ONLY"
    assert summary["hard_outcome_permission_count"] == 0


def test_volterra_contraction_separates_safe_and_unsafe_cases():
    summary = run()
    stable = next(row for row in summary["rows"] if row["name"] == "separated_multimodal_branch")
    near = next(row for row in summary["rows"] if row["name"] == "near_collision_family_population_branch")
    assert stable["volterra_contractive"] is True
    assert stable["volterra_contraction_ratio"] < 1
    assert near["separation_passes"] is False


def test_sectorial_direction_construction_returns_one_direction_per_branch():
    case = CASES[0]
    omegas = choose_sectorial_directions(case)
    assert len(omegas) == len(case.z)
    assert all(abs(omega) >= 1 for omega in omegas)
    metrics = path_metrics(case)
    assert metrics["r0"] == separation_scale(case.z)
    assert metrics["admissible_sector"] is True


def test_bbgky_collision_warning_is_present():
    summary = run()
    warning = summary["bbgky_collision_interpretation"]
    assert "collision" in warning
    assert "Family-linked genomic overlap" in warning
