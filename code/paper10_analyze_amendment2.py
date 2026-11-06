"""Analysis of real-audit Amendment 2 (REAL_AUDIT_AMENDMENT2.md).

Assembles two analysis roots from the downloaded Amendment 2 outputs and runs the registered analysis script on each:

  gsm8k768 : the five models' GSM8K files at 768 tokens (Amendment 1 files for the two Qwen models, Amendment 2 files for the
             other three); the ARC files are the registered log-probability files and are not part of this reading.
  arcgen   : the five models' ARC files from greedy generation of the answer letter; the GSM8K files are the registered
             320-token files and are not part of this reading.

Also writes the adequacy and interpretability flags fixed in the amendment: truncation of at most 1% of a model's audit forms
(Arm A) and at most 10% invalid replies on audit forms (Arm B).

Usage: python paper10_analyze_amendment2.py [--a2-dir results/amendment2_20261106] [--out-dir results]
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PRIMARY = ROOT / "results" / "primary_5models_20260821"
A1 = ROOT / "results" / "amendment1_qwen_20260821"
MODELS = {  # key -> (model dir name, source of the 768-token GSM8K files)
    "smollm2": ("HuggingFaceTB--SmolLM2-1.7B-Instruct", "a2"),
    "phi3": ("microsoft--Phi-3-mini-4k-instruct", "a2"),
    "olmo": ("allenai--OLMo-2-1124-7B-Instruct", "a2"),
    "qwen15": ("Qwen--Qwen2.5-1.5B-Instruct", "a1"),
    "qwen7": ("Qwen--Qwen2.5-7B-Instruct", "a1"),
}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--a2-dir", type=Path, default=ROOT / "results" / "amendment2_20261106")
    ap.add_argument("--out-dir", type=Path, default=ROOT / "results")
    args = ap.parse_args()

    roots = {"gsm8k768": args.a2_dir / "analysis_root_gsm8k768", "arcgen": args.a2_dir / "analysis_root_arcgen"}
    for r in roots.values():
        shutil.rmtree(r, ignore_errors=True)
    flags = {}
    for key, (dirname, src768) in MODELS.items():
        a2 = args.a2_dir / key
        env = PRIMARY / dirname / "environment.json"
        g_src = (A1 / dirname) if src768 == "a1" else a2
        for root_name, root in roots.items():
            d = root / dirname
            d.mkdir(parents=True)
            shutil.copy2(env, d / "environment.json")
            if root_name == "gsm8k768":
                for fn in ("gsm8k_results.csv", "gsm8k_control_results.csv"):
                    shutil.copy2(g_src / fn, d / fn)
                for fn in ("arc_results.csv", "arc_control_results.csv"):
                    shutil.copy2(PRIMARY / dirname / fn, d / fn)
            else:
                for fn in ("arc_results.csv", "arc_control_results.csv"):
                    shutil.copy2(a2 / fn, d / fn)
                for fn in ("gsm8k_results.csv", "gsm8k_control_results.csv"):
                    shutil.copy2(PRIMARY / dirname / fn, d / fn)

        g = pd.read_csv(g_src / "gsm8k_results.csv", usecols=["form_type", "correct", "n_generated_tokens"])
        cap = 768
        trunc = (g["n_generated_tokens"] >= cap)
        pub = g["form_type"] == "original_public"
        arc = pd.read_csv(a2 / "arc_results.csv")
        arc_lp = pd.read_csv(PRIMARY / dirname / "arc_results.csv")
        flags[key] = {
            "model": dirname.split("--")[-1],
            "gsm8k_trunc_rate_768_all": round(float(trunc.mean()), 4),
            "gsm8k_trunc_rate_768_public": round(float(trunc[pub].mean()), 4),
            "gsm8k_trunc_rate_768_fresh": round(float(trunc[~pub].mean()), 4),
            "gsm8k_acc_768_all": round(float(g["correct"].mean()), 4),
            "armA_adequate": bool(trunc.mean() <= 0.01),
            "arc_invalid_rate_audit": round(float(1 - arc["valid"].mean()), 4),
            "armB_interpretable": bool((1 - arc["valid"].mean()) <= 0.10),
            "arc_acc_generate": round(float(arc["correct"].mean()), 4),
            "arc_acc_logprob_registered": round(float(arc_lp["correct"].mean()), 4),
        }
    args.a2_dir.mkdir(parents=True, exist_ok=True)
    (args.a2_dir / "amendment2_flags.json").write_text(json.dumps(flags, indent=2), encoding="utf-8")
    for name, root in roots.items():
        out = args.out_dir / f"analysis_amendment2_{name}"
        subprocess.run([sys.executable, str(ROOT / "code" / "paper10_analyze_real_audit.py"),
                        "--results-root", str(root), "--out-dir", str(out)], check=True, cwd=ROOT)
    print(json.dumps(flags, indent=2))


if __name__ == "__main__":
    main()
