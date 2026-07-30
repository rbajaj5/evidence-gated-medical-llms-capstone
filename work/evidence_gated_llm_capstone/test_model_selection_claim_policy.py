from model_selection_claim_policy import run, select_claim_model
from run_evidence_gate_stress_test import SCENARIOS


def scenario_by_id(scenario_id):
    return next(s for s in SCENARIOS if s.scenario_id == scenario_id)


def test_model_selection_matches_all_expected_runtime_actions():
    summary = run()
    assert summary["scenario_count"] == 30
    assert summary["candidate_model_count"] == 19
    assert summary["matched_expected_count"] == 30
    assert summary["all_matched_expected"] is True


def test_surrogate_overclaim_selects_surrogate_model_not_hard_outcome_model():
    selected = select_claim_model(scenario_by_id("S02"))
    assert selected["selected_model"] == "narrow_surrogate_claim"
    assert selected["selected_action"] == "NARROW_TO_SURROGATE"
    hard_model = next(item for item in selected["top_losses"] if item["model"] == "narrow_surrogate_claim")
    assert hard_model["missing"] == []


def test_hard_outcome_claim_requires_pragmatic_rct_model():
    selected = select_claim_model(scenario_by_id("S03"))
    assert selected["selected_model"] == "hard_outcome_pragmatic_rct"
    assert selected["selected_action"] == "ALLOW_CAUTIOUS_CLINICIAN_SUMMARY"
    assert selected["selected_loss"] > 0


def test_context_missing_claim_prefers_abstention_over_workflow_or_surrogate():
    selected = select_claim_model(scenario_by_id("S09"))
    assert selected["selected_model"] == "abstain_context_missing"
    assert selected["selected_action"] == "ABSTAIN_CONTEXT"


def test_fifo_lifo_policy_is_explicit_in_model_selection_summary():
    summary = run()
    policy = summary["fifo_lifo_policy"]
    assert "FIFO" in policy
    assert "LIFO" in policy
    assert "priority-ordered" in policy


def test_audio_captioning_benchmark_selects_local_surrogate_model():
    selected = select_claim_model(scenario_by_id("S14"))
    assert selected["selected_model"] == "local_audio_surrogate_claim"
    assert selected["selected_action"] == "NARROW_TO_SURROGATE"
    assert selected["matches_expected"] is True


def test_telemedicine_practice_selects_bounded_training_model():
    selected = select_claim_model(scenario_by_id("S15"))
    assert selected["selected_model"] == "bounded_telemedicine_training_simulation"
    assert selected["selected_action"] == "ALLOW_BOUNDED_TRAINING_SIMULATION"
    assert selected["matches_expected"] is True


def test_sik3_tinnitus_selects_genetic_audiology_surrogate_model():
    selected = select_claim_model(scenario_by_id("S16"))
    assert selected["selected_model"] == "observational_mechanism_surrogate_claim"
    assert selected["selected_action"] == "NARROW_TO_SURROGATE"
    assert selected["matches_expected"] is True


def test_altitude_circadian_shift_selects_stress_test_model():
    selected = select_claim_model(scenario_by_id("S17"))
    assert selected["selected_model"] == "stress_test_temporal_shift"
    assert selected["selected_action"] == "STRESS_TEST_GENERALIZATION"
    assert selected["matches_expected"] is True


def test_robotic_cadaver_rehearsal_selects_bounded_training_model():
    selected = select_claim_model(scenario_by_id("S18"))
    assert selected["selected_model"] == "bounded_telemedicine_training_simulation"
    assert selected["selected_action"] == "ALLOW_BOUNDED_TRAINING_SIMULATION"
    assert selected["matches_expected"] is True


def test_reverse_flynn_norm_drift_selects_stress_test_model():
    selected = select_claim_model(scenario_by_id("S19"))
    assert selected["selected_model"] == "stress_test_temporal_shift"
    assert selected["selected_action"] == "STRESS_TEST_GENERALIZATION"
    assert selected["matches_expected"] is True


def test_penrose_quotient_case_selects_transport_abstention():
    selected = select_claim_model(scenario_by_id("S20"))
    assert selected["selected_model"] == "abstain_transport_gap"
    assert selected["selected_action"] == "ABSTAIN_TRANSPORT"
    assert selected["matches_expected"] is True


def test_cross_script_transcript_selects_provenance_audit_model():
    selected = select_claim_model(scenario_by_id("S21"))
    assert selected["selected_model"] == "abstain_provenance_gap"
    assert selected["selected_action"] == "ABSTAIN_PROVENANCE"
    assert selected["matches_expected"] is True


def test_saliva_genomics_selects_genetic_mechanism_surrogate_model():
    selected = select_claim_model(scenario_by_id("S22"))
    assert selected["selected_model"] == "observational_mechanism_surrogate_claim"
    assert selected["selected_action"] == "NARROW_TO_SURROGATE"
    assert selected["matches_expected"] is True


def test_sequential_depletion_selects_runtime_ordering_stress_test():
    selected = select_claim_model(scenario_by_id("S23"))
    assert selected["selected_model"] == "runtime_budget_ordering_stress_test"
    assert selected["selected_action"] == "STRESS_TEST_ORDERING"
    assert selected["matches_expected"] is True


def test_consumer_heart_rate_selects_observational_surrogate_model():
    selected = select_claim_model(scenario_by_id("S24"))
    assert selected["selected_model"] == "observational_mechanism_surrogate_claim"
    assert selected["selected_action"] == "NARROW_TO_SURROGATE"
    assert selected["matches_expected"] is True


def test_latent_alpha_selects_orthogonal_projection_stress_test():
    selected = select_claim_model(scenario_by_id("S25"))
    assert selected["selected_model"] == "orthogonal_projection_confounding_stress_test"
    assert selected["selected_action"] == "STRESS_TEST_CONFOUNDING"
    assert selected["matches_expected"] is True


def test_family_genomic_consent_selects_boundary_audit():
    selected = select_claim_model(scenario_by_id("S26"))
    assert selected["selected_model"] == "family_consent_boundary_audit"
    assert selected["selected_action"] == "PRESERVE_CONSENT_BOUNDARY"
    assert selected["matches_expected"] is True


def test_recurring_hospital_genetics_selects_triage_support_model():
    selected = select_claim_model(scenario_by_id("S27"))
    assert selected["selected_model"] == "hospital_genetics_triage_support"
    assert selected["selected_action"] == "NARROW_TO_SURROGATE"
    assert selected["matches_expected"] is True


def test_speculative_topological_theory_selects_provenance_audit_model():
    selected = select_claim_model(scenario_by_id("S28"))
    assert selected["selected_model"] == "abstain_provenance_gap"
    assert selected["selected_action"] == "ABSTAIN_PROVENANCE"
    assert selected["matches_expected"] is True


def test_kan_architecture_claim_selects_observational_surrogate_model():
    selected = select_claim_model(scenario_by_id("S29"))
    assert selected["selected_model"] == "observational_mechanism_surrogate_claim"
    assert selected["selected_action"] == "NARROW_TO_SURROGATE"
    assert selected["matches_expected"] is True


def test_picture_language_simulation_selects_provenance_audit_model():
    selected = select_claim_model(scenario_by_id("S30"))
    assert selected["selected_model"] == "abstain_provenance_gap"
    assert selected["selected_action"] == "ABSTAIN_PROVENANCE"
    assert selected["matches_expected"] is True
