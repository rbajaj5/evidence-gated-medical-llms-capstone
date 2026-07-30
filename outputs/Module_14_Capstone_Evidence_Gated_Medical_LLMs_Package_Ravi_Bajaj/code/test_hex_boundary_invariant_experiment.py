from hex_boundary_invariant_experiment import run


def test_full_hex_boards_have_exactly_one_crossing():
    summary = run()
    assert summary["board_sizes_enumerated"] == [1, 2, 3, 4]
    assert summary["total_full_boards_enumerated"] == 66066
    assert summary["both_crossing_count"] == 0
    assert summary["neither_crossing_count"] == 0
    assert summary["exactly_one_crossing_all_full_boards"] is True


def test_small_hex_first_player_win_matches_strategy_stealing_claim():
    summary = run()
    assert summary["first_player_win_sizes_checked"] == [1, 2, 3]
    assert summary["first_player_wins_all_checked"] is True
    assert summary["minimax_by_size"] == {"1": True, "2": True, "3": True}


def test_majority_triangle_coarse_graining_has_no_local_ties():
    summary = run()
    majority = summary["majority_triangle_summary"]
    assert majority["patterns"] == 8
    assert majority["tie_count"] == 0
    assert majority["blue_majority_patterns"] == 4
    assert majority["yellow_majority_patterns"] == 4
    assert majority["odd_local_aggregation"] is True
