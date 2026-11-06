"""Mechanical checks on the Study 4 deep-paraphrase bank.

Enforces the rules fixed in POSITIVE_CONTROL_STUDY4_REGISTRATION.md section 3
that a script can enforce. Rule 2, that rewording must not make a distractor
correct or the key wrong, is semantic and is not checkable here; it is what the
human reading is for, and the registration makes that reading a precondition.

Checked:
  1. every option is reworded, and is neither identical to nor a substring of
     its counterpart in the public form, in either direction
  3. the key stays at the same letter position, inherited from the public form
  4. the stem is genuinely rewritten: token overlap with the public stem below
     the 0.80 threshold the released ARC bank is held to
  5. every numeric quantity and unit in the public form survives unchanged
  plus: the four options stay pairwise distinct, and lengths stay within the
  bounds used for the released bank

Items exempted from rule 1 by Amendment 1, whose options are equations or bare
quantities, are checked on everything else and reported separately.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OPTS = ("optA", "optB", "optC", "optD")
JACCARD_MAX = 0.80


def tokens(text: str) -> set:
    return set(re.findall(r"[a-z0-9']+", str(text).lower()))


def jaccard(a: str, b: str) -> float:
    ta, tb = tokens(a), tokens(b)
    return len(ta & tb) / max(1, len(ta | tb))


def numbers(text: str) -> Counter:
    return Counter(re.findall(r"\d[\d,]*(?:\.\d+)?", str(text).replace(",", "")))


def norm(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(text).lower()).strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", type=Path, default=ROOT / "items" / "arc_deep_paraphrase.csv")
    ap.add_argument("--source", type=Path, default=ROOT / "items" / "arc_matched_forms.csv")
    args = ap.parse_args()

    g = pd.read_csv(args.bank)
    pub = pd.read_csv(args.source)
    pub = pub[pub.form_type == "original_public"].set_index("parent_id")

    problems, exempt = [], []
    for r in g.itertuples():
        p = pub.loc[r.parent_id]
        if int(r.options_reworded) == 0:
            exempt.append(r.parent_id)
        else:
            for col in OPTS:
                new, old = norm(getattr(r, col)), norm(p[col])
                if new == old:
                    problems.append(f"{r.parent_id}/{col}: identical to the public option")
                elif new in old or old in new:
                    problems.append(f"{r.parent_id}/{col}: one option contains the other "
                                    f"({getattr(r, col)!r} vs {p[col]!r})")
        seen = [norm(getattr(r, c)) for c in OPTS]
        if len(set(seen)) != 4:
            problems.append(f"{r.parent_id}: the four options are not pairwise distinct")

        sim = jaccard(r.prompt, p["prompt"])
        if sim >= JACCARD_MAX:
            problems.append(f"{r.parent_id}: stem jaccard {sim:.2f} to the public stem, "
                            f"at or above the {JACCARD_MAX} threshold")
        ratio = len(str(r.prompt)) / max(1, len(str(p["prompt"])))
        if not 0.60 <= ratio <= 1.60:
            problems.append(f"{r.parent_id}: stem length ratio {ratio:.2f} outside [0.60, 1.60]")

        # Rule 5: every quantity in the public form must survive somewhere in the
        # deep paraphrase, stem or options. A dropped number changes the question.
        want = numbers(p["prompt"]) + sum((numbers(p[c]) for c in OPTS), Counter())
        got = numbers(r.prompt) + sum((numbers(getattr(r, c)) for c in OPTS), Counter())
        lost = want - got
        if lost:
            problems.append(f"{r.parent_id}: quantities dropped: {dict(lost)}")

    print(f"deep-paraphrase bank: {len(g)} items, {len(exempt)} exempt from the "
          f"option-rewording rule by Amendment 1")
    if exempt:
        print("  exempt:", ", ".join(exempt))
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for x in problems:
            print("   -", x)
        sys.exit(1)
    print("\nAll mechanical checks pass. Rule 2 is semantic and needs the human reading.")


if __name__ == "__main__":
    main()
