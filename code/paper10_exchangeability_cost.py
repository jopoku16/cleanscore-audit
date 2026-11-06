"""What the randomization test's exactness costs when forms are not exchangeable.

Proposition 6's test is exact under the sharp null that a parent's forms are
exchangeable for the model. That null is joint: it says there is no contamination
AND no ordinary form mismatch. The paper measures form mismatch separately with
the control banks and finds it small but not zero, so the sharp null is not quite
true even for a clean model, and a rejection cannot be read as contamination on
its own.

This quantifies the gap rather than conceding it in prose. For a model with no
contamination at all, and a fresh-form penalty of size b, it reports how often
the test rejects at the nominal level. b = 0 recovers the exactness the paper
reports; the largest b measured on any control bank says how far from exact the
test can be in the regime this audit actually operated in.

Nothing here changes a reported number. It is a property of the procedure, added
in revision after a reviewer pointed out that the section claimed more than the
test delivers.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SEED = 20260827
ALPHA = 0.05
DRAWS = 2000          # randomization draws per audit
AUDITS = 4000         # simulated audits per setting
FORMS = 3             # one public form and two fresh forms


def randomization_p(matrix: np.ndarray, rng: np.random.Generator) -> float:
    """One-sided p-value for the public form scoring above its own fresh forms."""
    n, k = matrix.shape
    total = matrix.sum(axis=1)
    observed = float((matrix[:, 0] - (total - matrix[:, 0]) / (k - 1)).mean())
    labels = rng.integers(0, k, size=(DRAWS, n))
    chosen = matrix[np.arange(n), labels]
    null = (chosen - (total - chosen) / (k - 1)).mean(axis=1)
    return (int((null >= observed - 1e-12).sum()) + 1) / (DRAWS + 1)


def simulate(n: int, b: float, base: float, rng: np.random.Generator) -> float:
    """Rejection rate with no contamination and a fresh-form penalty of size b.

    Parent difficulty is drawn per parent so that forms of the same item are
    correlated, which is what makes the paired design worth having and what a
    naive independent-Bernoulli simulation would miss.
    """
    rejects = 0
    for _ in range(AUDITS):
        # Beta centred on the observed accuracy, spread wide enough to give a
        # realistic mixture of easy, hard and borderline items.
        theta = rng.beta(2.0 * base / (1 - base) if base < 1 else 2.0, 2.0, size=n)
        theta = np.clip(theta * (base / theta.mean()), 0.0, 1.0)
        public = (rng.random(n) < np.clip(theta + b, 0, 1)).astype(float)
        fresh = (rng.random((n, FORMS - 1)) < theta[:, None]).astype(float)
        matrix = np.column_stack([public, fresh])
        if randomization_p(matrix, rng) < ALPHA:
            rejects += 1
    return rejects / AUDITS


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=ROOT / "results" / "randomization")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    # b = 0 is the exact case the paper reports. 0.0875 is the largest form gap
    # measured on any control bank in Table 3, so it is the worst case this
    # audit actually saw rather than an invented one.
    settings = [(200, b, 0.55) for b in (0.0, 0.02, 0.05, 0.0875)]
    rows = []
    print(f"no contamination, {AUDITS} audits per setting, nominal level {ALPHA}\n")
    print(f"{'n':>5} {'form gap b':>11} {'rejection rate':>15}")
    for n, b, base in settings:
        rate = simulate(n, b, base, rng)
        rows.append({"n": n, "form_gap": b, "base_accuracy": base,
                     "rejection_rate": round(rate, 4)})
        print(f"{n:5d} {b:11.4f} {rate:15.4f}")

    (args.out / "exchangeability_cost.json").write_text(
        json.dumps({"alpha": ALPHA, "audits_per_setting": AUDITS,
                    "note": "no contamination is present in any setting; every "
                            "rejection is caused by form mismatch alone",
                    "settings": rows}, indent=2), encoding="utf-8")
    print(f"\nwrote {args.out / 'exchangeability_cost.json'}")


if __name__ == "__main__":
    main()
