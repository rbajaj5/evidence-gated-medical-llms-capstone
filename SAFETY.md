# Safety and Data Boundary

This repository is a synthetic research artifact for a course capstone. It is designed to evaluate evidence-governance logic for medical LLM alert text, not to provide clinical guidance.

## Active Scope

The active submission-facing package studies one workflow:

```text
LLM-drafted pharmacogenomic or genomic medication-alert text.
```

The implemented controller checks three evidence gates:

1. Endpoint/actionability.
2. Population fit.
3. Citation/guideline support.

## Explicit Non-Use Claims

- No real patient data is used.
- No protected health information is used.
- No private genomic data is used.
- No clinical diagnosis is produced.
- No treatment recommendation is produced.
- No clinical-effectiveness claim is validated.
- No EHR connection, medical-device connection, wearable-device connection, or live model endpoint is included.

## Assurance Boundary

The gate evaluates permission to state or display a claim. It may allow bounded alert language, narrow the claim, abstain because population fit or citation support is insufficient, or deny unsupported action language.

The submitted framework is about claim discipline, not permission to act on a patient.

## Stage 1 Versus Stage 2

Stage 1 uses 30 author-designed synthetic cases to verify that the gate follows the intended policy. These are construct-validity results only.

Stage 2 would require independently authored cases and blinded reviewer adjudication by qualified clinicians, pharmacogenomics reviewers, or pharmacists. That stage would report overclaim reduction, inappropriate denial, calibration, interrater agreement, and error categories.

## Genetics Boundary

Public guideline and database names are used as evidence anchors and population-fit examples. The project does not compute polygenic risk scores, infer traits, process family genomes, or issue pharmacogenomic guidance for a real person.

It is not suitable for clinical or patient-facing use.
