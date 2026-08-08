# Evidence-Gated Medical LLMs Capstone

[![tests](https://github.com/rbajaj5/evidence-gated-medical-llms-capstone/actions/workflows/tests.yml/badge.svg)](https://github.com/rbajaj5/evidence-gated-medical-llms-capstone/actions/workflows/tests.yml)

Public research artifact for the Module 14 AI-in-healthcare capstone.

## Active submission-facing project

**Evidence-Gated Medical LLM Alerts for Pharmacogenomic Claims: Detecting Overclaiming Relative to Guideline-Supported Evidence**

This repository now treats pruning as the main methodological move. The active capstone package narrows the project to one clinically interpretable workflow: LLM-drafted pharmacogenomic or genomic medication-alert text. The implemented gate checks only three things:

1. Endpoint/actionability.
2. Population fit.
3. Citation/guideline support.

The Stage 1 result is a synthetic construct-validity scaffold, not a clinical safety or patient-outcome claim. The planned Stage 2 study compares ungated and gated LLM drafts on independently authored cases with blinded reviewer adjudication.

## What This Contributes

- A bounded, non-clinical evidence gate for pharmacogenomic/genomic medication-alert text.
- A concrete overclaiming benchmark for cases where guideline support, source population, or actionability is weaker than the drafted LLM language.
- Stage 1 metrics for overclaim reduction, inappropriate denial, sensitivity, specificity, calibration, and error categories.
- A clean package that excludes unrelated exploratory components from the submission-facing artifact.

## Pruned Package

- `outputs/Module_14_Capstone_Pruned_Evidence_Gate_Package_Ravi_Bajaj.zip`
- `outputs/Module_14_Capstone_Pruned_Evidence_Gate_Package_Ravi_Bajaj/`

The package contains the proposal, paper draft, summary sheet, technical supplement, PDFs, executable tests, CSV/JSON results, figures, safety note, README, and manifest.

## Quick Start

```powershell
py -3.13 -m pip install -r requirements.txt
$env:PYTHONPATH=(Resolve-Path 'work\pruned_evidence_gate').Path
py -3.13 'work\pruned_evidence_gate\pruned_evidence_gate.py'
py -3.13 -m pytest 'work\pruned_evidence_gate' -q
```

Expected pruned validation snapshot:

- `6 passed`
- 30 synthetic cases
- 20 ungated overclaims
- 0 gated remaining overclaims
- 0 inappropriate denials

## File Map

- `work/pruned_evidence_gate/`: pruned pharmacogenomic evidence-gate evaluator and tests.
- `work/build_pruned_evidence_gate_package.py`: deterministic pruned package builder.
- `work/evidence_gated_llm_capstone/`: legacy exploratory harness retained for provenance, not the active submission-facing package.
- `work/build_evidence_gated_llm_capstone_package.py`: legacy broad package builder.
- `work/export_docx_with_word.py`: Word-to-PDF export helper.
- `outputs/Module_14_Capstone_Pruned_Evidence_Gate_Package_Ravi_Bajaj/`: active deliverable package.

## Public Notes

- Reproducibility details: `REPRODUCIBILITY.md`.
- Safety and data boundary: `SAFETY.md`.
- Release notes: `docs/RELEASE_NOTES_v0.1.md`.

## Safety Boundary

This is a research and course artifact. It is not a medical product, does not use real patient data, does not diagnose, does not recommend treatment, and does not validate clinical effectiveness.
