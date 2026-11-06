"""Registered analysis of Study 4, the ARC positive control.

Implements POSITIVE_CONTROL_STUDY4_REGISTRATION.md section 6 and nothing else.
Every quantity reported here was named in the registration before the model was
trained, and the interpretation rules in section 7 are evaluated mechanically at
the end rather than read off the numbers by hand.

Three form families per parent:

  P  the public wording, which is what the exposed model was trained on
  F  the two released fresh forms, stem rewritten, options verbatim
  G  the deep paraphrase, stem and options both rewritten

Each estimate is a difference in differences: the exposed model minus the base
model on the exposed parents, minus the same change on the 100 parents that were
never trained on. G has no control counterpart, so by registration it uses the
control group's F change as its counterfactual, and the assumption behind that
substitution is checked on the 25 control parents that do carry a G form.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DRAWS = 20000
SEED = 20260824
MANIPULATION_FLOOR = 0.05     # section 7, first bullet
ASSUMPTION_TOLERANCE = 0.05   # section 6, F-versus-G check on control parents


def per_parent(df: pd.DataFrame) -> pd.DataFrame:
    """One row per parent: accuracy on P, on F (mean of both variants), on G."""
    p = df[df.form_type == "original_public"].set_index("parent_id")["correct"].astype(float)
    f = df[df.form_type.str.startswith("fresh")].groupby("parent_id")["correct"].mean()
    g = df[df.form_type == "deep_paraphrase"].set_index("parent_id")["correct"].astype(float)
    return pd.DataFrame({"P": p, "F": f, "G": g})


def did(change: pd.DataFrame, exposed: np.ndarray, control: np.ndarray,
        family: str, counterfactual: str) -> float:
    """Exposed-group change on `family` minus control-group change on `counterfactual`."""
    a = change.loc[exposed, family].dropna()
    b = change.loc[control, counterfactual].dropna()
    if not len(a) or not len(b):
        return float("nan")
    return float(a.mean() - b.mean())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path,
                    default=ROOT / "study4_out" / "results" / "base" / "arc_study4_results.csv")
    ap.add_argument("--exposed", type=Path,
                    default=ROOT / "study4_out" / "results" / "exposed" / "arc_study4_results.csv")
    ap.add_argument("--exposure-file", type=Path,
                    default=ROOT / "data" / f"positive_control_arc_exposure_seed{SEED}.csv")
    ap.add_argument("--exempt-file", type=Path, default=ROOT / "data" / "arc_g_exempt.txt")
    ap.add_argument("--out-dir", type=Path, default=ROOT / "results" / "study4_arc")
    ap.add_argument("--g-counterfactual", choices=("fresh", "deep"), default="fresh",
                    help="Studies 4 and 5 have deep paraphrases for only 25 control "
                         "parents, so the control group's fresh-form change stands in for "
                         "its deep-paraphrase change and an assumption check decides "
                         "whether that is allowed. Study 6 writes deep paraphrases for "
                         "every control parent, so 'deep' compares like with like and "
                         "there is no assumption left to check.")
    ap.add_argument("--no-leak", action="store_true",
                    help="Study 7: nothing was planted, so a difference in differences "
                         "near zero is the desired outcome and not a failed manipulation.")
    ap.add_argument("--label", default="study4",
                    help="Names the summary file, so two studies do not overwrite "
                         "each other when only --out-dir is changed.")
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    base = per_parent(pd.read_csv(args.base))
    exposed_model = per_parent(pd.read_csv(args.exposed))
    if not base.index.equals(exposed_model.index):
        raise SystemExit("the two audits do not cover the same parents")

    assign = pd.read_csv(args.exposure_file).set_index("parent_id")["exposed"]
    exempt = {line.strip() for line in args.exempt_file.read_text().split() if line.strip()}

    change = exposed_model - base
    exposed_ids = np.array([i for i in change.index if assign.get(i, 0) == 1])
    control_ids = np.array([i for i in change.index if assign.get(i, 0) == 0])
    # Amendment 1: items whose options cannot be reworded carry a stem-only G,
    # which is what F already is, so they are out of the G arm by registration.
    g_exposed = np.array([i for i in exposed_ids
                          if i not in exempt and not np.isnan(change.loc[i, "G"])])
    g_control = np.array([i for i in control_ids
                          if i not in exempt and not np.isnan(change.loc[i, "G"])])

    print(f"exposed parents {len(exposed_ids)}   control parents {len(control_ids)}")
    print(f"G arm: {len(g_exposed)} exposed, {len(g_control)} control assumption-check\n")

    # Study 6 compares deep paraphrases against deep paraphrases, so the control
    # side of the G arm is the control parents that carry one, and no
    # substitution takes place.
    direct_g = args.g_counterfactual == "deep"
    g_family = "G" if direct_g else "F"
    g_control_side = g_control if direct_g else control_ids
    print(f"G counterfactual: control group's "
          f"{'deep paraphrases' if direct_g else 'fresh forms'} "
          f"({len(g_control_side)} parents)\n")

    point = {
        "did_P": did(change, exposed_ids, control_ids, "P", "P"),
        "did_F": did(change, exposed_ids, control_ids, "F", "F"),
        "did_G": did(change, g_exposed, g_control_side, "G", g_family),
    }

    # Registration section 6: does fine-tuning move F and G alike where nothing
    # leaked? Only asked when the F change is standing in for the G change. With
    # a direct comparison there is nothing being assumed, so nothing to check.
    if direct_g:
        assumption_gap = float("nan")
        assumption_holds = True
    else:
        assumption_gap = float(change.loc[g_control, "G"].mean()
                               - change.loc[g_control, "F"].mean())
        assumption_holds = abs(assumption_gap) <= ASSUMPTION_TOLERANCE

    boot = {k: np.empty(DRAWS) for k in ("did_P", "did_F", "did_G", "share_F", "share_G",
                                         "visible_F", "visible_G")}
    for d in range(DRAWS):
        e = rng.choice(exposed_ids, len(exposed_ids), replace=True)
        c = rng.choice(control_ids, len(control_ids), replace=True)
        ge = rng.choice(g_exposed, len(g_exposed), replace=True)
        p = did(change, e, c, "P", "P")
        f = did(change, e, c, "F", "F")
        # Only the direct comparison needs its own control draw. Consuming a
        # draw in the substituted mode as well would shift the random stream and
        # move the intervals already published for Studies 4 and 5, which must
        # not change because a later study gained an option.
        gc = rng.choice(g_control_side, len(g_control_side), replace=True) if direct_g else c
        g = did(change, ge, gc, "G", g_family)
        boot["did_P"][d], boot["did_F"][d], boot["did_G"][d] = p, f, g
        boot["share_F"][d] = f / p if p else np.nan
        boot["share_G"][d] = g / p if p else np.nan
        boot["visible_F"][d] = p - f
        boot["visible_G"][d] = p - g

    point["share_F"] = point["did_F"] / point["did_P"] if point["did_P"] else float("nan")
    point["share_G"] = point["did_G"] / point["did_P"] if point["did_P"] else float("nan")
    point["visible_F"] = point["did_P"] - point["did_F"]
    point["visible_G"] = point["did_P"] - point["did_G"]

    # A transfer share is a fraction of the planted effect. When the planted
    # effect is negative there is no fraction to take, and the ratio of two
    # negative numbers looks like a healthy positive share to anyone reading the
    # table without the manipulation check beside it. Withhold it at the source.
    if point["did_P"] < MANIPULATION_FLOOR:
        for key in ("share_F", "share_G"):
            point[key] = float("nan")
            boot[key][:] = np.nan

    summary = {}
    for key, value in point.items():
        draws = boot[key][~np.isnan(boot[key])]
        lo, hi = (np.percentile(draws, [2.5, 97.5]) if len(draws) else (np.nan, np.nan))
        summary[key] = {"estimate": round(float(value), 4),
                        "ci_low": round(float(lo), 4), "ci_high": round(float(hi), 4)}

    # Raw accuracies, so the difference in differences can be checked by hand.
    acc = {}
    for name, frame in (("base", base), ("exposed", exposed_model)):
        for fam in ("P", "F", "G"):
            ids = g_exposed if fam == "G" else exposed_ids
            acc[f"{name}_{fam}_exposed_parents"] = round(float(frame.loc[ids, fam].mean()), 4)
            # The control side of the G arm is only meaningful where the control
            # parents actually carry a deep paraphrase, which before Study 6 was
            # 20 of them and is now 83.
            control_side = g_control if fam == "G" else control_ids
            if len(control_side):
                acc[f"{name}_{fam}_control_parents"] = round(
                    float(frame.loc[control_side, fam].mean()), 4)

    manipulation_ok = point["did_P"] >= MANIPULATION_FLOOR
    # Registration section 6: if fine-tuning moves F and G differently on the
    # uncontaminated parents, the control group's F change is not a usable
    # counterfactual for G, and the G arm is reported descriptively only. The
    # verdict must not lean on an arm the registration has demoted.
    g_inferential = assumption_holds
    saturated = max(acc.get("exposed_P_exposed_parents", 0),
                    acc.get("exposed_F_exposed_parents", 0)) >= 0.98

    if args.no_leak:
        # There was nothing to detect, so the statistic is an empirical null for the
        # whole procedure rather than a manipulation check.
        worst = max(abs(point[k]) for k in ("did_P", "did_F", "did_G"))
        if worst <= MANIPULATION_FLOOR:
            verdict = (f"negative control passed: with no leak present the largest "
                       f"difference in differences across the three form families is "
                       f"{worst:.4f}, inside the registered 0.05, so the procedure does "
                       f"not manufacture an effect from nothing and the positive-control "
                       f"estimates are not inflated by fine-tuning alone.")
        else:
            verdict = (f"negative control FAILED: with no leak present the largest "
                       f"difference in differences is {worst:.4f}, beyond the registered "
                       f"0.05. Every positive-control effect must be reported with this "
                       f"offset stated beside it.")
    elif not manipulation_ok:
        verdict = ("failed manipulation: the leak did not raise accuracy on the leaked "
                   "wording by the registered 0.05, so this study contributes nothing to "
                   "any claim about transfer, in either direction. It is not evidence "
                   "that contamination fails to transfer on ARC.")
    elif not g_inferential:
        verdict = ("manipulation succeeded and the G counterfactual assumption FAILED, so "
                   "the deep-paraphrase arm is descriptive only and no confirmation of "
                   "Section 7.11 may be drawn from it. What stands is the F arm and the "
                   "visible gap, and the F arm holds the options word for word, so a "
                   "transfer share near 1 there is the mechanical outcome the registration "
                   "anticipated rather than evidence of deep item knowledge.")
    elif summary["did_G"]["ci_low"] > 0 and summary["did_F"]["ci_low"] > 0:
        verdict = ("transfer survives a log-probability scoring path and a rewrite of the "
                   "options, confirming Section 7.11 on a second benchmark.")
    elif summary["did_F"]["ci_low"] > 0:
        verdict = ("what looks like transfer on ARC is largely option-level memorisation: "
                   "F carries the effect and G does not. The released ARC bank is blind to "
                   "a form of contamination a deeper rewrite exposes.")
    else:
        verdict = ("contamination was planted but did not transfer to either rewrite depth; "
                   "the GSM8K transfer finding does not generalise to this scoring path.")
    if saturated:
        verdict += (" CEILING: accuracy on the exposed parents reaches or approaches 1.00, "
                    "so the differences in differences are censored from above and every "
                    "transfer share built from them is unreliable in size, though not in "
                    "sign.")

    out = {"n_exposed": len(exposed_ids), "n_control": len(control_ids),
           "n_g_exposed": len(g_exposed), "n_g_control_check": len(g_control),
           "accuracies": acc, "estimates": summary,
           "manipulation_check": {"did_P": summary["did_P"]["estimate"],
                                  "floor": MANIPULATION_FLOOR, "passed": bool(manipulation_ok)},
           "g_counterfactual": {"mode": args.g_counterfactual,
                                "n_control_side": len(g_control_side)},
           "g_counterfactual_assumption": {"control_G_change_minus_F_change":
                                           round(assumption_gap, 4),
                                           "tolerance": ASSUMPTION_TOLERANCE,
                                           "holds": bool(assumption_holds),
                                           "needed": not direct_g},
           "registered_verdict": verdict}
    (args.out_dir / f"{args.label}_summary.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    print("accuracy on the exposed parents")
    for fam in ("P", "F", "G"):
        print(f"  {fam}: base {acc[f'base_{fam}_exposed_parents']:.4f} "
              f"-> exposed {acc[f'exposed_{fam}_exposed_parents']:.4f}")
    print("accuracy on the control parents")
    for fam in ("P", "F"):
        print(f"  {fam}: base {acc[f'base_{fam}_control_parents']:.4f} "
              f"-> exposed {acc[f'exposed_{fam}_control_parents']:.4f}")
    print("\ndifference in differences, 95% bootstrap over parents")
    for key in ("did_P", "did_F", "did_G", "visible_F", "visible_G", "share_F", "share_G"):
        s = summary[key]
        print(f"  {key:10s} {s['estimate']:+.4f}  [{s['ci_low']:+.4f}, {s['ci_high']:+.4f}]")
    print(f"\nmanipulation check: DiD on P = {summary['did_P']['estimate']:+.4f} "
          f"against a floor of {MANIPULATION_FLOOR} -> "
          f"{'PASSED' if manipulation_ok else 'FAILED'}")
    print(f"G counterfactual assumption: control G change minus F change = "
          f"{assumption_gap:+.4f} -> {'holds' if assumption_holds else 'FAILED'}")
    print(f"\nregistered verdict: {verdict}")


if __name__ == "__main__":
    main()
