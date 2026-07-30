"""Monte Carlo Hex scaling and coarse-graining stress tests.

This file extends the exact Hex boundary probe. The first audit samples larger
boards and confirms that terminal full boards still have exactly one crossing.
The second audit applies a generic local majority smoother and measures how
often that blurring flips the global crossing. The capstone use is methodological:
coarse-graining needs a boundary-preservation proof, not merely a plausible
local aggregation rule.
"""

from __future__ import annotations

import csv
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from hex_boundary_invariant_experiment import BLUE, YELLOW, classify_full_board, neighbors


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"


def random_board(n: int, blue_probability: float, rng: random.Random) -> tuple[int, ...]:
    return tuple(BLUE if rng.random() < blue_probability else YELLOW for _ in range(n * n))


def wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total <= 0:
        raise ValueError("total must be positive")
    phat = successes / total
    denom = 1.0 + z * z / total
    centre = (phat + z * z / (2 * total)) / denom
    radius = z * math.sqrt((phat * (1 - phat) + z * z / (4 * total)) / total) / denom
    return max(0.0, centre - radius), min(1.0, centre + radius)


def local_majority_smooth(board: tuple[int, ...], n: int) -> tuple[tuple[int, ...], int]:
    """Smooth by replacing each cell with the local majority.

    Ties preserve the original cell. This is intentionally a generic smoother,
    unlike the Y-board majority-triangle reduction with a boundary-preservation
    proof. Its failures are therefore informative.
    """

    out: list[int] = []
    tie_count = 0
    for r in range(n):
        for c in range(n):
            idx = r * n + c
            local = [board[idx]]
            local.extend(board[rr * n + cc] for rr, cc in neighbors((r, c), n))
            blue_count = sum(1 for value in local if value == BLUE)
            yellow_count = len(local) - blue_count
            if blue_count == yellow_count:
                tie_count += 1
                out.append(board[idx])
            elif blue_count > yellow_count:
                out.append(BLUE)
            else:
                out.append(YELLOW)
    return tuple(out), tie_count


def sample_crossing_rates(
    board_sizes: list[int],
    probabilities: list[float],
    samples_per_cell: int,
    rng: random.Random,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for n in board_sizes:
        for p in probabilities:
            counts = {"blue_only": 0, "yellow_only": 0, "both": 0, "neither": 0}
            for _ in range(samples_per_cell):
                board = random_board(n, p, rng)
                counts[classify_full_board(board, n)] += 1
            lo, hi = wilson_interval(counts["blue_only"], samples_per_cell)
            rows.append(
                {
                    "board_size": n,
                    "blue_probability": p,
                    "samples": samples_per_cell,
                    "blue_crossing_rate": counts["blue_only"] / samples_per_cell,
                    "yellow_crossing_rate": counts["yellow_only"] / samples_per_cell,
                    "both_crossing_count": counts["both"],
                    "neither_crossing_count": counts["neither"],
                    "blue_crossing_wilson_low": lo,
                    "blue_crossing_wilson_high": hi,
                }
            )
    return rows


def sample_smoothing_flip_rates(
    board_sizes: list[int],
    probabilities: list[float],
    samples_per_cell: int,
    rng: random.Random,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for n in board_sizes:
        for p in probabilities:
            flips = 0
            ties = 0
            blue_to_yellow = 0
            yellow_to_blue = 0
            for _ in range(samples_per_cell):
                board = random_board(n, p, rng)
                before = classify_full_board(board, n)
                smoothed, tie_count = local_majority_smooth(board, n)
                after = classify_full_board(smoothed, n)
                ties += tie_count
                if before != after:
                    flips += 1
                    if before == "blue_only":
                        blue_to_yellow += 1
                    elif before == "yellow_only":
                        yellow_to_blue += 1
            lo, hi = wilson_interval(flips, samples_per_cell)
            rows.append(
                {
                    "board_size": n,
                    "blue_probability": p,
                    "samples": samples_per_cell,
                    "coarse_grain_flip_rate": flips / samples_per_cell,
                    "coarse_grain_flip_count": flips,
                    "blue_to_yellow_flips": blue_to_yellow,
                    "yellow_to_blue_flips": yellow_to_blue,
                    "mean_local_ties_per_board": ties / samples_per_cell,
                    "flip_wilson_low": lo,
                    "flip_wilson_high": hi,
                }
            )
    return rows


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_results(crossing_rows: list[dict[str, object]], smoothing_rows: list[dict[str, object]]) -> Path:
    FIGURES.mkdir(parents=True, exist_ok=True)
    path = FIGURES / "hex_scaling_coarse_grain.png"

    image = Image.new("RGB", (1600, 620), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    colors = {
        0.45: (46, 116, 181),
        0.48: (46, 116, 181),
        0.50: (70, 140, 80),
        0.52: (217, 125, 49),
        0.55: (217, 125, 49),
    }

    def draw_panel(
        box: tuple[int, int, int, int],
        rows: list[dict[str, object]],
        y_key: str,
        title: str,
        y_label: str,
        y_max: float,
    ) -> None:
        left, top, right, bottom = box
        plot_left, plot_top, plot_right, plot_bottom = left + 80, top + 55, right - 25, bottom - 65
        draw.rectangle([left, top, right, bottom], outline=(210, 216, 224), width=1)
        draw.text((left + 18, top + 15), title, fill=(20, 35, 55), font=font)
        draw.text((plot_left, bottom - 38), "Hex board side length", fill=(40, 40, 40), font=font)
        draw.text((left + 12, plot_top - 25), y_label, fill=(40, 40, 40), font=font)
        draw.line([(plot_left, plot_bottom), (plot_right, plot_bottom)], fill=(50, 50, 50), width=2)
        draw.line([(plot_left, plot_top), (plot_left, plot_bottom)], fill=(50, 50, 50), width=2)

        sizes = sorted({int(row["board_size"]) for row in rows})
        probabilities = sorted({float(row["blue_probability"]) for row in rows})

        for tick in range(6):
            value = y_max * tick / 5
            y = plot_bottom - int((plot_bottom - plot_top) * value / y_max)
            draw.line([(plot_left, y), (plot_right, y)], fill=(235, 238, 242), width=1)
            draw.text((plot_left - 45, y - 6), f"{value:.2f}", fill=(80, 80, 80), font=font)

        for i, n in enumerate(sizes):
            x = plot_left + int((plot_right - plot_left) * i / max(1, len(sizes) - 1))
            draw.line([(x, plot_bottom), (x, plot_bottom + 5)], fill=(50, 50, 50), width=1)
            draw.text((x - 8, plot_bottom + 12), str(n), fill=(60, 60, 60), font=font)

        for p in probabilities:
            sub = [row for row in rows if float(row["blue_probability"]) == p]
            sub.sort(key=lambda row: int(row["board_size"]))
            points: list[tuple[int, int]] = []
            for row in sub:
                n = int(row["board_size"])
                x_index = sizes.index(n)
                x = plot_left + int((plot_right - plot_left) * x_index / max(1, len(sizes) - 1))
                y_val = float(row[y_key])
                y = plot_bottom - int((plot_bottom - plot_top) * y_val / y_max)
                points.append((x, y))
            color = colors.get(round(p, 2), (80, 80, 80))
            if len(points) > 1:
                draw.line(points, fill=color, width=4)
            for x, y in points:
                draw.ellipse([x - 5, y - 5, x + 5, y + 5], fill=color, outline="white", width=2)

        legend_x = plot_right - 115
        legend_y = plot_top + 8
        for offset, p in enumerate(probabilities):
            color = colors.get(round(p, 2), (80, 80, 80))
            y = legend_y + offset * 22
            draw.line([(legend_x, y + 6), (legend_x + 25, y + 6)], fill=color, width=4)
            draw.text((legend_x + 34, y), f"p={p:.2f}", fill=(40, 40, 40), font=font)

    draw.text(
        (470, 16),
        "Hex boundary scaling and coarse-graining stress test",
        fill=(20, 35, 55),
        font=font,
    )
    draw_panel(
        (30, 55, 780, 590),
        crossing_rows,
        "blue_crossing_rate",
        "Random full boards",
        "Blue left-right crossing rate",
        1.0,
    )
    draw_panel(
        (820, 55, 1570, 590),
        smoothing_rows,
        "coarse_grain_flip_rate",
        "Generic local smoothing",
        "Global crossing flip rate",
        max(0.08, max(float(row["coarse_grain_flip_rate"]) for row in smoothing_rows) * 1.25),
    )

    image.save(path)
    return path


def run(crossing_samples: int = 2000, smoothing_samples: int = 1000) -> dict[str, object]:
    rng = random.Random(20260730)
    crossing_rows = sample_crossing_rates(
        board_sizes=[5, 7, 9, 11, 13, 15],
        probabilities=[0.45, 0.50, 0.55],
        samples_per_cell=crossing_samples,
        rng=rng,
    )
    smoothing_rows = sample_smoothing_flip_rates(
        board_sizes=[7, 9, 11, 13, 15],
        probabilities=[0.48, 0.50, 0.52],
        samples_per_cell=smoothing_samples,
        rng=rng,
    )

    ambiguous_count = sum(int(row["both_crossing_count"]) + int(row["neither_crossing_count"]) for row in crossing_rows)
    assert ambiguous_count == 0
    assert any(int(row["coarse_grain_flip_count"]) > 0 for row in smoothing_rows)

    p50_rows = [row for row in crossing_rows if float(row["blue_probability"]) == 0.50]
    p50_mean = sum(float(row["blue_crossing_rate"]) for row in p50_rows) / len(p50_rows)
    max_flip = max(smoothing_rows, key=lambda row: float(row["coarse_grain_flip_rate"]))

    RESULTS.mkdir(parents=True, exist_ok=True)
    write_csv(RESULTS / "hex_scaling_crossing_rates.csv", crossing_rows)
    write_csv(RESULTS / "hex_scaling_smoothing_flip_rates.csv", smoothing_rows)
    figure_path = plot_results(crossing_rows, smoothing_rows)

    summary = {
        "experiment": "hex_scaling_coarse_grain_probe",
        "clinical_status": "synthetic mathematical analogy only",
        "gpu_status": "GPU visible through nvidia-smi, but current Python torch build reports CUDA unavailable; CPU Monte Carlo used.",
        "crossing_samples_per_setting": crossing_samples,
        "smoothing_samples_per_setting": smoothing_samples,
        "crossing_board_sizes": [5, 7, 9, 11, 13, 15],
        "smoothing_board_sizes": [7, 9, 11, 13, 15],
        "sampled_full_boards": len(crossing_rows) * crossing_samples,
        "sampled_smoothed_boards": len(smoothing_rows) * smoothing_samples,
        "ambiguous_terminal_count": ambiguous_count,
        "unbiased_blue_crossing_mean": p50_mean,
        "max_coarse_grain_flip_rate": max_flip["coarse_grain_flip_rate"],
        "max_coarse_grain_flip_setting": {
            "board_size": max_flip["board_size"],
            "blue_probability": max_flip["blue_probability"],
        },
        "crossing_rows": crossing_rows,
        "smoothing_rows": smoothing_rows,
        "figure": str(figure_path.relative_to(ROOT)).replace("\\", "/"),
        "runtime_interpretation": "Sampled larger full boards preserved no both/none terminal ambiguity, but generic local smoothing sometimes changed the global crossing. Boundary-preserving coarse-graining therefore needs an explicit invariant or monitor.",
    }
    (RESULTS / "hex_scaling_coarse_grain_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
