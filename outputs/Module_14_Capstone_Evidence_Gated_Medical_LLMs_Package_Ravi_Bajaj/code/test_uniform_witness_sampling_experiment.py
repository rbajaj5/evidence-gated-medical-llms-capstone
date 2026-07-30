from uniform_witness_sampling_experiment import admissible_witness, run


def test_unverifiable_and_mismatched_witnesses_are_not_admissible():
    assert not admissible_witness(("hard_outcome", "pragmatic_rct", "match", "unverifiable"))
    assert not admissible_witness(("surrogate", "rct", "mismatch", "verified"))


def test_hard_outcome_witness_requires_pragmatic_rct_match_and_verification():
    assert admissible_witness(("hard_outcome", "pragmatic_rct", "match", "verified"))
    assert not admissible_witness(("hard_outcome", "rct", "match", "verified"))
    assert not admissible_witness(("hard_outcome", "pragmatic_rct", "plausible", "verified"))


def test_biased_generator_deviates_from_uniform_witness_distribution():
    summary = run()
    assert summary["admissible_witness_count"] > summary["biased_top_witness_count"]
    assert summary["variation_distance_from_uniform"] > 0.5
    assert summary["biased_endpoint_distribution"]["hard_outcome"] > summary["uniform_endpoint_distribution"]["hard_outcome"]
