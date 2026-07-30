# Evidence-Gated Medical LLMs Capstone

Public research artifact for the Module 14 AI-in-healthcare capstone:

**Surrogate-Aware Runtime Assurance for Agentic Medical LLMs: Preventing Evidence Overclaiming in Clinician-Facing AI Systems**

The project implements a synthetic runtime-assurance framework for medical LLM outputs. It tests whether an LLM-style claim should be allowed, narrowed, audited, stress-tested, or denied based on evidence currency, endpoint strength, source-population context, privacy/consent boundaries, and proof/provenance status.

## What This Contributes

- A bounded, non-clinical evidence gate for clinician-facing medical LLM claims.
- A surrogate-versus-hard-outcomes distinction inspired by the course's LLM evaluation assignment.
- Runtime-assurance tests for overclaiming, fabricated citations, stale evidence, source-population mismatch, family-linked genetic privacy, and multimodal/provenance transfer.
- Synthetic experiments that treat mathematical claims, diagrams, proof status, privacy permissions, and model-selection policies as auditable inputs rather than raw text alone.

## Final Package

- `outputs/Module_14_Capstone_Evidence_Gated_Medical_LLMs_Package_Ravi_Bajaj.zip`
- `outputs/Module_14_Capstone_Evidence_Gated_Medical_LLMs_Package_Ravi_Bajaj/`

The package contains the proposal, final paper, summary sheet, technical supplement, PDFs, executable tests, CSV/JSON results, figures, demo media, and manifest.

## Quick Start

```powershell
py -3.13 -m pip install -r requirements.txt
$env:PYTHONPATH=(Resolve-Path 'work\evidence_gated_llm_capstone').Path
py -3.13 -m pytest 'work\evidence_gated_llm_capstone' -q
```

Expected validation snapshot:

- `113 passed`
- Proposal: 2 pages
- Summary sheet: 2 pages
- Final paper: 20 pages
- Technical supplement: 24 pages

## File Map

- `work/evidence_gated_llm_capstone/`: synthetic assurance experiments and tests.
- `work/build_evidence_gated_llm_capstone_package.py`: deterministic package builder.
- `work/export_docx_with_word.py`: Word-to-PDF export helper.
- `outputs/.../paper/`: final paper in DOCX and PDF.
- `outputs/.../proposal/`: proposal in DOCX and PDF.
- `outputs/.../summary/`: required summary sheet in DOCX and PDF.
- `outputs/.../supplement/`: technical supplement in DOCX and PDF.
- `outputs/.../results/`: generated CSV/JSON evidence.
- `outputs/.../figures/`: generated figures used in the written package.

## Public Notes

- Reproducibility details: `REPRODUCIBILITY.md`.
- Safety and data boundary: `SAFETY.md`.
- Release notes: `docs/RELEASE_NOTES_v0.1.md`.

## Safety Boundary

This is a research and course artifact. It is not a medical product, does not use real patient data, does not diagnose, does not recommend treatment, and does not validate clinical effectiveness.
