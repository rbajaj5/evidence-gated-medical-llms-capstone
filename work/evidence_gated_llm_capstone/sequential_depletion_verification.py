"""Numerical checks for the Sequential Depletion Ordering manuscript.

These tests support transcription/debugging only; the paper contains proofs.
Run with: python sequential_depletion_verification.py
"""

from __future__ import annotations

import itertools
import math
import random
from collections.abc import Sequence


def cost(order: Sequence[float], q: float) -> float:
    remaining = q + sum(order)
    total = 0.0
    for x in order:
        total += x / remaining
        remaining -= x
    return total


def log_shocks(order: Sequence[float], q: float) -> list[float]:
    if q <= 0:
        raise ValueError("q must be positive for log shocks")
    remaining = q + sum(order)
    out: list[float] = []
    for x in order:
        after = remaining - x
        out.append(math.log(remaining / after))
        remaining = after
    return out


def is_majorized_by(x: Sequence[float], y: Sequence[float], tol: float = 1e-10) -> bool:
    """Return True when x is majorized by y."""
    xs = sorted(x, reverse=True)
    ys = sorted(y, reverse=True)
    if abs(sum(xs) - sum(ys)) > tol:
        return False
    return all(sum(xs[:k]) <= sum(ys[:k]) + tol for k in range(1, len(xs)))


def swap_identity(a: float, b: float, tail: float) -> tuple[float, float]:
    lhs = a / (tail + a + b) + b / (tail + b)
    lhs -= b / (tail + a + b) + a / (tail + a)
    rhs = a * b * (a - b) / ((tail + a + b) * (tail + a) * (tail + b))
    return lhs, rhs


def check_random_deterministic(trials: int = 2_000) -> None:
    rng = random.Random(20260724)
    for _ in range(trials):
        n = rng.randint(2, 8)
        xs = [10 ** rng.uniform(-1.0, 1.0) for _ in range(n)]
        q = 10 ** rng.uniform(-1.0, 1.0)

        a, b = rng.sample(xs, 2)
        tail = 10 ** rng.uniform(-1.0, 1.0)
        lhs, rhs = swap_identity(a, b, tail)
        assert math.isclose(lhs, rhs, rel_tol=1e-11, abs_tol=1e-11)

        asc = sorted(xs)
        desc = sorted(xs, reverse=True)
        perm = rng.sample(xs, len(xs))
        assert cost(asc, q) <= cost(perm, q) + 1e-11
        assert cost(perm, q) <= cost(desc, q) + 1e-11

        d_asc = log_shocks(asc, q)
        d_desc = log_shocks(desc, q)
        d_perm = log_shocks(perm, q)
        assert is_majorized_by(d_desc, d_perm)
        assert is_majorized_by(d_perm, d_asc)


def precedence_counterexample() -> None:
    q = 1.0
    greedy = cost([7.0, 8.0, 2.0], q)  # B, A, C
    better = cost([8.0, 2.0, 7.0], q)  # A, C, B
    assert better < greedy
    print(f"Precedence example: greedy={greedy:.8f}, better={better:.8f}")


def network_delta(
    a: Sequence[float],
    b: Sequence[float],
    tail: Sequence[float],
    weights: Sequence[float] | None = None,
) -> float:
    if weights is None:
        weights = [1.0] * len(a)
    return sum(
        w * ar * br * (ar - br) / ((tr + ar + br) * (tr + ar) * (tr + br))
        for ar, br, tr, w in zip(a, b, tail, weights, strict=True)
    )


def network_context_reversal() -> None:
    a = (4.0, 1.0)
    b = (1.0, 3.0)
    d1 = network_delta(a, b, (1.0, 1.0))
    d2 = network_delta(a, b, (10.0, 1.0))
    assert d1 > 0 > d2
    print(f"Network reversal: delta(1,1)={d1:.8f}, delta(10,1)={d2:.8f}")


def mc_expected_cost(
    rates: Sequence[float], order: Sequence[int], q: float, samples: int, seed: int
) -> float:
    rng = random.Random(seed)
    total = 0.0
    for _ in range(samples):
        xs = [-math.log1p(-rng.random()) / rate for rate in rates]
        total += cost([xs[i] for i in order], q)
    return total / samples


def stochastic_exponential_check(samples: int = 300_000) -> None:
    # Larger exponential rate means a smaller variable in likelihood-ratio order.
    rates = (5.0, 2.0, 0.8)
    asc_lr = (0, 1, 2)
    rev = tuple(reversed(asc_lr))
    q = 1.0
    best = mc_expected_cost(rates, asc_lr, q, samples, seed=11)
    worst = mc_expected_cost(rates, rev, q, samples, seed=12)
    assert best < worst
    print(f"Exponential MC: LR-order={best:.8f}, reverse={worst:.8f}")


def exhaustive_small_instance() -> None:
    xs = (1.0, 2.0, 4.0, 9.0)
    q = 1.5
    scored = sorted((cost(p, q), p) for p in itertools.permutations(xs))
    assert scored[0][1] == tuple(sorted(xs))
    assert scored[-1][1] == tuple(sorted(xs, reverse=True))
    print(f"Exhaustive 4-item min={scored[0][0]:.8f}, max={scored[-1][0]:.8f}")


def main() -> None:
    check_random_deterministic()
    exhaustive_small_instance()
    precedence_counterexample()
    network_context_reversal()
    stochastic_exponential_check()
    print("All verification checks passed.")


if __name__ == "__main__":
    main()
