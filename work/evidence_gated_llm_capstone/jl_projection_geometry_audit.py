"""Johnson-Lindenstrauss projection audit for medical LLM assurance.

Inspired by Li's unified JL analysis, this synthetic experiment separates
geometry-preserving dimensionality reduction from privacy, fairness, and
clinical validity. In the capstone setting, a projection may preserve distances
well enough for a bounded source-population or genetic-feature audit, but it
does not by itself authorize diagnostic, treatment, or outcome claims.
"""

from __future__ import annotations

import itertools
import json
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
SOURCE = "https://arxiv.org/abs/2402.10232"


@dataclass(frozen=True)
class ProjectionCase:
    case_id: str
    label: str
    model: str
    input_dim: int
    projected_dim: int
    distortion_budget: float
    privacy_noise: float
    source_shift: bool
    clinical_claim_requested: bool
    seed: int
    clinical_analogy: str


CASES = [
    ProjectionCase(
        case_id="J01",
        label="Gaussian JL geometry audit",
        model="gaussian",
        input_dim=36,
        projected_dim=24,
        distortion_budget=0.45,
        privacy_noise=0.0,
        source_shift=False,
        clinical_claim_requested=False,
        seed=240210232,
        clinical_analogy="Compressed synthetic genetic-feature vectors preserve pairwise geometry for audit only.",
    ),
    ProjectionCase(
        case_id="J02",
        label="Rademacher sign JL geometry audit",
        model="rademacher",
        input_dim=36,
        projected_dim=24,
        distortion_budget=0.75,
        privacy_noise=0.0,
        source_shift=False,
        clinical_claim_requested=False,
        seed=240210233,
        clinical_analogy="Binary-sign projection preserves enough geometry for bounded source-population checks.",
    ),
    ProjectionCase(
        case_id="J03",
        label="Sparse sign projection under explicit scaling",
        model="sparse_sign",
        input_dim=36,
        projected_dim=30,
        distortion_budget=0.50,
        privacy_noise=0.0,
        source_shift=False,
        clinical_claim_requested=False,
        seed=240210234,
        clinical_analogy="Sparse projection can be useful when scaling and distortion are audited explicitly.",
    ),
    ProjectionCase(
        case_id="J04",
        label="Unscaled sign projection",
        model="unscaled_sign",
        input_dim=36,
        projected_dim=24,
        distortion_budget=0.45,
        privacy_noise=0.0,
        source_shift=False,
        clinical_claim_requested=False,
        seed=240210235,
        clinical_analogy="A crude embedding changes distance scale enough to break geometry-preservation claims.",
    ),
    ProjectionCase(
        case_id="J05",
        label="JL plus excessive privacy noise",
        model="gaussian",
        input_dim=36,
        projected_dim=24,
        distortion_budget=0.45,
        privacy_noise=0.35,
        source_shift=False,
        clinical_claim_requested=False,
        seed=240210236,
        clinical_analogy="Adding noise for privacy can destroy the geometry needed for subgroup auditing.",
    ),
    ProjectionCase(
        case_id="J06",
        label="Geometry preserved but source population shifted",
        model="gaussian",
        input_dim=36,
        projected_dim=24,
        distortion_budget=0.75,
        privacy_noise=0.0,
        source_shift=True,
        clinical_claim_requested=False,
        seed=240210237,
        clinical_analogy="Geometry preservation does not remove the need for source-population validation.",
    ),
    ProjectionCase(
        case_id="J07",
        label="Geometry preserved but clinical claim requested",
        model="rademacher",
        input_dim=36,
        projected_dim=24,
        distortion_budget=0.75,
        privacy_noise=0.0,
        source_shift=False,
        clinical_claim_requested=True,
        seed=240210238,
        clinical_analogy="A good embedding cannot turn method evidence into a diagnosis or outcome claim.",
    ),
]


def synthetic_points(n: int, d: int) -> list[list[float]]:
    points: list[list[float]] = []
    for i in range(n):
        row = []
        for j in range(d):
            row.append(
                math.sin((i + 1) * (j + 1) / 7.0)
                + 0.5 * math.cos((i + 3) * (j + 2) / 11.0)
                + (0.08 if (i + j) % 5 == 0 else -0.04)
            )
        points.append(row)
    return points


def projection_matrix(case: ProjectionCase) -> list[list[float]]:
    rng = random.Random(case.seed)
    m = case.projected_dim
    d = case.input_dim
    scale = 1.0 / math.sqrt(m)

    matrix: list[list[float]] = []
    for _ in range(m):
        row = []
        for _ in range(d):
            if case.model == "gaussian":
                value = rng.gauss(0.0, scale)
            elif case.model == "rademacher":
                value = scale * (1.0 if rng.random() < 0.5 else -1.0)
            elif case.model == "sparse_sign":
                draw = rng.random()
                if draw < 1.0 / 6.0:
                    value = math.sqrt(3.0) * scale
                elif draw < 1.0 / 3.0:
                    value = -math.sqrt(3.0) * scale
                else:
                    value = 0.0
            elif case.model == "unscaled_sign":
                value = 1.0 if rng.random() < 0.5 else -1.0
            else:
                raise ValueError(f"unknown projection model: {case.model}")
            row.append(value)
        matrix.append(row)
    return matrix


def project(points: list[list[float]], case: ProjectionCase) -> list[list[float]]:
    matrix = projection_matrix(case)
    rng = random.Random(case.seed + 10_000)
    out: list[list[float]] = []
    for point in points:
        row = []
        for weights in matrix:
            value = sum(w * x for w, x in zip(weights, point, strict=True))
            if case.privacy_noise:
                value += rng.gauss(0.0, case.privacy_noise)
            row.append(value)
        out.append(row)
    return out


def squared_distance(a: list[float], b: list[float]) -> float:
    return sum((x - y) ** 2 for x, y in zip(a, b, strict=True))


def max_pairwise_distortion(points: list[list[float]], projected: list[list[float]]) -> float:
    worst = 0.0
    for i, j in itertools.combinations(range(len(points)), 2):
        before = squared_distance(points[i], points[j])
        after = squared_distance(projected[i], projected[j])
        if before > 1e-12:
            worst = max(worst, abs(after / before - 1.0))
    return worst


def audit_case(case: ProjectionCase) -> dict[str, object]:
    points = synthetic_points(n=10, d=case.input_dim)
    projected = project(points, case)
    max_distortion = round(max_pairwise_distortion(points, projected), 4)
    geometry_preserved = max_distortion <= case.distortion_budget

    if not geometry_preserved:
        action = "BLOCK_GEOMETRY_CLAIM"
        reason = "The projection exceeded the explicit distortion budget."
    elif case.clinical_claim_requested:
        action = "ABSTAIN_CLINICAL_CLAIM"
        reason = "JL preservation is method evidence, not diagnosis or outcome validation."
    elif case.source_shift:
        action = "REQUIRE_SOURCE_POPULATION_AUDIT"
        reason = "Geometry preservation does not settle source-population transport."
    elif case.privacy_noise > 0:
        action = "REQUIRE_PRIVACY_GEOMETRY_TRADEOFF_AUDIT"
        reason = "Privacy noise must be audited against geometry preservation."
    else:
        action = "ALLOW_GEOMETRY_PRESERVATION_CLAIM"
        reason = "The bounded synthetic audit stayed within the distortion budget."

    return {
        **asdict(case),
        "max_pairwise_distortion": max_distortion,
        "geometry_preserved": geometry_preserved,
        "action": action,
        "reason": reason,
    }


def run() -> dict[str, object]:
    rows = [audit_case(case) for case in CASES]
    action_counts: dict[str, int] = {}
    for row in rows:
        action_counts[row["action"]] = action_counts.get(row["action"], 0) + 1

    summary = {
        "source": SOURCE,
        "case_count": len(rows),
        "action_counts": action_counts,
        "rows": rows,
        "capstone_interpretation": (
            "JL-style projection can support bounded geometry-preservation claims, "
            "but projection is not automatically privacy, source-population validity, "
            "or clinical-outcome evidence."
        ),
    }

    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "jl_projection_geometry_audit_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
