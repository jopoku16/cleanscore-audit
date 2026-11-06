# Study 9 registration: the four GSM8K positive controls under three further training seeds

Registered 23 October 2026. The design, seeds and run rules were written before any Study 9 run was started. The estimator in item 4 and the wording rules under "What the paper will say" were finalized after the first two kernels (Qwen2.5-1.5B and StableLM-2-1.6B, seed 20261024) had been pushed and before any Study 9 result was read; the audit log says so.

## Purpose

The transferred-share estimate of Section 8.1 (pooled 77%, interval 52% to 110%) rests on four models fine-tuned once each. Its bootstrap interval covers which parents were drawn and nothing else. This study measures how much the estimate moves when only the training run changes, and replaces the interval with one that covers both sources of variation.

## An override of earlier rules, stated plainly

Studies 1, 2 and 3 each ruled out additional seeds by name. The rules were written to stop an experiment being repeated until it gave a convenient answer. A replication that can only weaken or confirm a published estimate, and that commits to reporting every run, does not do what the rules guard against, and Study 8 made the same override for the ARC study. We make it here, in writing, before any run.

## Design

Four base models, as registered for Studies 1 to 3, each at the pinned revision of that study:

| Model | Revision |
|---|---|
| Qwen/Qwen2.5-1.5B-Instruct | 989aa7980e4cf806f80c7fef2b1adb7bc71aa306 |
| HuggingFaceTB/SmolLM2-1.7B-Instruct | 31b70e2e869a7173562077fd711b654946d38674 |
| allenai/OLMo-2-0425-1B-Instruct | 48d788eca847d4d7548f375ad03d3c9312f6139e |
| stabilityai/stablelm-2-1_6b-chat | f3fe67057c2789ae1bb1fe42b038da99840d4f13 |

Three training seeds, fixed now: **20261024, 20261025, 20261026**. That is 12 runs. Together with the registered run of each model (seed 20260822) every model has four runs.

Identical to Studies 1 to 3: the exposure assignment (the same 100 exposed and 100 unexposed parents, from seed 20260822), the 900 background records, the mixture size of 1,000, three epochs, learning rate 2e-5, batch size 2 with gradient accumulation 8, maximum length 384, Adafactor, gradient checkpointing, full-parameter fp32 fine-tuning sharded over both GPUs, the 320-token generation budget and the unmodified audit script (`paper10_run_real_audit_eval.py`), which audits the exposed model on all four item files.

Different: the trainer seed, the data seed, and the order of the 1,000 training records. Nothing else. The code change is one argument, `--train-seed` in `paper10_positive_control.py`, and with the argument absent the script reproduces the earlier runs (checked: the training mixture of the default run has the same SHA-256 as before the change).

Clean audits of the base models are deterministic and already archived (Table 3 for Qwen and SmolLM2, the Study 3 base audits for OLMo-2-1B and StableLM-2-1.6B), so each run is training plus the audit of the exposed model.

## Run rules

One kernel per (model, seed), one training run and one audit per session. If a run fails for an infrastructure reason (out of memory, session killed), the identical kernel is rerun and the failed attempt is recorded in the audit log. No run is dropped, replaced or repeated because of its result. Every completed run enters the analysis, including a run whose manipulation check fails.

## Estimands and estimators

For each run: the difference in differences against the unexposed parents of the same model for public-form accuracy (DiD public) and for fresh-form accuracy (DiD fresh), and the visible gap, exactly as in Studies 1 to 3.

1. **Per-run table** of DiD public, DiD fresh and visible gap for all 16 runs, with the per-model spread across the four runs.
2. **Per-model mean** over its four runs.
3. **Pooled effects:** the mean over the four models of the per-model means, for DiD public and DiD fresh. The **invisible share** is pooled DiD fresh divided by pooled DiD public.
4. **Primary interval, two levels.** In each of 20,000 draws: (a) resample the exposed parents and the unexposed parents with replacement once, and apply the same resampled parents to every model and every seed, because the parents are shared across all 16 runs; (b) add a seed component for each model. With four runs per model, resampling the runs would be crude, so the between-run standard deviation s of a model's DiD is estimated from its four runs and the sampling error of the mean of four runs is t(3) * s / 2, the usual t interval. DiD public and DiD fresh draw independent t variables, which is the conservative choice for their ratio; the version with a shared t variable is reported beside it. Compute the per-model means, the pooled effects and the share, and take percentile intervals. This interval covers parent and training-run variation and replaces the one in the paper.
5. **Comparison interval.** The Study 3 estimator (independent resampling of parents within each model, one run each) on the registered runs, and the same estimator on all 16 runs treated as a pool, reported beside the primary one so a reader can see what each source of variation contributes.

The shared-parent resampling in (4)(a) is a change from the registered Study 3 pooling, which resampled parents independently across models. It is the correct treatment when the same parents are used in every model, and it can only widen the interval.

## What the paper will say, fixed before the results

- The headline invisible share and its interval in the abstract, introduction, Section 8.1 and the discussion are replaced by the primary two-level estimate, whatever it is.
- The statement that most of a contamination effect is invisible to a paraphrase audit is kept only if the lower 95% limit of the invisible share is above 0.5. If the lower limit is between 0.25 and 0.5 the wording becomes a substantial share, a quarter to a half or more. If it is below 0.25 the paper says that transfer is established but its share is not pinned down.
- The Study 3 falsifier stands. If the two-level interval for the pooled DiD fresh includes zero, the paper says that transfer is not established once training variation is included.
- If the pooled estimate moves by more than five points of share in either direction, the old figure is reported beside the new one in Section 8.1 and the change is described.
- Per-model spread is reported. A model whose runs disagree in sign on DiD fresh is named.
- If the pooled DiD fresh interval excludes zero but the lower limit of the share is below 0.25, the paper says that a substantial share transfers and gives no number for it. If the pooled DiD fresh interval includes zero, the paper says transfer was detected in k of the four models, with k counted from the per-model intervals.
- A run whose manipulation check fails (DiD public below 0.05) stays in the analysis and in the spread, as in Study 8. SmolLM2-1.7B, whose registered run gave +0.100 with an interval that includes zero, is the likeliest model to produce one.

## What this does not do

It adds no new model, dose, exposure format or benchmark. The models stay between 1B and 1.7B parameters and the leak stays deliberate and concentrated. It does not address interference between trained and untrained parents or other effects of a fine-tuning run beyond seed-to-seed variation. The authors know the earlier results, so this is a replication that can confirm or weaken the earlier estimate and cannot be read as an independent test.

## Files

`code/paper10_positive_control.py` (with `--train-seed`), `code/make_build_study9_kernel.py` and `code/build_study9_kernel.py` (kernel builder), kernels `cleanscore-study-9-<model>-<seed>` under `kernels/`, results under `results/study9_gsm8k/`. Analysis: `code/paper10_pool_study9.py`, written before the runs finish and run once when all 12 are in.
