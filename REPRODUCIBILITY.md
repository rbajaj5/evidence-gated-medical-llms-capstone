# Reproducibility

This repository is intentionally dependency-light. The executable part of the capstone is a set of synthetic Python experiments and tests under `work/evidence_gated_llm_capstone/`.

## Environment

Tested locally with Python 3.13 on Windows.

```powershell
py -3.13 -m pip install -r requirements.txt
$env:PYTHONPATH=(Resolve-Path 'work\evidence_gated_llm_capstone').Path
py -3.13 -m pytest 'work\evidence_gated_llm_capstone' -q
```

Expected result:

```text
115 passed
```

## Main Experiment Scripts

- `run_evidence_gate_stress_test.py`: scenario/action gate for LLM-style medical claims.
- `model_selection_claim_policy.py`: policy-model selection audit over candidate claim policies.
- `zdd_sparse_claim_family.py`: sparse-family compression audit for evidence feature sets.
- `proof_status_poset_experiment.py`: proof/provenance permission poset.
- `picture_language_diagram_audit.py`: multimodal/diagram provenance audit.
- `loop_equation_runtime_stability.py`: synthetic loop-equation and Gronwall-style stability probe.
- `branch_factor_path_stability.py`: branch-factor and near-collision stability probe.
- `consent_aggregation_experiment.py`: ranked family-consent privacy-budget experiment.
- `mahalanobis_covariate_experiment.py`: source-population covariate distance probe.
- `hex_boundary_invariant_experiment.py` and `hex_scaling_coarse_grain_experiment.py`: boundary/coarse-graining checks used as assurance analogies.

## Generated Artifacts

Generated CSV and JSON outputs are committed under:

```text
work/evidence_gated_llm_capstone/results/
outputs/Module_14_Capstone_Evidence_Gated_Medical_LLMs_Package_Ravi_Bajaj/results/
```

The final course-facing package is:

```text
outputs/Module_14_Capstone_Evidence_Gated_Medical_LLMs_Package_Ravi_Bajaj.zip
```

The package manifest is:

```text
outputs/Module_14_Capstone_Evidence_Gated_Medical_LLMs_Package_Ravi_Bajaj/MANIFEST_SHA256.csv
```
