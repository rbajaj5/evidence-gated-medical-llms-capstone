from hex_scaling_coarse_grain_experiment import run


def test_sampled_large_hex_boards_have_no_ambiguous_terminal_state():
    summary = run(crossing_samples=120, smoothing_samples=80)
    assert summary["ambiguous_terminal_count"] == 0
    assert summary["sampled_full_boards"] == 2160


def test_unbiased_random_hex_is_near_balanced_in_sample():
    summary = run(crossing_samples=180, smoothing_samples=80)
    assert 0.35 <= summary["unbiased_blue_crossing_mean"] <= 0.65


def test_generic_local_smoothing_can_flip_global_boundary():
    summary = run(crossing_samples=120, smoothing_samples=120)
    assert summary["max_coarse_grain_flip_rate"] > 0
    assert summary["max_coarse_grain_flip_setting"]["board_size"] in [7, 9, 11, 13, 15]
