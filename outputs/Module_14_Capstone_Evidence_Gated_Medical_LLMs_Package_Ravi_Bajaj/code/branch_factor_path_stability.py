"""Branch-factor and Volterra path stability probe.

This synthetic probe translates the branch-factor/radial-system section of
Bourgade-Huang into runtime-assurance language. A transported claim must stay
on a declared branch: the path should not cross the real-axis branch cut, the
configuration should remain separated from collision diagonals, the leading
edge phase should have a positive real part, and the Volterra fixed-point
estimate should be contractive.

The BBGKY appendix motivates the collision-diagonal rule: pointwise identities
away from collisions do not automatically justify contact or near-collision
claims. This is a mathematical analogy only, not a clinical result.
"""

from __future__ import annotations

import csv
import json
import math
from cmath import exp, phase, sqrt
from dataclasses import asdict, dataclass
from pathlib import Path
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"


@dataclass(frozen=True)
class BranchCase:
    name: str
    z: tuple[complex, ...]
    sigma: tuple[int, ...]
    delta: float
    min_runtime_separation: float
    contraction_constant: float
    interpretation: str


CASES = (
    BranchCase(
        name="separated_multimodal_branch",
        z=(30 + 20j, 66 - 22j, -42 + 31j, 15 - 58j),
        sigma=(1, -1, 1, -1),
        delta=0.40,
        min_runtime_separation=12.0,
        contraction_constant=6.0,
        interpretation="A well-separated branch can be followed as an audit artifact without crossing the branch cut.",
    ),
    BranchCase(
        name="near_collision_family_population_branch",
        z=(1.0 + 0.03j, 1.06 - 0.04j, 1.12 + 0.02j, 1.18 - 0.03j),
        sigma=(1, -1, 1, -1),
        delta=0.40,
        min_runtime_separation=12.0,
        contraction_constant=6.0,
        interpretation="Near-collision/source-overlap case fails separation and contraction checks; it remains branch/transport audit only.",
    ),
)


def angular_distance(a: float, b: float) -> float:
    diff = abs((a - b + math.pi) % (2 * math.pi) - math.pi)
    return diff


def separation_scale(z: tuple[complex, ...]) -> float:
    distances = [abs(value) for value in z]
    distances.extend(abs(z[i] - z[j]) for i in range(len(z)) for j in range(i + 1, len(z)))
    return min(distances)


def in_admissible_sector(z: tuple[complex, ...], delta: float) -> bool:
    return all(abs(phase(value)) <= math.pi - delta and abs(value.imag) > 1e-12 for value in z)


def choose_sectorial_directions(case: BranchCase) -> tuple[complex, ...]:
    count = len(case.z)
    alpha = case.delta / 4.0
    kappa = alpha / (16.0 * count)
    lengths: list[float] = []
    for index in range(count):
        if index == 0:
            lengths.append(2.0)
        else:
            lengths.append(max(2.0, 2.1 * max(lengths) / math.sin(kappa)))

    omegas: list[complex] = []
    theta_values: list[float] = []
    for j, (zj, sigma_j) in enumerate(zip(case.z, case.sigma, strict=True)):
        sj = 1 if zj.imag > 0 else -1
        if -sigma_j * sj == 1:
            interval = (alpha / 2.0, alpha)
        else:
            interval = (-alpha, -alpha / 2.0)

        excluded = [phase(sigma_j * zj)]
        excluded.extend(phase(-sigma_j * (case.z[i] - zj)) for i in range(j))
        theta = None
        for step in range(1001):
            candidate = interval[0] + (interval[1] - interval[0]) * step / 1000.0
            if all(angular_distance(candidate, blocked) >= 3.0 * kappa for blocked in excluded):
                theta = candidate
                break
        if theta is None:
            theta = (interval[0] + interval[1]) / 2.0
        theta_values.append(theta)
        omegas.append(-sigma_j * lengths[j] * exp(1j * theta))
    return tuple(omegas)


def path_metrics(case: BranchCase) -> dict[str, object]:
    r0 = separation_scale(case.z)
    admissible = in_admissible_sector(case.z, case.delta) and r0 >= case.min_runtime_separation
    if not in_admissible_sector(case.z, case.delta):
        return {
            "r0": r0,
            "admissible_sector": False,
            "separation_passes": r0 >= case.min_runtime_separation,
            "path_samples": [],
            "min_sampled_separation_ratio": 0.0,
            "half_plane_preserved": False,
            "phase_gap_positive": False,
        }

    omegas = choose_sectorial_directions(case)
    lambdas = [r0, 1.5 * r0, 2.5 * r0, 4.0 * r0]
    path_samples = []
    min_ratio = float("inf")
    half_plane_preserved = True
    phase_gap_positive = True
    min_phase_margin = float("inf")

    for lam in lambdas:
        shifted = tuple(z + (lam - r0) * omega for z, omega in zip(case.z, omegas, strict=True))
        scale = separation_scale(shifted)
        min_ratio = min(min_ratio, scale / lam)
        for original, current, omega, sigma_i in zip(case.z, shifted, omegas, case.sigma, strict=True):
            half_plane_preserved = half_plane_preserved and (original.imag * current.imag > 0)
            margin = ((-sigma_i * omega) * sqrt(current)).real / math.sqrt(max(lam, 1e-12))
            min_phase_margin = min(min_phase_margin, margin)
            phase_gap_positive = phase_gap_positive and margin > 0
        path_samples.append(
            {
                "lambda": lam,
                "separation": scale,
                "separation_over_lambda": scale / lam,
            }
        )

    zeta0 = (2.0 / 3.0) * (r0 ** 1.5)
    contraction_ratio = case.contraction_constant / zeta0 if zeta0 > 0 else float("inf")
    return {
        "r0": r0,
        "admissible_sector": in_admissible_sector(case.z, case.delta),
        "separation_passes": r0 >= case.min_runtime_separation,
        "path_samples": path_samples,
        "min_sampled_separation_ratio": min_ratio,
        "half_plane_preserved": half_plane_preserved,
        "phase_gap_positive": phase_gap_positive,
        "min_scaled_phase_margin": min_phase_margin,
        "zeta0": zeta0,
        "volterra_contraction_ratio": contraction_ratio,
        "volterra_contractive": contraction_ratio < 1.0,
        "branch_path_passes": admissible and half_plane_preserved and phase_gap_positive and contraction_ratio < 1.0,
        "omegas": [[omega.real, omega.imag] for omega in omegas],
    }


def _font(size: int, bold: bool = False):
    filename = "arialbd.ttf" if bold else "arial.ttf"
    path = Path(r"C:\Windows\Fonts") / filename
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def _wrapped(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, width: int, font, fill) -> int:
    x, y = xy
    for line in wrap(text, width=max(18, width // 10)):
        draw.text((x, y), line, fill=fill, font=font)
        y += 25
    return y


def plot_branch_probe(rows: list[dict[str, object]]) -> Path:
    FIGURES.mkdir(parents=True, exist_ok=True)
    path = FIGURES / "branch_factor_path_stability.png"
    image = Image.new("RGB", (1800, 1050), "white")
    draw = ImageDraw.Draw(image)
    title = _font(40, True)
    h2 = _font(27, True)
    body = _font(22)
    small = _font(18)
    tiny = _font(16)

    navy = (25, 44, 68)
    teal = (45, 137, 128)
    red = (172, 67, 75)
    amber = (214, 144, 39)
    gray = (78, 86, 96)
    grid = (220, 226, 232)

    draw.text((70, 42), "Branch-Factor / Volterra Path Stability Probe", fill=navy, font=title)
    draw.text(
        (70, 96),
        "A transported artifact must stay on a declared branch: no branch-cut crossing, no collision collapse, positive phase gap, and contractive radial system.",
        fill=gray,
        font=body,
    )

    panel_x, panel_y, panel_w, panel_h = 85, 180, 810, 560
    draw.rectangle([panel_x, panel_y, panel_x + panel_w, panel_y + panel_h], outline=grid, width=2)
    draw.line([panel_x, panel_y + panel_h // 2, panel_x + panel_w, panel_y + panel_h // 2], fill=grid, width=2)
    draw.line([panel_x + panel_w // 2, panel_y, panel_x + panel_w // 2, panel_y + panel_h], fill=grid, width=2)
    draw.text((panel_x + 34, panel_y + 10), "complex branch plane", fill=gray, font=small)

    def project(value: complex) -> tuple[int, int]:
        # Compact nonlinear scaling keeps long proof-style rays visible.
        x = math.copysign(math.log1p(abs(value.real)), value.real)
        y = math.copysign(math.log1p(abs(value.imag)), value.imag)
        px, py = (
            panel_x + panel_w // 2 + int(x * 105),
            panel_y + panel_h // 2 - int(y * 105),
        )
        return (
            max(panel_x + 18, min(panel_x + panel_w - 18, px)),
            max(panel_y + 18, min(panel_y + panel_h - 18, py)),
        )

    stable_case = CASES[0]
    stable_omega = choose_sectorial_directions(stable_case)
    for z, omega in zip(stable_case.z, stable_omega, strict=True):
        start = project(z)
        dx = omega.real
        dy = -omega.imag
        norm = math.hypot(dx, dy) or 1.0
        arrow_len = 95
        end = (
            max(panel_x + 12, min(panel_x + panel_w - 12, start[0] + int(arrow_len * dx / norm))),
            max(panel_y + 12, min(panel_y + panel_h - 12, start[1] + int(arrow_len * dy / norm))),
        )
        draw.line([start, end], fill=teal, width=4)
        draw.ellipse([start[0] - 7, start[1] - 7, start[0] + 7, start[1] + 7], fill=teal)
        head_dx = end[0] - start[0]
        head_dy = end[1] - start[1]
        head_norm = math.hypot(head_dx, head_dy) or 1.0
        ux, uy = head_dx / head_norm, head_dy / head_norm
        px, py = -uy, ux
        draw.polygon(
            [
                end,
                (int(end[0] - 16 * ux + 7 * px), int(end[1] - 16 * uy + 7 * py)),
                (int(end[0] - 16 * ux - 7 * px), int(end[1] - 16 * uy - 7 * py)),
            ],
            fill=teal,
        )

    # Near-collision points, deliberately clustered.
    for z in CASES[1].z:
        p = project(z)
        draw.ellipse([p[0] - 7, p[1] - 7, p[0] + 7, p[1] + 7], fill=red)
    draw.text((panel_x + 20, panel_y + panel_h - 50), "red cluster = near collision / blocked branch", fill=red, font=small)

    table_x, table_y = 940, 190
    draw.text((table_x, table_y - 50), "Audit Outcomes", fill=navy, font=h2)
    col_w = [320, 130, 160, 210]
    headers = ["Case", "R0", "Contraction", "Action"]
    row_h = 80
    x = table_x
    for header, width in zip(headers, col_w, strict=True):
        draw.rectangle([x, table_y, x + width, table_y + row_h], fill=(239, 244, 247), outline=grid)
        draw.text((x + 12, table_y + 26), header, fill=navy, font=small)
        x += width
    for i, row in enumerate(rows, start=1):
        y = table_y + i * row_h
        x = table_x
        values = [
            row["name"].replace("_", " "),
            f"{row['r0']:.2f}",
            f"{row['volterra_contraction_ratio']:.2f}" if "volterra_contraction_ratio" in row else "blocked",
            row["runtime_action"].replace("_", " ").lower(),
        ]
        for value, width in zip(values, col_w, strict=True):
            draw.rectangle([x, y, x + width, y + row_h], fill="white", outline=grid)
            _wrapped(draw, (x + 12, y + 17), value, width - 24, tiny, gray)
            x += width

    draw.rounded_rectangle([980, 470, 1700, 715], radius=14, fill=(251, 246, 237), outline=amber, width=3)
    draw.text((1005, 495), "Runtime interpretation", fill=amber, font=h2)
    _wrapped(
        draw,
        (1005, 545),
        "The safe branch can be followed as a bounded audit object. The near-collision branch is blocked because pointwise-looking evidence near overlapping sources needs a distributional/contact-term audit.",
        665,
        body,
        navy,
    )
    draw.rounded_rectangle([980, 760, 1700, 920], radius=14, fill=(239, 247, 247), outline=teal, width=3)
    draw.text((1005, 785), "Gates", fill=teal, font=h2)
    _wrapped(
        draw,
        (1005, 835),
        "half-plane preservation; separation from collision diagonals; positive edge-phase gap; Volterra contraction; branch identifier preserved.",
        665,
        body,
        navy,
    )

    image.save(path)
    return path


def run() -> dict[str, object]:
    RESULTS.mkdir(parents=True, exist_ok=True)
    rows = []
    for case in CASES:
        metrics = path_metrics(case)
        branch_passes = bool(metrics.get("branch_path_passes", False))
        case_dict = asdict(case)
        case_dict["z"] = [[value.real, value.imag] for value in case.z]
        row = {
            **case_dict,
            **metrics,
            "runtime_action": "ALLOW_BRANCH_AUDIT_ARTIFACT" if branch_passes else "ABSTAIN_BRANCH_STABILITY",
            "hard_outcome_permission": False,
        }
        rows.append(row)

    figure = plot_branch_probe(rows)
    csv_path = RESULTS / "branch_factor_path_stability.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "name",
                "r0",
                "admissible_sector",
                "separation_passes",
                "half_plane_preserved",
                "phase_gap_positive",
                "volterra_contractive",
                "runtime_action",
            ]
        )
        for row in rows:
            writer.writerow(
                [
                    row["name"],
                    f"{row['r0']:.8f}",
                    row["admissible_sector"],
                    row["separation_passes"],
                    row["half_plane_preserved"],
                    row["phase_gap_positive"],
                    row.get("volterra_contractive", False),
                    row["runtime_action"],
                ]
            )

    stable = next(row for row in rows if row["name"] == "separated_multimodal_branch")
    near = next(row for row in rows if row["name"] == "near_collision_family_population_branch")
    summary = {
        "experiment": "branch_factor_path_stability_probe",
        "clinical_status": "synthetic mathematical analogy only",
        "source": "Bourgade-Huang branch factors, radial block system, Volterra contraction, and BBGKY contact/collision warning",
        "case_count": len(rows),
        "stable_branch_passes": stable["branch_path_passes"],
        "near_collision_branch_passes": near["branch_path_passes"],
        "stable_r0": stable["r0"],
        "near_collision_r0": near["r0"],
        "stable_min_separation_ratio": stable["min_sampled_separation_ratio"],
        "stable_min_scaled_phase_margin": stable["min_scaled_phase_margin"],
        "stable_volterra_contraction_ratio": stable["volterra_contraction_ratio"],
        "near_collision_separation_passes": near["separation_passes"],
        "hard_outcome_permission_count": sum(row["hard_outcome_permission"] for row in rows),
        "permission": "BRANCH_STABILITY_AUDIT_ONLY",
        "bbgky_collision_interpretation": (
            "Pointwise identities away from collision diagonals do not authorize contact or near-collision claims. "
            "Family-linked genomic overlap and clustered source populations should therefore trigger distributional or transport audit."
        ),
        "csv": str(csv_path.relative_to(ROOT)),
        "figure": str(figure.relative_to(ROOT)),
        "rows": rows,
    }
    (RESULTS / "branch_factor_path_stability_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
