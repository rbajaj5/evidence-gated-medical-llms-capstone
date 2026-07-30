from zdd_sparse_claim_family import (
    MiniZDD,
    FEATURE_ORDER,
    SCENARIOS,
    hard_outcome_claim_family,
    narrow_surrogate_family,
    observed_stress_family,
    run,
    scenario_features,
    bounded_training_family,
    provenance_gap_family,
    runtime_ordering_family,
    orthogonal_projection_family,
    consent_boundary_family,
)


def scenario_by_id(scenario_id):
    return next(s for s in SCENARIOS if s.scenario_id == scenario_id)


def test_observed_family_contains_every_stress_scenario():
    zdd = MiniZDD(FEATURE_ORDER)
    root = zdd.build(observed_stress_family())
    for scenario in SCENARIOS:
        assert zdd.contains(root, scenario_features(scenario))


def test_hard_outcome_family_allows_only_hard_outcome_scenario():
    zdd = MiniZDD(FEATURE_ORDER)
    root = zdd.build(hard_outcome_claim_family())
    assert zdd.contains(root, scenario_features(scenario_by_id("S03")))
    assert not zdd.contains(root, scenario_features(scenario_by_id("S02")))
    assert not zdd.contains(root, scenario_features(scenario_by_id("S13")))


def test_surrogate_family_allows_surrogate_cases_but_not_hard_outcome_case():
    zdd = MiniZDD(FEATURE_ORDER)
    root = zdd.build(narrow_surrogate_family())
    assert zdd.contains(root, scenario_features(scenario_by_id("S02")))
    assert zdd.contains(root, scenario_features(scenario_by_id("S13")))
    assert zdd.contains(root, scenario_features(scenario_by_id("S14")))
    assert zdd.contains(root, scenario_features(scenario_by_id("S16")))
    assert zdd.contains(root, scenario_features(scenario_by_id("S22")))
    assert zdd.contains(root, scenario_features(scenario_by_id("S24")))
    assert zdd.contains(root, scenario_features(scenario_by_id("S27")))
    assert zdd.contains(root, scenario_features(scenario_by_id("S29")))
    assert not zdd.contains(root, scenario_features(scenario_by_id("S03")))
    assert not zdd.contains(root, scenario_features(scenario_by_id("S17")))
    assert not zdd.contains(root, scenario_features(scenario_by_id("S19")))


def test_zdd_representation_is_smaller_than_naive_observed_trie_bound():
    summary = run()
    assert summary["observed_membership_all_true"] is True
    assert summary["observed_zdd_node_count"] < summary["naive_observed_trie_upper_bound"]
    assert summary["s03_hard_outcome_allowed"] is True
    assert summary["s02_hard_outcome_allowed"] is False
    assert summary["s29_surrogate_allowed"] is True


def test_fifo_lifo_note_is_a_policy_not_membership_rule():
    summary = run()
    assert summary["event_ordering_policy"]["audit_log"] == "FIFO"
    assert summary["event_ordering_policy"]["zdd_construction"] == "recursive LIFO/backtracking"
    assert summary["event_ordering_policy"]["runtime_safety_decision"] == "priority-ordered boundary crossing"


def test_training_family_allows_telemedicine_practice_not_audio_overclaim():
    zdd = MiniZDD(FEATURE_ORDER)
    root = zdd.build(bounded_training_family())
    assert zdd.contains(root, scenario_features(scenario_by_id("S15")))
    assert zdd.contains(root, scenario_features(scenario_by_id("S18")))
    assert not zdd.contains(root, scenario_features(scenario_by_id("S14")))


def test_provenance_gap_family_allows_cross_script_audit_only_case():
    zdd = MiniZDD(FEATURE_ORDER)
    root = zdd.build(provenance_gap_family())
    assert zdd.contains(root, scenario_features(scenario_by_id("S21")))
    assert zdd.contains(root, scenario_features(scenario_by_id("S28")))
    assert zdd.contains(root, scenario_features(scenario_by_id("S30")))
    assert not zdd.contains(root, scenario_features(scenario_by_id("S04")))


def test_runtime_ordering_family_allows_only_depletion_budget_case():
    zdd = MiniZDD(FEATURE_ORDER)
    root = zdd.build(runtime_ordering_family())
    assert zdd.contains(root, scenario_features(scenario_by_id("S23")))
    assert not zdd.contains(root, scenario_features(scenario_by_id("S15")))


def test_orthogonal_projection_family_allows_only_latent_alpha_case():
    zdd = MiniZDD(FEATURE_ORDER)
    root = zdd.build(orthogonal_projection_family())
    assert zdd.contains(root, scenario_features(scenario_by_id("S25")))
    assert not zdd.contains(root, scenario_features(scenario_by_id("S15")))


def test_consent_boundary_family_allows_only_family_genomic_consent_case():
    zdd = MiniZDD(FEATURE_ORDER)
    root = zdd.build(consent_boundary_family())
    assert zdd.contains(root, scenario_features(scenario_by_id("S26")))
    assert not zdd.contains(root, scenario_features(scenario_by_id("S15")))
