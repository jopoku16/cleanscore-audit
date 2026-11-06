"""Deterministic verification of CleanScore real-audit matched forms.

Registered checks (REAL_AUDIT_REGISTRATION.md section 3):

GSM8K variants
  - every parent has exactly the registered form set;
  - the multiset of digit-number tokens in each variant equals the original's;
  - the gold answer is unchanged;
  - character-length ratio to the original lies in [0.60, 1.60];
  - variants differ from the original and from each other.

ARC variants
  - options and answer key are untouched (checked against the frozen sample);
  - the rewritten stem is not a trivial copy: token Jaccard similarity with the
    original stem must be below 0.80;
  - character-length ratio in [0.60, 1.60] against the original stem.

Control banks
  - GSM8K-style controls: form set complete, digit multiset preserved across
    forms of a parent, stated answer consistent across forms, and no control
    text duplicates any sampled benchmark item;
  - ARC-style controls: four options, a valid key, stem variants pass the same
    dissimilarity rule.

Exit code is nonzero if any check fails; failures are listed by item.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def numbers(text: str) -> Counter:
    return Counter(re.findall(r"\d[\d,]*(?:\.\d+)?", text.replace(",", "")))


def tokens(text: str) -> set:
    return set(re.findall(r"[a-z0-9']+", text.lower()))


def jaccard(a: str, b: str) -> float:
    ta, tb = tokens(a), tokens(b)
    return len(ta & tb) / max(1, len(ta | tb))


def check_gsm8k(forms: pd.DataFrame, parents: pd.DataFrame,
                notices: list[str] | None = None) -> list[str]:
    """Hard checks for the GSM8K bank, plus one advisory.

    The advisory is the token-dissimilarity rule that ARC stems are held to. It
    was never applied to GSM8K, which was an oversight: GSM8K forms were checked
    only for exact identity to the original, so a near-copy passed. Applying the
    rule after the fact flags 21 of 400 forms.

    It is reported rather than failed, deliberately. The bank was frozen before
    any model was queried, and dropping items once the results are known is the
    move the registration exists to prevent, so the released bank still verifies
    and Section 7.7 reports the sensitivity analysis instead. An audit building a
    new bank with this code should promote the advisory to a failure before
    freezing.
    """
    problems = []
    gold = dict(zip(parents["parent_id"], parents["gold"].astype(str)))
    original = dict(zip(parents["parent_id"], parents["question"]))
    # Per-parent variation in rewrite depth is healthy, so flagging it item by
    # item cries wolf. What is not healthy is one variant slot being
    # systematically lighter than the other across the whole bank, which is what
    # happened here: every near-copy was a first variant. That only shows up in
    # the aggregate, so it is reported once at the end rather than per item.
    depth_by_variant: dict[int, list[float]] = {0: [], 1: []}
    for pid, group in forms.groupby("parent_id"):
        kinds = sorted(group["form_type"])
        if kinds != ["fresh_variant_1", "fresh_variant_2", "original_public"]:
            problems.append(f"{pid}: form set {kinds}")
            continue
        rows = {row["form_type"]: row for _, row in group.iterrows()}
        orig_text = original[pid]
        if rows["original_public"]["prompt"] != orig_text:
            problems.append(f"{pid}: original text drifted from frozen sample")
        base = numbers(orig_text)
        texts, sims = [], []
        for kind in ("fresh_variant_1", "fresh_variant_2"):
            row = rows[kind]
            if str(row["answer"]) != gold[pid]:
                problems.append(f"{pid}/{kind}: answer {row['answer']} != gold {gold[pid]}")
            if numbers(row["prompt"]) != base:
                problems.append(f"{pid}/{kind}: numeric multiset differs {dict(numbers(row['prompt'])-base)} / {dict(base-numbers(row['prompt']))}")
            ratio = len(row["prompt"]) / max(1, len(orig_text))
            if not 0.60 <= ratio <= 1.60:
                problems.append(f"{pid}/{kind}: length ratio {ratio:.2f}")
            if row["prompt"].strip() == orig_text.strip():
                problems.append(f"{pid}/{kind}: identical to original")
            sim = jaccard(row["prompt"], orig_text)
            sims.append(sim)
            if sim >= 0.80 and notices is not None:
                notices.append(f"{pid}/{kind}: jaccard {sim:.2f} to original, at or above the "
                               f"threshold ARC forms are held to (advisory, see Section 7.7)")
            texts.append(row["prompt"].strip())
        if len(sims) == 2:
            depth_by_variant[0].append(sims[0])
            depth_by_variant[1].append(sims[1])
        if len(texts) == 2 and texts[0] == texts[1]:
            problems.append(f"{pid}: variants identical to each other")
    if notices is not None and depth_by_variant[0]:
        mean0 = sum(depth_by_variant[0]) / len(depth_by_variant[0])
        mean1 = sum(depth_by_variant[1]) / len(depth_by_variant[1])
        if abs(mean0 - mean1) >= 0.10:
            lighter = 1 if mean0 > mean1 else 2
            notices.append(
                f"variant {lighter} is systematically the lighter rewrite across the bank: "
                f"mean jaccard to original {mean0:.2f} for variant 1 against {mean1:.2f} for "
                f"variant 2. Both slots should be rewritten to the same depth (advisory)")
    missing = set(parents["parent_id"]) - set(forms["parent_id"])
    for pid in sorted(missing):
        problems.append(f"{pid}: no forms authored")
    return problems


def check_arc(forms: pd.DataFrame, parents: pd.DataFrame) -> list[str]:
    problems = []
    frozen = parents.set_index("parent_id")
    for pid, group in forms.groupby("parent_id"):
        kinds = sorted(group["form_type"])
        if kinds != ["fresh_variant_1", "fresh_variant_2", "original_public"]:
            problems.append(f"{pid}: form set {kinds}")
            continue
        ref = frozen.loc[pid]
        for _, row in group.iterrows():
            for col in ("optA", "optB", "optC", "optD", "answerKey"):
                if str(row[col]) != str(ref[col]):
                    problems.append(f"{pid}/{row['form_type']}: {col} altered")
        rows = {row["form_type"]: row for _, row in group.iterrows()}
        if rows["original_public"]["prompt"] != ref["question"]:
            problems.append(f"{pid}: original stem drifted from frozen sample")
        for kind in ("fresh_variant_1", "fresh_variant_2"):
            stem = rows[kind]["prompt"]
            sim = jaccard(stem, ref["question"])
            if sim >= 0.80:
                problems.append(f"{pid}/{kind}: jaccard {sim:.2f} too close to original")
            ratio = len(stem) / max(1, len(ref["question"]))
            if not 0.60 <= ratio <= 1.60:
                problems.append(f"{pid}/{kind}: length ratio {ratio:.2f}")
        if rows["fresh_variant_1"]["prompt"].strip() == rows["fresh_variant_2"]["prompt"].strip():
            problems.append(f"{pid}: variants identical to each other")
    missing = set(parents["parent_id"]) - set(forms["parent_id"])
    for pid in sorted(missing):
        problems.append(f"{pid}: no forms authored")
    return problems


def check_gsm8k_controls(forms: pd.DataFrame, parents: pd.DataFrame) -> list[str]:
    problems = []
    bench_texts = {t.strip() for t in parents["question"]}
    for pid, group in forms.groupby("parent_id"):
        kinds = sorted(group["form_type"])
        if kinds != ["fresh_variant_1", "fresh_variant_2", "public_like"]:
            problems.append(f"{pid}: form set {kinds}")
            continue
        answers = set(group["answer"].astype(str))
        if len(answers) != 1:
            problems.append(f"{pid}: inconsistent answers {answers}")
        base = numbers(group[group["form_type"] == "public_like"].iloc[0]["prompt"])
        for _, row in group.iterrows():
            if row["prompt"].strip() in bench_texts:
                problems.append(f"{pid}/{row['form_type']}: duplicates a benchmark item")
            if numbers(row["prompt"]) != base:
                problems.append(f"{pid}/{row['form_type']}: numeric multiset differs from public_like form")
    return problems


def check_arc_controls(forms: pd.DataFrame) -> list[str]:
    problems = []
    for pid, group in forms.groupby("parent_id"):
        kinds = sorted(group["form_type"])
        if kinds != ["fresh_variant_1", "fresh_variant_2", "public_like"]:
            problems.append(f"{pid}: form set {kinds}")
            continue
        first = group.iloc[0]
        if str(first["answerKey"]) not in {"A", "B", "C", "D"}:
            problems.append(f"{pid}: bad answer key {first['answerKey']}")
        for _, row in group.iterrows():
            for col in ("optA", "optB", "optC", "optD", "answerKey"):
                if str(row[col]) != str(first[col]):
                    problems.append(f"{pid}/{row['form_type']}: {col} inconsistent across forms")
        rows = {row["form_type"]: row for _, row in group.iterrows()}
        base = rows["public_like"]["prompt"]
        for kind in ("fresh_variant_1", "fresh_variant_2"):
            if jaccard(rows[kind]["prompt"], base) >= 0.80:
                problems.append(f"{pid}/{kind}: too close to public_like stem")
    return problems


def main() -> None:
    failures: list[str] = []
    notices: list[str] = []
    gsm_parents = pd.read_csv(ROOT / "data" / "gsm8k_parents_200.csv")
    arc_parents = pd.read_csv(ROOT / "data" / "arc_parents_200.csv")

    targets = [
        ("items/gsm8k_matched_forms.csv", lambda df: check_gsm8k(df, gsm_parents, notices)),
        ("items/arc_matched_forms.csv", lambda df: check_arc(df, arc_parents)),
        ("items/gsm8k_control_bank.csv", lambda df: check_gsm8k_controls(df, gsm_parents)),
        ("items/arc_control_bank.csv", check_arc_controls),
    ]
    for rel, checker in targets:
        path = ROOT / rel
        if not path.is_file():
            print(f"[pending] {rel} not present yet")
            continue
        df = pd.read_csv(path)
        problems = checker(df)
        label = "OK" if not problems else f"{len(problems)} problem(s)"
        print(f"[{label}] {rel}: {df['parent_id'].nunique()} parents, {len(df)} forms")
        for p in problems:
            print("   -", p)
        failures.extend(problems)
    if notices:
        near = sum(1 for n in notices if "at or above the" in n)
        print(f"\n[advisory] {len(notices)} note(s) on the GSM8K bank, {near} of them fresh "
              f"forms at or above the ARC dissimilarity threshold. None fails the frozen "
              f"bank; Section 7.7 reports the sensitivity analysis.")
        for n in notices:
            print("   -", n)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
