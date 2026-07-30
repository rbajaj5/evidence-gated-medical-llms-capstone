"""Hex-style boundary invariant probe for runtime assurance.

Karlin and Peres use Hex to illustrate a progressively bounded partisan game
with no ties: a full standard board has exactly one monochromatic crossing.
This file turns that idea into a tiny finite audit. The clinical analogy is that
a runtime monitor should not allow terminal states that are both "safe" and
"unsafe," or neither classified, after all required evidence features are known.
"""

from __future__ import annotations

import functools
import itertools
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"

BLUE = 1
YELLOW = 0
EMPTY = -1


def neighbors(cell: tuple[int, int], n: int) -> list[tuple[int, int]]:
    r, c = cell
    candidates = [
        (r - 1, c),
        (r + 1, c),
        (r, c - 1),
        (r, c + 1),
        (r - 1, c + 1),
        (r + 1, c - 1),
    ]
    return [(rr, cc) for rr, cc in candidates if 0 <= rr < n and 0 <= cc < n]


def has_crossing(board: tuple[int, ...], n: int, color: int) -> bool:
    def value(r: int, c: int) -> int:
        return board[r * n + c]

    if color == BLUE:
        start = [(r, 0) for r in range(n) if value(r, 0) == BLUE]
        is_target = lambda cell: cell[1] == n - 1
    else:
        start = [(0, c) for c in range(n) if value(0, c) == YELLOW]
        is_target = lambda cell: cell[0] == n - 1

    seen = set(start)
    stack = list(start)
    while stack:
        cell = stack.pop()
        if is_target(cell):
            return True
        for nxt in neighbors(cell, n):
            if nxt not in seen and value(*nxt) == color:
                seen.add(nxt)
                stack.append(nxt)
    return False


def classify_full_board(board: tuple[int, ...], n: int) -> str:
    blue = has_crossing(board, n, BLUE)
    yellow = has_crossing(board, n, YELLOW)
    if blue and yellow:
        return "both"
    if blue:
        return "blue_only"
    if yellow:
        return "yellow_only"
    return "neither"


def enumerate_full_boards(n: int) -> dict[str, int]:
    counts = {"blue_only": 0, "yellow_only": 0, "both": 0, "neither": 0}
    for bits in itertools.product((YELLOW, BLUE), repeat=n * n):
        counts[classify_full_board(tuple(bits), n)] += 1
    return counts


def first_player_wins(n: int) -> bool:
    @functools.lru_cache(maxsize=None)
    def solve(board: tuple[int, ...], turn: int) -> bool:
        if has_crossing(board, n, BLUE):
            return True
        if has_crossing(board, n, YELLOW):
            return False
        empties = [i for i, value in enumerate(board) if value == EMPTY]
        if not empties:
            return False
        if turn == BLUE:
            return any(solve(board[:i] + (BLUE,) + board[i + 1 :], YELLOW) for i in empties)
        return all(solve(board[:i] + (YELLOW,) + board[i + 1 :], BLUE) for i in empties)

    return solve((EMPTY,) * (n * n), BLUE)


def majority_triangle_summary() -> dict[str, object]:
    counts = {BLUE: 0, YELLOW: 0}
    tie_count = 0
    for triple in itertools.product((YELLOW, BLUE), repeat=3):
        blue_count = sum(1 for item in triple if item == BLUE)
        yellow_count = 3 - blue_count
        if blue_count == yellow_count:
            tie_count += 1
        majority = BLUE if blue_count > yellow_count else YELLOW
        counts[majority] += 1
    return {
        "patterns": 8,
        "tie_count": tie_count,
        "blue_majority_patterns": counts[BLUE],
        "yellow_majority_patterns": counts[YELLOW],
        "odd_local_aggregation": True,
    }


def run() -> dict[str, object]:
    board_sizes = [1, 2, 3, 4]
    enumeration = {}
    for n in board_sizes:
        counts = enumerate_full_boards(n)
        total = sum(counts.values())
        assert total == 2 ** (n * n)
        assert counts["both"] == 0
        assert counts["neither"] == 0
        enumeration[str(n)] = {"total_full_boards": total, **counts}

    minimax_sizes = [1, 2, 3]
    minimax = {str(n): first_player_wins(n) for n in minimax_sizes}
    assert all(minimax.values())
    majority = majority_triangle_summary()
    assert majority["tie_count"] == 0

    total_full_boards = sum(item["total_full_boards"] for item in enumeration.values())
    summary = {
        "experiment": "hex_boundary_invariant_probe",
        "clinical_status": "synthetic mathematical analogy only",
        "board_sizes_enumerated": board_sizes,
        "total_full_boards_enumerated": total_full_boards,
        "both_crossing_count": sum(item["both"] for item in enumeration.values()),
        "neither_crossing_count": sum(item["neither"] for item in enumeration.values()),
        "exactly_one_crossing_all_full_boards": True,
        "first_player_win_sizes_checked": minimax_sizes,
        "first_player_wins_all_checked": all(minimax.values()),
        "enumeration_by_size": enumeration,
        "minimax_by_size": minimax,
        "majority_triangle_summary": majority,
        "runtime_interpretation": "Terminal runtime states should be designed to avoid both/none safety classifications; hidden extra moves favor the acting agent and should be logged.",
        "coarse_graining_interpretation": "The Y-game majority-triangle reduction is a model for safe coarse-graining: local blurring is acceptable only when it preserves the global boundary property being audited.",
    }
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / "hex_boundary_invariant_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
