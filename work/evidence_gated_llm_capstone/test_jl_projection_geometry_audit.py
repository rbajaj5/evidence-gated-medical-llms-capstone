from jl_projection_geometry_audit import run


def row_by_id(summary, case_id):
    return next(row for row in summary["rows"] if row["case_id"] == case_id)


def test_gaussian_projection_allows_geometry_claim_only():
    summary = run()
    row = row_by_id(summary, "J01")
    assert row["geometry_preserved"] is True
    assert row["action"] == "ALLOW_GEOMETRY_PRESERVATION_CLAIM"


def test_rademacher_projection_allows_geometry_claim_only():
    summary = run()
    row = row_by_id(summary, "J02")
    assert row["geometry_preserved"] is True
    assert row["action"] == "ALLOW_GEOMETRY_PRESERVATION_CLAIM"


def test_sparse_projection_requires_explicit_scaling_but_can_pass():
    summary = run()
    row = row_by_id(summary, "J03")
    assert row["model"] == "sparse_sign"
    assert row["geometry_preserved"] is True


def test_unscaled_projection_blocks_geometry_claim():
    summary = run()
    row = row_by_id(summary, "J04")
    assert row["geometry_preserved"] is False
    assert row["action"] == "BLOCK_GEOMETRY_CLAIM"


def test_excessive_privacy_noise_blocks_geometry_before_privacy_claim():
    summary = run()
    row = row_by_id(summary, "J05")
    assert row["privacy_noise"] > 0
    assert row["action"] == "BLOCK_GEOMETRY_CLAIM"


def test_source_shift_requires_population_audit_even_when_geometry_preserved():
    summary = run()
    row = row_by_id(summary, "J06")
    assert row["geometry_preserved"] is True
    assert row["source_shift"] is True
    assert row["action"] == "REQUIRE_SOURCE_POPULATION_AUDIT"


def test_clinical_claim_abstains_even_when_geometry_preserved():
    summary = run()
    row = row_by_id(summary, "J07")
    assert row["geometry_preserved"] is True
    assert row["clinical_claim_requested"] is True
    assert row["action"] == "ABSTAIN_CLINICAL_CLAIM"


def test_summary_preserves_jl_source_and_case_count():
    summary = run()
    assert summary["source"] == "https://arxiv.org/abs/2402.10232"
    assert summary["case_count"] == 7
