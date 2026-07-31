"""Proxy/mass counterexample audit for medical LLM assurance.

Inspired by Li and Xia's counterexample to the zero-mass conjecture, this
synthetic audit separates a vanishing local proxy from concentrated residual
mass. In the capstone setting, the warning is simple: a weak or zero proxy
signal should not be upgraded to "no clinically relevant residual risk" unless
the missing mass/risk channel is independently audited.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
SOURCE = "https://arxiv.org/abs/2607.26549"


@dataclass(frozen=True)
class ProxyMassCase:
    case_id: str
    label: str
    local_proxy: float
    residual_mass: float
    isolated_event: bool
    added_structure: bool
    directional_witness: bool
    monotone_limit: bool
    clinical_analogy: str


CASES = [
    ProxyMassCase(
        case_id="Z01",
        label="Vanishing proxy with concentrated residual mass",
        local_proxy=0.0,
        residual_mass=1.0,
        isolated_event=True,
        added_structure=False,
        directional_witness=True,
        monotone_limit=True,
        clinical_analogy="A local biomarker appears absent while residual event risk remains concentrated.",
    ),
    ProxyMassCase(
        case_id="Z02",
        label="Positive proxy forces positive residual channel",
        local_proxy=0.45,
        residual_mass=0.62,
        isolated_event=True,
        added_structure=False,
        directional_witness=False,
        monotone_limit=False,
        clinical_analogy="A strong warning signal correctly prevents a no-risk claim.",
    ),
    ProxyMassCase(
        case_id="Z03",
        label="Vanishing proxy with added regularity structure",
        local_proxy=0.0,
        residual_mass=0.0,
        isolated_event=True,
        added_structure=True,
        directional_witness=False,
        monotone_limit=False,
        clinical_analogy="Extra validated structure makes the proxy-to-risk implication safer.",
    ),
    ProxyMassCase(
        case_id="Z04",
        label="Low proxy with un-audited missing-mass channel",
        local_proxy=0.03,
        residual_mass=0.27,
        isolated_event=True,
        added_structure=False,
        directional_witness=False,
        monotone_limit=False,
        clinical_analogy="A near-zero score hides unresolved risk because no residual audit was run.",
    ),
    ProxyMassCase(
        case_id="Z05",
        label="No isolated event and low residual mass",
        local_proxy=0.0,
        residual_mass=0.02,
        isolated_event=False,
        added_structure=True,
        directional_witness=False,
        monotone_limit=False,
        clinical_analogy="The low proxy is supported by broader context and no concentrated failure mode.",
    ),
]


def audit_case(case: ProxyMassCase) -> dict[str, object]:
    if case.local_proxy == 0.0 and case.residual_mass > 0.25 and not case.added_structure:
        action = "BLOCK_ZERO_PROXY_TO_ZERO_RISK"
        reason = "A vanishing proxy does not exclude concentrated residual mass."
    elif case.residual_mass > 0.10 and case.local_proxy < 0.10:
        action = "REQUIRE_RESIDUAL_MASS_AUDIT"
        reason = "Residual mass remains material despite a weak proxy."
    elif case.local_proxy > 0.0 and case.residual_mass > 0.0:
        action = "ALLOW_POSITIVE_PROXY_WARNING"
        reason = "Positive proxy evidence supports warning, not reassurance."
    elif case.added_structure and case.residual_mass <= 0.05:
        action = "ALLOW_REASSURANCE_WITH_STRUCTURE"
        reason = "Reassurance is bounded by added structure and residual-mass audit."
    else:
        action = "ALLOW_LOW_RISK_ONLY_WITH_AUDIT"
        reason = "Low-risk language requires explicit residual audit, not proxy absence alone."

    return {
        **asdict(case),
        "proxy_mass_gap": round(case.residual_mass - case.local_proxy, 3),
        "counterexample_shape": (
            case.local_proxy == 0.0
            and case.residual_mass > 0.25
            and case.isolated_event
            and case.directional_witness
        ),
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
            "A vanishing local proxy cannot by itself authorize a no-risk or no-mass "
            "claim. Medical LLM monitors should require residual-risk audits before "
            "turning proxy absence into reassurance."
        ),
    }

    RESULTS.mkdir(exist_ok=True)
    (RESULTS / "proxy_mass_counterexample_audit_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
