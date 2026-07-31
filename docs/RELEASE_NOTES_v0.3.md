# Release Notes: v0.3 Coordination Benchmark Audit

Adds a synthetic benchmark-design audit inspired by:

Gessler, T., Dizdarevic, T., Calinescu, A., Ellis, B., Lupu, A., & Foerster, J. N. (2025). *OvercookedV2: Rethinking Overcooked for Zero-Shot Coordination*. ICLR 2025. https://arxiv.org/abs/2503.17821

## Added

- `coordination_benchmark_audit.py`
- `test_coordination_benchmark_audit.py`
- `coordination_benchmark_audit_summary.json`

## Interpretation

The audit separates:

- state-coverage failures,
- weak benchmark design after state augmentation,
- asymmetric-information coordination,
- stochastic workflow coordination,
- grounded communication,
- implicit action demonstration,
- and test-time protocol formation.

The capstone implication is narrow: a medical LLM benchmark should not treat broad prompt/chart state coverage as evidence of clinician-AI coordination. Genuine coordination tests need hidden information, stochastic workflow, protocol formation, and runtime auditability.

## Validation

Local validation before push:

```text
120 passed
```

## Boundary

No clinical behavior changed. This is a benchmark-design audit and does not introduce any medical claims or patient-facing functionality.
