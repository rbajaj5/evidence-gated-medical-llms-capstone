from measure_on_measures_experiment import META_MEASURE, run


def test_meta_measure_is_probability_measure_on_source_measures():
    summary = run()
    assert abs(summary["meta_measure_total_mass"] - 1.0) < 1e-12
    assert summary["source_measure_count"] == len(META_MEASURE)
    assert abs(summary["mixture_summary"]["total_mass"] - 1.0) < 1e-12


def test_source_measures_differ_from_meta_measure_mixture():
    summary = run()
    assert summary["max_source_tv_to_mixture"] > 0
    assert summary["source_with_highest_audit_probability"] in META_MEASURE
    for source_summary in summary["source_summaries"].values():
        assert abs(source_summary["total_mass"] - 1.0) < 1e-12
