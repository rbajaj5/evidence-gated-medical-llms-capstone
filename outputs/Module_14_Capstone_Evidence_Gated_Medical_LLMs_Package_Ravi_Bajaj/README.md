# Module 14 Capstone Package

## Project

Surrogate-Aware Runtime Assurance for Agentic Medical LLMs: Preventing evidence overclaiming in clinician-facing AI systems.

## Goal

This package proposes and implements a synthetic runtime-assurance framework for agentic medical LLM outputs and proposed actions, with the practical genetics scope narrowed to recurring hospital problems: pharmacogenomic alerts, newborn-screening follow-up, ACMG secondary findings, hereditary cancer/FH/Lynch flags, VUS handling, and family-linked privacy boundaries. The central idea is to decouple evidence assets from claim currencies: a fluent answer, real citation, surrogate endpoint, workflow metric, genetic result, and patient-outcome RCT do not carry the same permission level.

## What Is Already Done

- Stress-test harness implemented with 30 scenarios.
- Expected actions matched in 30 of 30 scenarios.
- ZDD-style sparse-family audit implemented across 39 evidence features.
- Observed stress states compressed to 89 ZDD nodes versus a naive trie upper bound of 899.
- Model-selection audit implemented with 19 candidate claim models and 30 matched expected actions.
- Proof-status/provenance poset audit enumerates 4096 states and 18432 cover transitions; only 4 states allow hard outcomes, and NIETTU remains audit-only under source/proof upgrades.
- Picture-language diagram audit classifies 9 multimodal/mathematical artifacts; none allow hard-outcome permission, 5 reset validation after representation transfer, and the Bourgade-Huang loop-equation row remains universality-audit-only.
- Loop-equation/Gronwall stability probe checks 6 invariant gates: stable transfer ends at 0.0173 under budget 0.050, while missing-provenance transfer ends at 0.1792 over budget 0.050; switching-cumulant checks cancel the main quadratic term and keep rare-event/replacement errors inside budget.
- Branch-factor/Volterra path probe accepts the separated synthetic branch with contraction ratio 0.0416 and blocks the near-collision family/population branch, preserving the BBGKY contact/collision warning.
- Sequential-depletion ordering experiment implemented across 24 runtime-load permutations.
- Orthogonal-projection confounding experiment passed: max design inner product after projection is 4.68e-15.
- Kelly-style runtime exposure experiment shows all-in ruin probability 1.000 despite favorable expected value.
- Uniform-witness sampling experiment shows biased strongest-five witness display has variation distance 0.828 from the uniform admissible witness distribution.
- Family genomic-consent experiment detects ranked-choice cycling, blocks full raw release, and preserves partial inclusion under synthetic epsilon budget 1.00.
- Finite event-algebra experiment verifies measurable-event identities over 144 runtime histories.
- Measure-on-measures experiment compares 4 source-population measures against a meta-measure mixture.
- Mahalanobis covariate-distance experiment flags 2 synthetic source(s) for source-specific validation.
- Exact matrix counterexample probe verifies a 2x2 rank-one projector failure with violation factor 1 + sqrt(2); included only as a counterexample-search analogy.
- Tail/maximal-inequality runtime probe enumerates 4096 mean-zero paths and shows pathwise boundary crossing can exceed terminal-only exceedance.
- Hex/Y boundary probe enumerates 66066 full boards with no both/neither terminal crossings and verifies majority-triangle coarse-graining has 0 local ties.
- Hex scaling/coarse-graining probe samples 36000 larger boards with 0 ambiguous terminals, then shows generic smoothing can flip the global crossing at rate 0.256.
- Companion Python verification script included for sequential-depletion manuscript checks.
- Figures generated for gate architecture, runtime action counts, endpoint/design permission mapping, proof-status poset audit, and supporting experiment probes.
- Survivorship-bias aircraft figure added as a missing-denominator analogy for medical LLM evaluation, with original SVG and PNG included under its CC BY-SA 4.0 attribution.
- Reverse-sprinkler momentum-flux result added as a bounded analogy for why LLM evidence flow is not safely invertible without provenance logs.
- Tests verify that surrogate evidence cannot become a hard-outcome claim, fabricated citations are denied, CLOT-style low acceptance is routed to workflow diagnosis, Kanazawa-style evidence ambiguity is narrowed before claim composition, recurring hospital genetics triage, SIK3/tinnitus, saliva evolutionary genomics, and consumer heart-rate/wearable physiology are narrowed to surrogate monitoring or mechanism/association evidence, altitude/circadian and reverse-Flynn cases are stress-tested, robot-as-cadaver rehearsal stays training-only, cross-script, Romani-style language, and picture-language inputs require provenance audit, and Connes/Penrose evidence-patch collapse is blocked by a transport gate.
- Liquid neural networks noted as a future streaming-monitor architecture while keeping the assurance layer model-agnostic.
- Nonlocal modeling, game p-Laplacian inpainting, and coding/cryptography references added as bounded analogies for memory, reconstruction, and decodable provenance in transformed medical inputs.
- PSLQ/Euler-sum experimental mathematics added as a bounded analogy for candidate discovery versus proof/validation status.
- PhilPapers/PhilArchive NIETTU topological-theory record added as a proof-status/provenance stress case: verified source existence does not imply clinical validation or medical claim permission.
- Kolmogorov-Arnold Networks critical-assessment preprint added as a model-selection stress case: theorem-inspired architecture claims remain method/surrogate evidence until clinical validation gates are satisfied.
- Jaffe-Liu picture-language program added as a multimodal simulation stress case: diagrams, screenshots, photos, and videos require an explicit simulation map before clinical claim use.
- Bourgade-Huang loop-equation characterization added as a universality stress case: approximate invariant hierarchies support portability audits but do not authorize clinical outcome claims.
- Gronwall, resolvent-stability, cumulant-error, and random d-regular switching-calculus excerpts added as runtime-stability language for error propagation and sparse-network perturbation audits.
- Branch-factor, radial Volterra, and BBGKY collision excerpts added as branch-stability language for near-collision family, population, and contact-term audits.
- Axelrod/Hamilton and Wu/Axelrod cooperation/noise references added as bounded adoption and family-consent analogies; noisy interaction is audited before being interpreted as defection/refusal.
- Sequential depletion ordering added as a concrete runtime-budget experiment: small-first, large-first, FIFO, and LIFO are not interchangeable once residual budgets matter.
- Figaro noted as a future probabilistic-programming substrate for richer runtime-history and source-measure models; the submitted artifact remains dependency-light Python.

## Package Contents

- `proposal/`: Week 11 research proposal in DOCX and PDF.
- `paper/`: Final paper draft in DOCX and PDF.
- `summary/`: Required 1-2 page summary sheet in DOCX and PDF.
- `supplement/`: Technical supplement with scenario matrix and reproducibility notes.
- `code/`: Synthetic stress-test harness and tests.
- `results/`: JSON and CSV outputs, including the ZDD sparse-family and model-selection summaries.
- `figures/`: Generated figures used in the paper.
- `demo/`: Skater/Hawkes logged replay video and contact sheet, included only as a runtime-assurance visual analogy.
- Runtime implementation note: async/coroutine control flow is used as an analogy for suspending output until assurance checks pass.

## Safety Boundary

This is not a medical product. It does not use real patient data, does not diagnose, does not recommend treatment, and does not validate clinical effectiveness. It is an auditable design and evaluation artifact for clinician-facing LLM safety.

## Reproduction

```powershell
$env:PYTHONPATH=(Resolve-Path 'work\evidence_gated_llm_capstone').Path
& 'C:\Users\anaxe\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'work\evidence_gated_llm_capstone\run_evidence_gate_stress_test.py'
& 'C:\Users\anaxe\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'work\evidence_gated_llm_capstone\zdd_sparse_claim_family.py'
& 'C:\Users\anaxe\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'work\evidence_gated_llm_capstone\model_selection_claim_policy.py'
& 'C:\Users\anaxe\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'work\evidence_gated_llm_capstone\proof_status_poset_experiment.py'
& 'C:\Users\anaxe\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'work\evidence_gated_llm_capstone\picture_language_diagram_audit.py'
& 'C:\Users\anaxe\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'work\evidence_gated_llm_capstone\loop_equation_runtime_stability.py'
& 'C:\Users\anaxe\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'work\evidence_gated_llm_capstone\branch_factor_path_stability.py'
& 'C:\Users\anaxe\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'work\evidence_gated_llm_capstone\depletion_ordering_experiment.py'
& 'C:\Users\anaxe\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'work\evidence_gated_llm_capstone\orthogonal_projection_experiment.py'
& 'C:\Users\anaxe\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'work\evidence_gated_llm_capstone\kelly_runtime_budget_experiment.py'
& 'C:\Users\anaxe\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'work\evidence_gated_llm_capstone\uniform_witness_sampling_experiment.py'
& 'C:\Users\anaxe\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'work\evidence_gated_llm_capstone\consent_aggregation_experiment.py'
& 'C:\Users\anaxe\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'work\evidence_gated_llm_capstone\event_algebra_experiment.py'
& 'C:\Users\anaxe\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'work\evidence_gated_llm_capstone\measure_on_measures_experiment.py'
& 'C:\Users\anaxe\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'work\evidence_gated_llm_capstone\mahalanobis_covariate_experiment.py'
& 'C:\Users\anaxe\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'work\evidence_gated_llm_capstone\noncommutative_amgm_counterexample.py'
& 'C:\Users\anaxe\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'work\evidence_gated_llm_capstone\tail_maximal_inequality_experiment.py'
& 'C:\Users\anaxe\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'work\evidence_gated_llm_capstone\hex_boundary_invariant_experiment.py'
& 'C:\Users\anaxe\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'work\evidence_gated_llm_capstone\hex_scaling_coarse_grain_experiment.py'
& 'C:\Users\anaxe\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' 'work\evidence_gated_llm_capstone\sequential_depletion_verification.py'
py -3.13 -m pytest 'work\evidence_gated_llm_capstone' -q
```

## Final DOCX Files

- `Module_14_Capstone_Proposal_Evidence_Gated_Medical_LLMs_Ravi_Bajaj.docx`
- `Module_14_Final_Paper_Evidence_Gated_Medical_LLMs_Ravi_Bajaj.docx`
- `Module_14_Summary_Sheet_Evidence_Gated_Medical_LLMs_Ravi_Bajaj.docx`
- `Module_14_Technical_Supplement_Evidence_Gated_Medical_LLMs_Ravi_Bajaj.docx`

## Final PDF Files

- `Module_14_Capstone_Proposal_Evidence_Gated_Medical_LLMs_Ravi_Bajaj.pdf`
- `Module_14_Final_Paper_Evidence_Gated_Medical_LLMs_Ravi_Bajaj.pdf`
- `Module_14_Summary_Sheet_Evidence_Gated_Medical_LLMs_Ravi_Bajaj.pdf`
- `Module_14_Technical_Supplement_Evidence_Gated_Medical_LLMs_Ravi_Bajaj.pdf`
