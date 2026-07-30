from mahalanobis_covariate_experiment import run


def test_mahalanobis_covariate_audit_flags_distant_sources():
    summary = run()
    assert summary["source_count"] == 4
    assert summary["feature_count"] == 6
    assert summary["flagged_sources"]
    assert "genomeindia_like" in summary["flagged_sources"]
    assert summary["max_distance_source"] in summary["flagged_sources"]


def test_near_reference_source_does_not_require_source_specific_validation():
    summary = run()
    us_row = summary["source_rows"]["us_ehr_like"]
    assert us_row["mahalanobis_distance"] < summary["action_threshold"]
    assert us_row["requires_source_specific_validation"] is False
