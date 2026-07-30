from orthogonal_projection_experiment import run


def test_projection_removes_design_matrix_component():
    summary = run()
    assert summary["orthogonality_passed"] is True
    assert summary["max_abs_design_inner_product_after"] < 1e-10
    assert summary["max_abs_design_inner_product_before"] > 1.0


def test_projection_detects_that_latent_component_was_confounded():
    summary = run()
    assert summary["projection_removed_design_signal"] is True
    assert summary["projected_component_norm"] > summary["alpha_norm_after_projection"]
