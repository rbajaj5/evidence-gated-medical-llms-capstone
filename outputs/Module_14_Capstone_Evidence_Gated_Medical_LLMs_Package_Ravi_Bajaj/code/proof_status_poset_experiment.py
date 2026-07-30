"""Proof-status and provenance poset for evidence-gated medical LLMs.

The NIETTU stress case is useful only if it stays bounded: source existence,
mathematical ambition, and proof status are not the same evidentiary currency
as clinical validation. This finite audit models that rule as a graded poset of
evidence dimensions and checks that nonclinical source/proof upgrades cannot
be promoted into patient-outcome permission.
"""

from __future__ import annotations

import csv
import itertools
import json
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"


DIMENSIONS = {
    "source_status": ["missing", "artifact_exists", "archived_or_indexed", "peer_reviewed_or_guideline"],
    "validation_status": ["none", "hypothesis_or_conjecture", "formal_or_internal_validation", "clinical_validation"],
    "domain_relevance": ["nonmedical", "methodological_analogy", "biomedical_mechanism", "clinical_workflow"],
    "endpoint_status": ["none", "technical_or_surrogate", "validated_surrogate", "hard_patient_outcome"],
    "transport_context": ["unknown", "source_only", "plausible_transfer", "target_context_matched"],
    "authority_boundary": ["missing", "audit_only", "clinician_retained", "clinician_retained_with_governance"],
}

DIMENSION_NAMES = tuple(DIMENSIONS)
LEVEL_COUNT = 4


@dataclass(frozen=True)
class ArtifactCase:
    name: str
    state: tuple[int, ...]
    expected_permission: str
    interpretation: str


def state_dict(state: tuple[int, ...]) -> dict[str, str]:
    return {name: DIMENSIONS[name][state[index]] for index, name in enumerate(DIMENSION_NAMES)}


def rank(state: tuple[int, ...]) -> int:
    return sum(state)


def permission(state: tuple[int, ...]) -> str:
    source, validation, domain, endpoint, transport, authority = state
    if source == 0:
        return "deny_no_source"
    if (
        source >= 2
        and validation >= 3
        and domain >= 3
        and endpoint >= 3
        and transport >= 3
        and authority >= 2
    ):
        return "hard_outcome_allowed_with_caveats"
    if (
        source >= 2
        and validation >= 2
        and domain >= 2
        and endpoint >= 2
        and transport >= 2
        and authority >= 2
    ):
        return "validated_surrogate_or_guideline_support_only"
    if source >= 1 and domain >= 1 and endpoint >= 1 and authority >= 1:
        return "surrogate_or_method_claim_only"
    return "proof_status_or_provenance_audit_only"


def all_states() -> list[tuple[int, ...]]:
    return list(itertools.product(range(LEVEL_COUNT), repeat=len(DIMENSION_NAMES)))


def cover_transitions(states: list[tuple[int, ...]]) -> list[tuple[tuple[int, ...], tuple[int, ...], str]]:
    out: list[tuple[tuple[int, ...], tuple[int, ...], str]] = []
    for state in states:
        for index, name in enumerate(DIMENSION_NAMES):
            if state[index] < LEVEL_COUNT - 1:
                nxt = list(state)
                nxt[index] += 1
                out.append((state, tuple(nxt), name))
    return out


def artifact_cases() -> list[ArtifactCase]:
    return [
        ArtifactCase(
            name="NIETTU topological theory record",
            state=(2, 1, 1, 0, 0, 1),
            expected_permission="proof_status_or_provenance_audit_only",
            interpretation="Real archived/forthcoming source object; not medical validation.",
        ),
        ArtifactCase(
            name="Karlin-Peres Hex/Y theorem",
            state=(3, 2, 1, 0, 1, 1),
            expected_permission="proof_status_or_provenance_audit_only",
            interpretation="Formal mathematical analogy for boundary invariants; not clinical evidence.",
        ),
        ArtifactCase(
            name="Byrne-style pragmatic patient-outcome RCT",
            state=(3, 3, 3, 3, 3, 2),
            expected_permission="hard_outcome_allowed_with_caveats",
            interpretation="Clinical permission only when source, endpoint, design, context, and authority all align.",
        ),
        ArtifactCase(
            name="Hospital genetics guideline support",
            state=(3, 2, 3, 2, 2, 3),
            expected_permission="validated_surrogate_or_guideline_support_only",
            interpretation="Guideline-backed genetics support can route/triage but is not automatically a patient-outcome claim.",
        ),
        ArtifactCase(
            name="Synthetic audio/captioning benchmark",
            state=(1, 2, 1, 1, 1, 1),
            expected_permission="surrogate_or_method_claim_only",
            interpretation="Technical metric can support a method claim only.",
        ),
        ArtifactCase(
            name="KAN architecture critical assessment",
            state=(2, 2, 1, 1, 1, 1),
            expected_permission="surrogate_or_method_claim_only",
            interpretation="Architecture benchmark evidence can support model-selection discipline only.",
        ),
        ArtifactCase(
            name="Jaffe-Liu picture language program",
            state=(2, 2, 1, 0, 1, 1),
            expected_permission="proof_status_or_provenance_audit_only",
            interpretation="Picture-language simulation requires an explicit map before clinical claim use.",
        ),
    ]


def upgrade_only_source_or_validation(state: tuple[int, ...]) -> list[tuple[int, ...]]:
    source, validation, domain, endpoint, transport, authority = state
    out = []
    for next_source in range(source, LEVEL_COUNT):
        for next_validation in range(validation, LEVEL_COUNT):
            out.append((next_source, next_validation, domain, endpoint, transport, authority))
    return out


def plot_permission_distribution(permission_counts: dict[str, int], artifact_rows: list[dict[str, str]]) -> Path:
    FIGURES.mkdir(parents=True, exist_ok=True)
    path = FIGURES / "proof_status_poset_permissions.png"
    image = Image.new("RGB", (1800, 1000), "white")
    draw = ImageDraw.Draw(image)
    font_path = Path(r"C:\Windows\Fonts\arial.ttf")
    bold_path = Path(r"C:\Windows\Fonts\arialbd.ttf")
    font = ImageFont.truetype(str(font_path), 24) if font_path.exists() else ImageFont.load_default()
    small = ImageFont.truetype(str(font_path), 20) if font_path.exists() else ImageFont.load_default()
    tiny = ImageFont.truetype(str(font_path), 18) if font_path.exists() else ImageFont.load_default()
    title_font = ImageFont.truetype(str(bold_path), 34) if bold_path.exists() else font

    draw.text((50, 34), "Proof-Status / Provenance Poset Audit", fill=(20, 35, 55), font=title_font)
    draw.text(
        (50, 88),
        "Source existence, proof status, and mathematical analogy cannot upgrade into clinical-outcome permission without clinical dimensions.",
        fill=(55, 55, 55),
        font=small,
    )

    ordered_permissions = {
        "deny_no_source": "Deny: no source",
        "proof_status_or_provenance_audit_only": "Audit only: proof/provenance",
        "surrogate_or_method_claim_only": "Surrogate or method claim only",
        "validated_surrogate_or_guideline_support_only": "Validated surrogate / guideline support",
        "hard_outcome_allowed_with_caveats": "Hard outcome allowed with caveats",
    }
    colors = {
        "deny_no_source": (150, 45, 55),
        "proof_status_or_provenance_audit_only": (90, 110, 135),
        "surrogate_or_method_claim_only": (217, 125, 49),
        "validated_surrogate_or_guideline_support_only": (64, 135, 96),
        "hard_outcome_allowed_with_caveats": (46, 116, 181),
    }

    left, top, right = 90, 175, 880
    max_count = max(permission_counts.values())
    bar_h = 56
    for i, (key, label) in enumerate(ordered_permissions.items()):
        y = top + i * 94
        count = permission_counts.get(key, 0)
        width = max(3, int((right - left - 180) * count / max_count))
        draw.rounded_rectangle([left, y, left + width, y + bar_h], radius=5, fill=colors[key])
        draw.text((left + width + 16, y + 14), f"{count}", fill=(30, 30, 30), font=small)
        draw.text((left, y + bar_h + 8), label, fill=(40, 40, 40), font=small)

    table_x, table_y = 970, 175
    draw.text((table_x, table_y - 45), "Representative Artifacts", fill=(20, 35, 55), font=title_font)
    headers = ["Artifact", "Permission"]
    col_w = [440, 330]
    row_h = 74
    draw.rectangle([table_x, table_y, table_x + sum(col_w), table_y + row_h], outline=(180, 185, 195), width=1)
    x = table_x
    for j, header in enumerate(headers):
        draw.rectangle([x, table_y, x + col_w[j], table_y + row_h], fill=(244, 246, 249), outline=(180, 185, 195))
        draw.text((x + 16, table_y + 24), header, fill=(20, 35, 55), font=small)
        x += col_w[j]
    for i, row in enumerate(artifact_rows):
        y = table_y + row_h * (i + 1)
        x = table_x
        permission_label = ordered_permissions.get(row["permission"], row["permission"])
        for j, value in enumerate([row["name"], permission_label]):
            draw.rectangle([x, y, x + col_w[j], y + row_h], outline=(210, 216, 224), width=1)
            text = value[:48] + ("..." if len(value) > 48 else "")
            draw.text((x + 16, y + 24), text, fill=(40, 40, 40), font=tiny)
            x += col_w[j]

    draw.text(
        (90, 820),
        "Invariant: a nonclinical or endpoint-free state remains audit-only under source/proof upgrades.",
        fill=(20, 35, 55),
        font=small,
    )
    draw.text(
        (90, 855),
        "Clinical permission is a meet of several dimensions, not a consequence of one impressive source object.",
        fill=(55, 55, 55),
        font=small,
    )
    image.save(path)
    return path


def run() -> dict[str, object]:
    states = all_states()
    transitions = cover_transitions(states)
    permission_counts: dict[str, int] = {}
    for state in states:
        key = permission(state)
        permission_counts[key] = permission_counts.get(key, 0) + 1

    nonclinical_hard_states = [
        state
        for state in states
        if permission(state) == "hard_outcome_allowed_with_caveats"
        and (state[2] < 3 or state[3] < 3 or state[4] < 3 or state[5] < 2)
    ]
    endpoint_free_promotions = [
        state
        for state in states
        if state[3] == 0
        and permission(state)
        not in {"deny_no_source", "proof_status_or_provenance_audit_only"}
    ]
    method_only_hard_states = [
        state for state in states if state[2] <= 1 and permission(state) == "hard_outcome_allowed_with_caveats"
    ]

    artifact_rows: list[dict[str, str]] = []
    for case in artifact_cases():
        actual = permission(case.state)
        assert actual == case.expected_permission
        artifact_rows.append(
            {
                "name": case.name,
                "rank": str(rank(case.state)),
                "permission": actual,
                "expected_permission": case.expected_permission,
                "matches_expected": str(actual == case.expected_permission),
                "interpretation": case.interpretation,
                **state_dict(case.state),
            }
        )

    niettu = next(case for case in artifact_cases() if case.name.startswith("NIETTU"))
    niettu_source_proof_upgrades = upgrade_only_source_or_validation(niettu.state)
    niettu_upgrade_permissions = sorted({permission(state) for state in niettu_source_proof_upgrades})
    assert niettu_upgrade_permissions == ["proof_status_or_provenance_audit_only"]

    cover_into_hard = [
        {"changed_dimension": changed, "from_rank": rank(before), "to_rank": rank(after)}
        for before, after, changed in transitions
        if permission(before) != "hard_outcome_allowed_with_caveats"
        and permission(after) == "hard_outcome_allowed_with_caveats"
    ]

    assert len(nonclinical_hard_states) == 0
    assert len(endpoint_free_promotions) == 0
    assert len(method_only_hard_states) == 0

    RESULTS.mkdir(parents=True, exist_ok=True)
    FIGURES.mkdir(parents=True, exist_ok=True)
    csv_path = RESULTS / "proof_status_poset_artifacts.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(artifact_rows[0].keys()))
        writer.writeheader()
        writer.writerows(artifact_rows)

    figure_path = plot_permission_distribution(permission_counts, artifact_rows)

    summary = {
        "experiment": "proof_status_poset_probe",
        "clinical_status": "synthetic methodological audit only",
        "dimension_names": list(DIMENSION_NAMES),
        "states_enumerated": len(states),
        "cover_transitions_enumerated": len(transitions),
        "permission_counts": permission_counts,
        "nonclinical_hard_state_count": len(nonclinical_hard_states),
        "endpoint_free_promotion_count": len(endpoint_free_promotions),
        "method_only_hard_state_count": len(method_only_hard_states),
        "niettu_permission": permission(niettu.state),
        "niettu_source_proof_upgrade_permissions": niettu_upgrade_permissions,
        "artifact_rows": artifact_rows,
        "cover_transitions_into_hard_count": len(cover_into_hard),
        "cover_transitions_into_hard_changed_dimensions": sorted(
            {item["changed_dimension"] for item in cover_into_hard}
        ),
        "figure": str(figure_path.relative_to(ROOT)).replace("\\", "/"),
        "runtime_interpretation": (
            "The permission map is a graded evidence poset. Source/proof upgrades are not exchangeable for "
            "clinical endpoint, population/context, or authority upgrades. NIETTU remains audit-only under "
            "source/proof strengthening because it has no clinical endpoint."
        ),
    }
    (RESULTS / "proof_status_poset_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
