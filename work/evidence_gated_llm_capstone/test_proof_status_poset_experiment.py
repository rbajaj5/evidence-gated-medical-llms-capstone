from proof_status_poset_experiment import artifact_cases, permission, run, upgrade_only_source_or_validation


def artifact_by_name(prefix: str):
    return next(case for case in artifact_cases() if case.name.startswith(prefix))


def test_proof_status_poset_domain_size_and_invariants():
    summary = run()
    assert summary["states_enumerated"] == 4096
    assert summary["cover_transitions_enumerated"] == 18432
    assert summary["nonclinical_hard_state_count"] == 0
    assert summary["endpoint_free_promotion_count"] == 0
    assert summary["method_only_hard_state_count"] == 0


def test_niettu_remains_audit_only_under_source_and_proof_upgrades():
    niettu = artifact_by_name("NIETTU")
    permissions = {permission(state) for state in upgrade_only_source_or_validation(niettu.state)}
    assert permissions == {"proof_status_or_provenance_audit_only"}


def test_representative_artifacts_have_expected_permission_levels():
    summary = run()
    rows = {row["name"]: row for row in summary["artifact_rows"]}
    assert rows["NIETTU topological theory record"]["permission"] == "proof_status_or_provenance_audit_only"
    assert rows["Karlin-Peres Hex/Y theorem"]["permission"] == "proof_status_or_provenance_audit_only"
    assert rows["Byrne-style pragmatic patient-outcome RCT"]["permission"] == "hard_outcome_allowed_with_caveats"
    assert rows["Hospital genetics guideline support"]["permission"] == "validated_surrogate_or_guideline_support_only"
    assert rows["Synthetic audio/captioning benchmark"]["permission"] == "surrogate_or_method_claim_only"
    assert rows["KAN architecture critical assessment"]["permission"] == "surrogate_or_method_claim_only"
    assert rows["Jaffe-Liu picture language program"]["permission"] == "proof_status_or_provenance_audit_only"
