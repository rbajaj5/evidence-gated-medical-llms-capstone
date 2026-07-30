"""Loop-equation/Gronwall runtime-stability probe.

Bourgade and Huang use local laws, integration-by-parts or switching calculus,
resolvent stability, cumulant-error estimates, and loop-equation hierarchies to
characterize universal random-matrix statistics. This file translates that
methodological pattern into a synthetic runtime-assurance check for medical LLM
claims: a claim may be portable only when a hierarchy of approximate invariants
has residuals small enough that Gronwall-style propagation remains within a
runtime budget.

This is a nonclinical mathematical analogy. It does not estimate a patient
outcome and does not simulate a real random matrix ensemble.
"""

from __future__ import annotations

import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"


@dataclass(frozen=True)
class RuntimeChain:
    name: str
    initial_error: float
    lipschitz: tuple[float, ...]
    residuals: tuple[float, ...]
    budget: float
    interpretation: str


REQUIRED_GATES = (
    "local_law_or_calibration",
    "integration_by_parts_or_switching_identity",
    "single_entry_stability",
    "cumulant_or_residual_error_bound",
    "gronwall_growth_budget",
    "source_population_context",
)


CHAINS = (
    RuntimeChain(
        name="stable_multimodal_transfer",
        initial_error=0.003,
        lipschitz=(0.05, 0.06, 0.04, 0.05, 0.04, 0.03),
        residuals=(0.002, 0.002, 0.003, 0.002, 0.002, 0.001),
        budget=0.050,
        interpretation="Small residuals remain inside the runtime budget after representation transfers.",
    ),
    RuntimeChain(
        name="unstable_missing_provenance_transfer",
        initial_error=0.010,
        lipschitz=(0.18, 0.22, 0.20, 0.18, 0.20, 0.16),
        residuals=(0.012, 0.016, 0.020, 0.018, 0.016, 0.014),
        budget=0.050,
        interpretation="Missing provenance and larger residuals exceed the budget even if each local step looks plausible.",
    ),
)


def discrete_gronwall_trace(chain: RuntimeChain) -> list[float]:
    error = chain.initial_error
    trace = [error]
    for lipschitz, residual in zip(chain.lipschitz, chain.residuals, strict=True):
        error = (1.0 + lipschitz) * error + residual
        trace.append(error)
    return trace


def exponential_gronwall_upper(chain: RuntimeChain) -> float:
    total_lipschitz = sum(chain.lipschitz)
    forcing = chain.initial_error + sum(chain.residuals)
    return math.exp(total_lipschitz) * forcing


def single_entry_resolvent_bound(
    n: int = 1_048_576, gamma: float = 0.05, constant: float = 1.0
) -> dict[str, float | int | bool]:
    # Lemma-style scale: single-entry perturbation is bounded by C N^-1/2 Lambda^3.
    lambda_bound = n**gamma
    perturbation_bound = constant * (n ** -0.5) * (lambda_bound**3)
    return {
        "n": n,
        "gamma": gamma,
        "lambda_bound": lambda_bound,
        "gamma_below_one_twelfth": gamma < (1.0 / 12.0),
        "single_entry_bound": perturbation_bound,
        "single_entry_budget": 0.010,
        "single_entry_stable": perturbation_bound < 0.010,
    }


def switching_cumulant_budget_check(
    n: int = 1_048_576, gamma: float = 0.05, moment_order: int = 4
) -> dict[str, float | int | bool | dict[str, float]]:
    """Check the proof-inspired cancellation/error budget for switching terms.

    The random d-regular excerpt separates three runtime duties: cancel the main
    quadratic term, make the rare bad event negligible, and keep replacement or
    product-rule errors small enough after summing sparse edge updates.
    """

    d = int(round(math.sqrt(n)))
    lambda_bound = n**gamma
    bad_event_probability = math.exp(-(math.log(n) ** 2))
    bad_event_expectation_bound = (n**moment_order) * bad_event_probability
    main_cancellation = {
        "positive_m2_term": 1.0,
        "negative_m2_term": -1.0,
        "net": 0.0,
    }
    replacement_error_scale = (lambda_bound**3) / math.sqrt(d)
    replacement_error_budget = 0.35
    derivative_error_exponent = -0.25 + 3.0 * gamma
    return {
        "n": n,
        "d": d,
        "gamma": gamma,
        "moment_order": moment_order,
        "lambda_bound": lambda_bound,
        "gamma_below_one_twelfth": gamma < (1.0 / 12.0),
        "bad_event_probability": bad_event_probability,
        "bad_event_expectation_bound": bad_event_expectation_bound,
        "bad_event_negligible": bad_event_expectation_bound < 1e-6,
        "main_cancellation": main_cancellation,
        "main_cancellation_passes": abs(main_cancellation["net"]) < 1e-12,
        "replacement_error_scale": replacement_error_scale,
        "replacement_error_budget": replacement_error_budget,
        "replacement_error_inside_budget": replacement_error_scale < replacement_error_budget,
        "derivative_error_exponent": derivative_error_exponent,
        "derivative_error_decays": derivative_error_exponent < 0.0,
        "requires_que_or_spatial_profile_gate": True,
    }


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    filename = "arialbd.ttf" if bold else "arial.ttf"
    path = Path(r"C:\Windows\Fonts") / filename
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def _wrapped_text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, width: int, font, fill) -> int:
    x, y = xy
    for line in wrap(text, width=max(18, width // 10)):
        draw.text((x, y), line, fill=fill, font=font)
        y += 25
    return y


def plot_loop_stability(chain_rows: list[dict[str, object]], single_entry: dict[str, object]) -> Path:
    FIGURES.mkdir(parents=True, exist_ok=True)
    path = FIGURES / "loop_equation_runtime_stability.png"
    image = Image.new("RGB", (1800, 1050), "white")
    draw = ImageDraw.Draw(image)
    title = _font(40, bold=True)
    h2 = _font(27, bold=True)
    body = _font(22)
    small = _font(18)

    navy = (23, 45, 70)
    teal = (43, 134, 126)
    red = (168, 65, 72)
    amber = (214, 143, 44)
    gray = (76, 84, 94)
    grid = (218, 226, 232)

    draw.text((70, 42), "Loop-Equation / Gronwall Runtime Stability Probe", fill=navy, font=title)
    draw.text(
        (70, 96),
        "Approximate invariant gates must remain stable under representation transfer before a claim can be transported.",
        fill=gray,
        font=body,
    )

    # Error traces.
    chart_x, chart_y, chart_w, chart_h = 90, 190, 980, 520
    draw.rectangle([chart_x, chart_y, chart_x + chart_w, chart_y + chart_h], outline=grid, width=2)
    for i in range(6):
        y = chart_y + i * chart_h // 5
        draw.line([chart_x, y, chart_x + chart_w, y], fill=grid, width=1)
    max_y = 0.18
    for row in chain_rows:
        trace = row["trace"]
        color = teal if row["passes_budget"] else red
        points = []
        for step, value in enumerate(trace):
            px = chart_x + int(step * chart_w / (len(trace) - 1))
            py = chart_y + chart_h - int(min(value, max_y) * chart_h / max_y)
            points.append((px, py))
        draw.line(points, fill=color, width=5)
        for point in points:
            draw.ellipse([point[0] - 6, point[1] - 6, point[0] + 6, point[1] + 6], fill=color)
    budget_y = chart_y + chart_h - int(0.05 * chart_h / max_y)
    draw.line([chart_x, budget_y, chart_x + chart_w, budget_y], fill=amber, width=4)
    draw.text((chart_x + chart_w - 180, budget_y - 32), "runtime budget", fill=amber, font=small)
    draw.text((chart_x, chart_y + chart_h + 22), "Representation-transfer step", fill=gray, font=body)
    draw.text((chart_x + 10, chart_y + 12), "Error / residual bound", fill=gray, font=body)

    # Gate stack.
    stack_x, stack_y = 1140, 190
    draw.text((stack_x, stack_y - 48), "Required Hierarchy", fill=navy, font=h2)
    gate_h = 58
    for idx, gate in enumerate(REQUIRED_GATES):
        y = stack_y + idx * (gate_h + 12)
        draw.rounded_rectangle([stack_x, y, stack_x + 570, y + gate_h], radius=10, fill=(241, 247, 247), outline=teal, width=2)
        draw.text((stack_x + 18, y + 17), gate.replace("_", " "), fill=navy, font=small)

    draw.rounded_rectangle([1140, 690, 1710, 895], radius=14, fill=(252, 245, 234), outline=amber, width=3)
    draw.text((1162, 715), "Single-entry stability", fill=amber, font=h2)
    _wrapped_text(
        draw,
        (1162, 765),
        f"N={single_entry['n']}, gamma={single_entry['gamma']:.2f}, bound={single_entry['single_entry_bound']:.4f}, budget={single_entry['single_entry_budget']:.3f}.",
        520,
        body,
        navy,
    )
    _wrapped_text(
        draw,
        (1162, 840),
        "Small perturbations are auditably stable here; larger local-law failures remain blocked.",
        520,
        small,
        gray,
    )

    draw.text((90, 790), "Interpretation", fill=navy, font=h2)
    _wrapped_text(
        draw,
        (90, 835),
        "The stable chain can remain a bounded audit artifact. The unstable chain is not denied because one local artifact looks bad; it is blocked because residuals amplify past the runtime budget.",
        960,
        body,
        gray,
    )
    image.save(path)
    return path


def run() -> dict[str, object]:
    RESULTS.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    for chain in CHAINS:
        trace = discrete_gronwall_trace(chain)
        upper = exponential_gronwall_upper(chain)
        rows.append(
            {
                **asdict(chain),
                "trace": trace,
                "final_error": trace[-1],
                "exponential_gronwall_upper": upper,
                "passes_budget": trace[-1] <= chain.budget,
                "upper_passes_budget": upper <= chain.budget,
                "runtime_action": "ALLOW_AUDIT_ARTIFACT" if trace[-1] <= chain.budget else "ABSTAIN_STABILITY",
            }
        )

    single_entry = single_entry_resolvent_bound()
    cumulant_budget = switching_cumulant_budget_check()
    figure = plot_loop_stability(rows, single_entry)

    csv_path = RESULTS / "loop_equation_runtime_stability.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "final_error", "budget", "passes_budget", "exponential_upper", "runtime_action"])
        for row in rows:
            writer.writerow(
                [
                    row["name"],
                    f"{row['final_error']:.8f}",
                    row["budget"],
                    row["passes_budget"],
                    f"{row['exponential_gronwall_upper']:.8f}",
                    row["runtime_action"],
                ]
            )

    summary = {
        "experiment": "loop_equation_runtime_stability_probe",
        "clinical_status": "synthetic mathematical analogy only",
        "source": "Bourgade-Huang loop-equation characterization, Gronwall/resolvent-stability/switching-calculus excerpts",
        "required_gate_count": len(REQUIRED_GATES),
        "required_gates": list(REQUIRED_GATES),
        "chain_count": len(rows),
        "stable_chain_passes": rows[0]["passes_budget"],
        "unstable_chain_passes": rows[1]["passes_budget"],
        "stable_final_error": rows[0]["final_error"],
        "unstable_final_error": rows[1]["final_error"],
        "stable_budget": rows[0]["budget"],
        "unstable_budget": rows[1]["budget"],
        "single_entry": single_entry,
        "cumulant_budget": cumulant_budget,
        "permission": "UNIVERSALITY_AUDIT_ONLY",
        "switching_calculus_interpretation": (
            "For sparse network-like inputs, local switching or edge updates should be treated as a perturbation audit. "
            "A model cannot transport a claim across source populations unless local-law, perturbation, and residual gates pass."
        ),
        "csv": str(csv_path.relative_to(ROOT)),
        "figure": str(figure.relative_to(ROOT)),
        "rows": rows,
    }
    (RESULTS / "loop_equation_runtime_stability_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
