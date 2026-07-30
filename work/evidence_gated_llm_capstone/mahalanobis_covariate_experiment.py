"""Synthetic Mahalanobis covariate-balance experiment.

This is a nonclinical source-transport audit. It treats each source population
as a covariate vector and measures distance from a reference distribution using
the inverse covariance. Large distance triggers source-specific validation
rather than aggregate transport.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"

FEATURES = (
    "pc1_ancestry",
    "pc2_ancestry",
    "mean_age_scaled",
    "rural_access_scaled",
    "missingness_scaled",
    "privacy_constraint_scaled",
)

REFERENCE_MEAN = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

# Diagonal covariance plus low-rank-looking simplification kept explicit for a
# dependency-light audit script. Values are synthetic scale assumptions.
REFERENCE_VARIANCE = [1.00, 0.85, 0.70, 0.60, 0.50, 0.45]

SOURCE_COVARIATES = {
    "us_ehr_like": [0.10, -0.05, 0.15, -0.10, 0.20, 0.10],
    "genomeindia_like": [1.45, 0.85, -0.05, 0.70, 0.55, 0.80],
    "latin_america_admixed_like": [0.95, -1.15, -0.10, 0.35, 0.50, 0.65],
    "israel_biobank_like": [0.35, 0.15, 0.20, -0.05, 0.15, 0.25],
}

ACTION_THRESHOLD = 2.0


def mahalanobis_distance(vector: list[float], mean: list[float], variance: list[float]) -> float:
    squared = sum(((x - mu) ** 2) / var for x, mu, var in zip(vector, mean, variance, strict=True))
    return math.sqrt(squared)


def standardized_contributions(vector: list[float], mean: list[float], variance: list[float]) -> dict[str, float]:
    return {
        feature: ((x - mu) ** 2) / var
        for feature, x, mu, var in zip(FEATURES, vector, mean, variance, strict=True)
    }


def run() -> dict[str, object]:
    source_rows = {}
    for source, vector in SOURCE_COVARIATES.items():
        distance = mahalanobis_distance(vector, REFERENCE_MEAN, REFERENCE_VARIANCE)
        contributions = standardized_contributions(vector, REFERENCE_MEAN, REFERENCE_VARIANCE)
        top_feature = max(contributions, key=contributions.get)
        source_rows[source] = {
            "mahalanobis_distance": distance,
            "requires_source_specific_validation": distance > ACTION_THRESHOLD,
            "largest_contribution_feature": top_feature,
            "largest_contribution_value": contributions[top_feature],
            "contributions": contributions,
        }

    summary = {
        "feature_count": len(FEATURES),
        "source_count": len(SOURCE_COVARIATES),
        "action_threshold": ACTION_THRESHOLD,
        "source_rows": source_rows,
        "flagged_sources": [
            source for source, row in source_rows.items() if row["requires_source_specific_validation"]
        ],
        "max_distance_source": max(source_rows, key=lambda source: source_rows[source]["mahalanobis_distance"]),
        "max_distance": max(row["mahalanobis_distance"] for row in source_rows.values()),
        "interpretation": (
            "Mahalanobis distance turns population/covariate fit into a runtime transport gate. "
            "A source with large covariance-adjusted distance from the reference distribution should be routed "
            "to source-specific validation, not aggregate claim transport."
        ),
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "mahalanobis_covariate_experiment_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
