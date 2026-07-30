# Safety and Data Boundary

This repository is a synthetic research artifact for a course capstone. It is designed to evaluate evidence-governance logic for medical LLM outputs, not to provide clinical guidance.

## Explicit Non-Use Claims

- No real patient data is used.
- No clinical diagnosis is produced.
- No treatment recommendation is produced.
- No clinical-effectiveness claim is validated.
- No deployment integration is provided.
- No EHR connection, medical device connection, wearable-device connection, or live model endpoint is included.

## Assurance Boundary

The framework treats LLM output as a candidate claim requiring runtime checks. The gate can allow, narrow, audit, stress-test, or deny a claim depending on evidence status and context. In the capstone artifact, these checks are synthetic and deterministic.

The submitted framework is about permission to state a claim, not permission to act on a patient.

## Genetics and Family Data Boundary

The genetics portion is framed as a governance and privacy problem. It uses synthetic examples to reason about family-linked consent, source-population mismatch, and graded access to genetic information. It does not process real genomic data and does not generate polygenic risk scores.

## Intended Review Use

The repository is suitable for reviewing:

- research proposal logic,
- reproducible synthetic experiments,
- runtime-assurance design,
- transparency of generative-AI use,
- evidence-overclaiming safeguards,
- and future directions for responsible clinical evaluation.

It is not suitable for clinical or patient-facing use.
