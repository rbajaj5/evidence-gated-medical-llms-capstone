from oracle_consistency_audit import audit_run, run


def row_by_id(summary, run_id):
    return next(row for row in summary["rows"] if row["run_id"] == run_id)


def test_strong_aggregate_play_is_not_oracle_safety():
    summary = run()
    row = row_by_id(summary, "O05")
    assert row["full_trace_match"] >= 0.75
    assert row["full_trace_perfect"] == 0.0
    assert row["action"] == "DO_NOT_EQUATE_STRONG_WITH_ORACLE_SAFE"


def test_more_context_frames_do_not_replace_supervision():
    summary = run()
    row = row_by_id(summary, "O02")
    assert row["representation_only_change"] is True
    assert row["action"] == "DO_NOT_TREAT_MORE_CONTEXT_AS_SUPERVISION"


def test_auxiliary_oracle_supervision_improves_but_does_not_certify():
    summary = run()
    row = row_by_id(summary, "O06")
    assert row["auxiliary_oracle_supervision"] is True
    assert row["full_trace_perfect"] == 0.0
    assert row["action"] == "ALLOW_WITH_RUNTIME_ORACLE_MONITOR"


def test_perfect_traces_still_need_sampled_state_audit():
    summary = run()
    row = row_by_id(summary, "O04")
    assert row["full_trace_perfect"] == 1.0
    assert row["sampled_state_match"] < 1.0
    assert row["action"] == "REQUIRE_RANDOM_START_ORACLE_AUDIT"


def test_azal_mean_match_exceeds_selected_vanilla_mean_match():
    summary = run()
    assert summary["mean_azal_full_trace_match"] > summary["mean_vanilla_full_trace_match"]


def test_summary_preserves_arxiv_source_and_case_count():
    summary = run()
    assert summary["source"] == "https://arxiv.org/abs/2607.08984"
    assert summary["case_count"] == 6
