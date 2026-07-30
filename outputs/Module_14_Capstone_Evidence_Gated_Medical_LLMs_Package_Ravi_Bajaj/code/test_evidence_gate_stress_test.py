from run_evidence_gate_stress_test import SCENARIOS, decide, run


def by_id(scenario_id):
    return next(s for s in SCENARIOS if s.scenario_id == scenario_id)


def test_all_scenarios_match_expected_actions():
    summary = run()
    assert summary["scenario_count"] == 30
    assert summary["all_matched_expected"] is True
    assert summary["matched_expected_count"] == 30


def test_surrogate_evidence_cannot_become_hard_outcome_claim():
    decision = decide(by_id("S02"))
    assert decision.action == "NARROW_TO_SURROGATE"
    assert decision.permission_level == "surrogate_or_process_claim_only"
    assert "endpoint_strength" in decision.blocked_by


def test_only_hard_outcome_pragmatic_rct_gets_hard_outcome_permission():
    allowed = decide(by_id("S03"))
    assert allowed.action == "ALLOW_CAUTIOUS_CLINICIAN_SUMMARY"
    assert allowed.permission_level == "hard_outcome_claim_allowed_with_caveats"

    for scenario in SCENARIOS:
        decision = decide(scenario)
        if scenario.scenario_id != "S03":
            assert decision.permission_level != "hard_outcome_claim_allowed_with_caveats"


def test_fabricated_or_unverifiable_citation_is_denied():
    decision = decide(by_id("S04"))
    assert decision.action == "DENY_CITATION"
    assert decision.permission_level == "no_claim"
    assert "citation" in decision.blocked_by


def test_clot_low_acceptance_is_not_labeled_simple_implementation_failure():
    decision = decide(by_id("S06"))
    assert decision.action == "ESCALATE_WORKFLOW_DIAGNOSIS"
    assert decision.permission_level == "implementation_analysis_only"
    assert "workflow_interpretation" in decision.blocked_by


def test_ana_high_opportunity_cost_abstains():
    decision = decide(by_id("S07"))
    assert decision.action == "ABSTAIN_OPPORTUNITY_COST"
    assert decision.permission_level == "workflow_trial_required"
    assert "opportunity_cost" in decision.blocked_by


def test_yablo_style_nonterminal_evidence_chain_abstains():
    decision = decide(by_id("S08"))
    assert decision.action == "ABSTAIN_EVIDENCE_CHAIN"
    assert decision.permission_level == "ask_for_terminal_patient_outcome"
    assert "evidence_chain" in decision.blocked_by


def test_context_sensitive_gesture_claim_abstains_without_material_context():
    decision = decide(by_id("S09"))
    assert decision.action == "ABSTAIN_CONTEXT"
    assert decision.permission_level == "no_action_claim"
    assert "context" in decision.blocked_by


def test_seir_variant_shift_is_sent_to_stress_testing():
    decision = decide(by_id("S10"))
    assert decision.action == "STRESS_TEST_GENERALIZATION"
    assert decision.permission_level == "research_or_monitoring_only"
    assert "population_or_shift" in decision.blocked_by


def test_every_scenario_keeps_human_authority_boundary_explicit():
    for scenario in SCENARIOS:
        assert scenario.clinician_authority
        assert "authority" in scenario.clinician_authority or "clinician" in scenario.clinician_authority or "public_health" in scenario.clinician_authority


def test_bounded_evidence_ambiguity_is_narrowed_before_claim_composition():
    decision = decide(by_id("S13"))
    assert decision.action == "NARROW_TO_SURROGATE"
    assert decision.permission_level == "surrogate_or_process_claim_only"
    assert "endpoint_strength" in decision.blocked_by


def test_audio_captioning_metric_is_surrogate_not_communication_outcome():
    decision = decide(by_id("S14"))
    assert decision.action == "NARROW_TO_SURROGATE"
    assert decision.permission_level == "surrogate_or_process_claim_only"
    assert "endpoint_strength" in decision.blocked_by


def test_telemedicine_practice_is_allowed_only_as_simulation_training():
    decision = decide(by_id("S15"))
    assert decision.action == "ALLOW_BOUNDED_TRAINING_SIMULATION"
    assert decision.permission_level == "simulation_training_only"
    assert decision.blocked_by == ()


def test_sik3_tinnitus_claim_is_narrowed_to_genetic_association():
    decision = decide(by_id("S16"))
    assert decision.action == "NARROW_TO_SURROGATE"
    assert decision.permission_level == "surrogate_or_process_claim_only"
    assert "endpoint_strength" in decision.blocked_by


def test_altitude_circadian_claim_is_sent_to_shift_testing():
    decision = decide(by_id("S17"))
    assert decision.action == "STRESS_TEST_GENERALIZATION"
    assert decision.permission_level == "research_or_monitoring_only"
    assert "population_or_shift" in decision.blocked_by


def test_robotic_cadaver_rehearsal_is_training_only():
    decision = decide(by_id("S18"))
    assert decision.action == "ALLOW_BOUNDED_TRAINING_SIMULATION"
    assert decision.permission_level == "simulation_training_only"
    assert decision.blocked_by == ()


def test_reverse_flynn_norm_drift_is_sent_to_shift_testing():
    decision = decide(by_id("S19"))
    assert decision.action == "STRESS_TEST_GENERALIZATION"
    assert decision.permission_level == "research_or_monitoring_only"
    assert "population_or_shift" in decision.blocked_by


def test_penrose_quotient_analogy_preserves_context_before_transport():
    decision = decide(by_id("S20"))
    assert decision.action == "ABSTAIN_TRANSPORT"
    assert decision.permission_level == "research_or_monitoring_only"
    assert "population_or_shift" in decision.blocked_by


def test_cross_script_transcript_requires_provenance_before_claim_use():
    decision = decide(by_id("S21"))
    assert decision.action == "ABSTAIN_PROVENANCE"
    assert decision.permission_level == "audit_only"
    assert "context" in decision.blocked_by


def test_saliva_evolutionary_genomics_is_not_individual_clinical_action():
    decision = decide(by_id("S22"))
    assert decision.action == "NARROW_TO_SURROGATE"
    assert decision.permission_level == "surrogate_or_process_claim_only"
    assert "endpoint_strength" in decision.blocked_by


def test_sequential_depletion_ordering_requires_budget_stress_test():
    decision = decide(by_id("S23"))
    assert decision.action == "STRESS_TEST_ORDERING"
    assert decision.permission_level == "budget_ordering_simulation_only"
    assert "ordering_or_budget" in decision.blocked_by


def test_consumer_heart_rate_signal_is_monitoring_not_diagnosis():
    decision = decide(by_id("S24"))
    assert decision.action == "NARROW_TO_SURROGATE"
    assert decision.permission_level == "surrogate_or_process_claim_only"
    assert "endpoint_strength" in decision.blocked_by


def test_latent_alpha_requires_orthogonal_projection_audit():
    decision = decide(by_id("S25"))
    assert decision.action == "STRESS_TEST_CONFOUNDING"
    assert decision.permission_level == "projection_audit_only"
    assert "confounding_or_projection" in decision.blocked_by


def test_family_genomic_consent_preserves_boundary():
    decision = decide(by_id("S26"))
    assert decision.action == "PRESERVE_CONSENT_BOUNDARY"
    assert decision.permission_level == "consent_boundary_audit_only"
    assert "consent_aggregation" in decision.blocked_by


def test_recurring_hospital_genetics_is_triage_not_treatment_authority():
    decision = decide(by_id("S27"))
    assert decision.action == "NARROW_TO_SURROGATE"
    assert decision.permission_level == "surrogate_or_process_claim_only"
    assert "endpoint_strength" in decision.blocked_by


def test_speculative_topological_theory_is_provenance_audit_only():
    scenario = by_id("S28")
    decision = decide(scenario)
    assert scenario.citation_status == "verified"
    assert decision.action == "ABSTAIN_PROVENANCE"
    assert decision.permission_level == "audit_only"
    assert "context" in decision.blocked_by


def test_kan_architecture_claim_is_method_evidence_not_clinical_permission():
    scenario = by_id("S29")
    decision = decide(scenario)
    assert "Kolmogorov-Arnold" in scenario.claim_requested
    assert decision.action == "NARROW_TO_SURROGATE"
    assert decision.permission_level == "surrogate_or_process_claim_only"
    assert "endpoint_strength" in decision.blocked_by


def test_picture_language_simulation_requires_provenance_audit():
    scenario = by_id("S30")
    decision = decide(scenario)
    assert "picture-language" in scenario.label.lower()
    assert decision.action == "ABSTAIN_PROVENANCE"
    assert decision.permission_level == "audit_only"
    assert "context" in decision.blocked_by
