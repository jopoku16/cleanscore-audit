# CleanScore audit: forms, registrations, code and outputs

This repository holds the data and code behind the paper *CleanScore: Black-Box Benchmark Audits with Negative Controls and Sensitivity Bounds* by Jeffery Opoku and David Banahene. An earlier version of the paper is on arXiv (2609.22183).

CleanScore audits a public benchmark for an advantage that its published wording gives a model. For each benchmark question (a parent) it compares accuracy on the public form with accuracy on two freshly written forms that keep the numbers, facts and answer. A private control bank of never-public problems estimates how large the gap is when nothing has leaked. The paper reports the audit of five open models on 200 GSM8K and 200 ARC-Challenge parents, the registered positive-control experiments that measure how much of a planted contamination effect such an audit can see, and the design simulations.

## Contents

| Folder or file | What it holds |
|---|---|
| `registrations/` | The registered protocol of the audit and of each positive-control study, the two audit amendments, and the registration of a larger audit that has not been run. See `REDACTIONS.md` for the one change made to these files. |
| `items/` | The matched-form bank: 200 GSM8K and 200 ARC-Challenge parents, each with its public form and two fresh forms (1,200 forms), the never-public control banks (60 GSM8K-style and 40 ARC-style parents, 300 forms), and the forms used by the ARC positive-control studies. |
| `data/` | The frozen parent samples with the sampling scripts' outputs, and the GSM8K training questions used as background items in the positive controls. |
| `code/` | Sampling, item verification, evaluation, analysis, simulation, baselines, positive-control training and plotting scripts. The figure scripts redraw the paper's figures from the files in `results/`. |
| `results/` | Per-form outputs of the five audited models under the registered settings, the 768-token reruns, the output-only ARC arm, every analysis table, the simulations, the positive-control runs for Studies 1 to 9, and the figures. |
| `reading_packets/` | The packets prepared for the authors' reading of the forms. |
| `DEVIATIONS.md` | Every deviation from a registration, in date order, with its effect on the reported results. |
| `MANIFEST.json` | SHA-256 and size of every file. |

## What the forms are

A language model from a provider and family different from every audited model drafted the fresh forms and the control banks under written rules. A script checked every form (numeric tokens, answer, length and, for ARC, option integrity and a dissimilarity threshold). The authors read a prioritized packet, not all forms. One defect is known and left in the bank: the second fresh form of `arcc_test_0656` is ungrammatical. `DEVIATIONS.md` and the paper give the details.

## Intended and unintended uses

Intended: reproducing the paper, auditing other models on these parents with the same protocol, and studying how rewriting changes benchmark scores. Not intended: training models. Once these forms are public they can enter training data, so treat them as used, and do not read a score on them as a held-out score. The forms of the larger audit that is registered but not run are not released, so that audit stays valid.

## Licenses

Code: MIT (`LICENSE`). Data in `items/` and `data/`: CC BY-SA 4.0 (`LICENSE-DATA.md`). GSM8K rows derive from `openai/gsm8k` (MIT) and ARC rows from `allenai/ai2_arc` (CC BY-SA 4.0); their original notices apply.

## Reproducing the main tables

The scripts find their folders relative to this repository, which keeps the layout of the working copy.

1. Evaluate a model: `python code/paper10_run_real_audit_eval.py --items-dir items --out-dir <out> --models <name>@<revision>` (GSM8K at 320 tokens, ARC by option log probabilities). The Amendment 1 reruns of the two Qwen models use the same script with `--max-new-tokens 768 --amended-parser`. The Amendment 2 runs (GSM8K at 768 tokens, ARC by generated letter) use `code/paper10_run_amendment2_eval.py`, which imports the registered GSM8K function unchanged.
2. Analyse: `python code/paper10_analyze_real_audit.py --results-root results/primary_5models_20260821 --out-dir <out>`. The Amendment 2 analyses are built by `code/paper10_analyze_amendment2.py`.
3. Simulations: `code/paper10_claim_rule_power.py`, `code/paper10_power_analysis.py`, `code/paper10_randomization_test.py`.
4. Positive controls: `code/paper10_positive_control.py`, `code/paper10_arc_positive_control.py`, and the pooling scripts `code/paper10_pool_*.py`.
5. Figures: `code/paper10_plot_*.py`, `code/paper10_fig_*.py`, `code/paper10_make_study9_figures.py`.

Model runs used free GPU sessions. Weights are not included; the model names and pinned revisions are in each run's `environment.json`.

## Hosting and maintenance

The repository is hosted on GitHub under the authors' account and released as tagged versions; the paper cites the version tag. A DOI is minted from the release when the paper is accepted. The authors maintain the repository, answer questions through its issue tracker and record every correction in a changelog and in `DEVIATIONS.md`. File integrity can be checked against `MANIFEST.json`.

## Citation

See `CITATION.cff`.
