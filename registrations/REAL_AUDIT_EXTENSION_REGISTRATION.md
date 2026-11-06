# CleanScore extended GSM8K audit: registered protocol

Registered 23 October 2026. Its SHA-256 is recorded in AUDIT_LOG.md before any item is drafted. Nothing in it has been run. Changes after that point are appended as dated amendments, never edited in place.

## 1. Why this audit exists

The paper's power analysis shows that at the first audit's size (200 audited parents, control banks of 60) the claim rule flags a planted ten-point advantage in 5% of GSM8K audits. This audit is sized to give the claim rule a useful chance of finding a real advantage, and it removes the weaknesses the paper lists in its own Section 10: a control bank smaller than the audit, no stated multiplicity treatment, a Wald component inside the sensitivity interval where the guardrail applies, a verifier that never checked GSM8K near-copies, rewrites of unequal depth, a 320-token budget, and a human reading that came after the results.

## 2. Scope decisions

**GSM8K only.** ARC is not extended. Its released rewrites keep the options fixed, so a larger audit would inherit the blindness Section 8.2 of the paper proves. An ARC extension with stem-and-option rewrites changes the estimand and is a separate registration.

**A control bank of 300, not 200.** The first plan was 800 audited parents and 200 control parents. The power simulation of Section 10 shows that the control bank is the binding constraint: with the registered interval, 800 audited parents and 200 control parents detect a planted ten-point advantage 60% of the time, and 800 and 400 detect it 83% of the time. A bank of 300 is the compromise, set because a bank of 200 sits exactly at the guardrail's size limit and near-ceiling models may fall under its nonzero-gap limit.

## 3. Design in one paragraph

800 GSM8K test parents, all with newly drafted fresh forms; a newly composed control bank of 300 parents; five open models; a human reading of a random sample of the new forms that must pass before any model is queried; then one run per model with a 768-token budget and the boxed-answer parser from the start.

## 4. Sampling

Frame: GSM8K test split, N = 1,319 (same file and gold-answer rule as the first audit). The first audit's 200 parents (data/gsm8k_parents_200.csv) are included. Sampling: `numpy.random.default_rng(20261025)`, 600 further indices drawn without replacement from the 1,119 items not in the first audit, in the order implemented in `code/paper10_sample_extension.py`. A simple random sample of 200 followed by a simple random sample of 600 from the rest is a simple random sample of 800, so the finite-population correction is 1 - 800/1319 = 0.393. The list is frozen in `data/gsm8k_parents_800.csv` before any drafting.

New fresh forms are drafted for all 800 parents, including the 200 audited before. This keeps one drafting process, one set of rules and one token budget across the whole audit. The first audit's results are not pooled into the primary analysis. They are used in the replication check of Section 11.

## 5. Matched forms and mechanical checks

K = 2 fresh forms per parent, drafted by a language model from a provider and family different from every audited model, as for the first audit. The rules: change names, entities and sentence structure; preserve every numeric quantity, the logical structure, the units and the gold answer; add no hint and add or remove no reasoning step; the two fresh forms differ from the original and from each other. Drafting is done in batches by independent instances of that language model that see the rules and a few worked examples and never see model output of any kind. The model versions are recorded in AUDIT_LOG.md.

Mechanical verification runs on every form before any human reading and before any model query (`code/paper10_verify_extension_items.py`). A form that fails is redrafted and rechecked, and the failure is logged. The checks:
1. the multiset of numeric tokens equals the original's;
2. the stated gold answer is unchanged;
3. token Jaccard overlap with the original is below 0.65 for each fresh form (the first audit's second variants peaked at 0.657, and its first variants had median 0.684);
4. the two fresh forms of a parent have Jaccard overlaps to the original that differ by at most 0.15, so neither is a light copy and the other a deep rewrite (in the first audit the mean overlap was 0.664 for variant 1 and 0.392 for variant 2);
5. the two fresh forms have Jaccard overlap below 0.80 to each other;
6. the length ratio to the original is between 0.60 and 1.60;
7. no form is identical to the original or to the other fresh form.

Variant order is randomized per parent when the bank is assembled.

## 6. Private control bank

300 newly composed, never-public arithmetic word problems at GSM8K difficulty, each with a public-like first form and two fresh forms under the same rules and the same mechanical checks 1 to 7. Each item is checked against the GSM8K test split and, when the file can be fetched, the train split, and any item with token Jaccard 0.60 or more to a GSM8K item is replaced. The first audit's 60-item control bank is not reused (it passes checks 3 and 5: its largest fresh-form overlap is 0.60). The bank stays private until scoring completes.

**An optional human-written stratum.** In the first audit and here the public-like control form is written by the language model, so the control gap b_C compares model-written with model-rewritten text, while the benchmark gap compares human-written originals with model rewrites, and the transport radius carries that difference. If the authors write 60 or more never-public problems before the bank is frozen, they form a registered stratum, drafted into forms by the same rules, and the paper reports the between-stratum difference in b_C for each model. If they do not, the paper states the limitation.

## 7. Reading gate, before any model is queried

A human reading of the new forms is a precondition for running the audit. The order is fixed: mechanical check, freeze and hash, human reading, then the model runs. No model sees any item of the new audit or control bank until the reading has passed.

The reading is done by the two authors independently, using the packet format and rubric of `HUMAN_RATING_PROTOCOL.md`, with seeded defects mixed in. The sample is 300 audit fresh forms drawn at random from the 1,600 (stratified by variant slot), 100 control fresh forms, and every form that failed the mechanical check and was redrafted. A consensus defect is one both raters mark. Rule: with 0 or 1 consensus defects in the 300 audit forms the bank passes and the defect rate is reported with its exact 95% upper limit. With 2 or 3, the defective forms are redrafted, a further random sample of 150 is read, and the bank passes only if the new sample adds none. With 4 or more, the drafting batches containing the defects are redrafted and the reading repeated on a fresh sample. Each rater must catch at least 14 of 16 seeded defects or that rater's ratings are repeated. The control bank is held to the same rule on its 100 forms. The rating distributions are compared with those of the existing-bank packet, which the raters rated after seeing results, to see whether knowledge of results moved them.

## 8. Models, prompt, decoding, scoring

The five models of the first audit at the same pinned revisions (Qwen2.5-1.5B-Instruct, Qwen2.5-7B-Instruct, Phi-3-mini-4k-instruct, OLMo-2-1124-7B-Instruct, SmolLM2-1.7B-Instruct). The same prompt, the model's chat template, greedy decoding, float16 weights. The generation budget is 768 new tokens and the parser is the amended one that also accepts a boxed answer, both from the start. Exact numeric match, one evaluation per form. The inference engine and version are recorded before the first run and are the same for every model.

## 9. Inference, fixed in advance

Per model, with D_i in [-1, 1] over the 800 parents:
- Point estimate: the sample mean. Wald interval with the finite-population correction, Hoeffding interval, and empirical Bernstein interval reported beside them.
- **Guardrail, stated exactly.** The Wald interval is primary for Delta unless fewer than 200 parents are audited or fewer than 30 sampled parents have a nonzero gap, in which case the Hoeffding interval is primary. The control component follows the same rule: its Wald interval is used unless fewer than 200 control parents are used or fewer than 30 have a nonzero gap, in which case the Hoeffding interval is used.
- **Sensitivity interval, two constructions, both reported.** (a) Proposition 3b: because the audit parents and the control parents are independent samples, one interval on Delta minus b_C with the two variances added, Delta-hat - b_C-hat +/- z_{1-alpha/2} sqrt(Var(Delta-hat) + Var(b_C-hat)) +/- rho, with the finite-population correction on the audit variance. When the guardrail applies to either component, (a) falls back to (b). (b) Proposition 3 as in the first audit: the union of the two component intervals each at alpha/2, where a component is the Wald interval or, where the guardrail applies to it, the Hoeffding interval at alpha/2. Proposition 3b is new for this audit, is proved in the paper's appendix, and is approximate because it uses Wald intervals. It is the registered claim-rule construction. Proposition 3 is reported beside it.
- Radius grid {0, 0.01, 0.02, 0.05, 0.10}, headline radius 0.02.
- **Claim rule:** a model is reported as showing an exposure-consistent public-form advantage only if the primary interval for Delta excludes zero and the Proposition 3b sensitivity interval at 0.02 excludes zero, both at the 95% level. The same rule with Proposition 3 in place of 3b is reported beside it.
- **Multiplicity.** The five models form one family. No further adjustment is applied to the claim rule, because its simulated false-claim rate is at most 0.7% per model (Section 10), so the family-wise rate over five models is at most 3.5%, below 0.05. A Holm correction across the five models is applied to the PaCoST-style p-values and to every other test-based secondary result. The Bonferroni-adjusted claim rule (alpha 0.01 per model) is reported as a sensitivity result.
- **Deliverables per model, whatever the claim rule says:** the interval for Delta, the interval for Delta - b_C, the upper 95% limit of the sensitivity interval for tau at 0.02, and the tipping radius, the smallest rho at which the sensitivity interval includes zero.
- **How a significant gap is read.** A primary interval that excludes zero while the Delta - b_C interval includes zero is ordinary form mismatch, reported as that. A negative Delta, meaning the rewrites are easier than the originals, is reported as a rewrite-difficulty finding that bears on the matched-form assumption, not as evidence about contamination. A positive Delta - b_C that exceeds rho* is reported as a gap not explained by ordinary mismatch under the stated radius, not as proof of exposure.

## 10. What the claim rule can and cannot find, stated before the data

From the paper's power simulation (resampling the first audit's observed gaps, planting an advantage in a random share of parents that show none; `code/paper10_claim_rule_power.py`, grid in `results/power/extension_design/`), for GSM8K with 800 audited parents and a control bank of 300:

| Planted advantage | Proposition 3b (registered rule) | Proposition 3 |
|---:|---:|---:|
| 5 points | 33% | 8% |
| 10 points | 95% | 75% |
| 15 points | 100% | 99.6% |
| 0 (nothing planted) | at most 0.7% | at most 0.1% |

If the control-bank guardrail binds for a model, that model's rule falls back to Proposition 3 with a Hoeffding control component and its power is much lower. The paper will say that, per model, after the data are in.

What a null means. A visible public-form advantage of 10 points is what the paper's four-model positive control would produce from about 43 points of gain on the leaked wording, because only about 23% of such a gain is visible to a paraphrase audit. A null from this audit therefore rules out a 10-point visible advantage with about 95% power, and, for contamination like the planted kind, a gain of roughly 40 points or more on the leaked wording. It says much less about smaller effects. The paper will state this whatever the result.

## 11. Registered secondary analyses

1. **Replication on the first 200 parents.** For the 200 parents in both audits, the correlation between per-parent gaps from the two independently drafted fresh-form sets, and the paired difference in Delta-hat per model with a bootstrap interval over parents. This measures how much a result depends on which rewrites were drawn.
2. **Block analysis.** Delta-hat separately for the 200 earlier parents and the 600 new parents.
3. **Exact randomization test** (Appendix B.2 of the paper), reported as before: a non-rejection strengthens a null, a rejection is not read as a positive finding.
4. **Baselines on the same forms:** the fresh-form score (Clean-Eval-style) and the PaCoST-style paired confidence test, Holm-corrected across the five models.
5. **Placebo-label identity** on every control parent.
6. **Rewrite depth.** Delta-hat against token Jaccard to the original, now for both variants.
7. **Between-stratum b_C** if the optional human-written stratum exists.

## 12. Deviations and reporting

Every deviation is listed. A run that fails for an infrastructure reason is rerun unchanged and the failure is logged. Item-level outputs are never edited and no form is removed after the models are queried. All results are reported, nulls included.

## 13. Order of events and hashes

1. This file's SHA-256 is recorded in AUDIT_LOG.md. 2. The parent list is drawn and frozen. 3. Forms are drafted and mechanically verified. 4. The banks are frozen and hashed. 5. The human reading takes place and its result is recorded. 6. Only then are the models run, privately on Kaggle. 7. The analysis script `code/paper10_analyze_extension.py` is written before step 6 and run once.


---

## Amendment 1 (23 October 2026, before any model was queried on the new banks)

Made after an independent referee review of the registration. Each change answers a specific finding. Where a finding changes the registered text above, this amendment supersedes it. All simulation outputs are in `results/power/amendment1/`, produced by `code/paper10_claim_rule_power.py` (options `--mode independent --control-guardrail --control-branch bernstein`, 4,000 simulated audits per cell, GSM8K, 800 audited parents, 300 control parents), resampling the first audit's per-parent gaps.

**A1. Multiplicity: Bonferroni is the primary claim rule.** Section 9 argued that no correction was needed because the rule's simulated false-claim rate is at most 0.7% per model. That rate was measured with nothing planted and the benchmark's ordinary form gap equal to the control gap, which is the interior of the null set. The null set of the claim rule is tau at or below zero with |b_B - b_C| at most 0.02, and its edge is where the transport radius is used up. At the edge (nothing planted, the control mean set so that E[Delta-hat - b_C-hat] = 0.02, option `--boundary-rho 0.02`) the unadjusted Proposition 3b rule claims in 2.9% of audits per model, and in 6.7% when the mismatch is 0.03. Over five models the family-wise rate then exceeds 0.05. The primary claim rule is therefore **Proposition 3b with a Bonferroni correction across the five models: every interval used in the claim decision is built at alpha = 0.01, the sensitivity interval included**. The edge rate is then 0.7% per model (at most 3.5% over five models), and 2.1% per model at a 0.03 mismatch. The unadjusted 95% rule is reported as a secondary result. Holm still applies to every other test-based secondary result.

**A2. The detection table of Section 10 is replaced.** Proposition 3b at the Bonferroni level, with the empirical Bernstein branch of A3 where the control guardrail binds. Pooled over the five models' first-audit gap distributions:

| Planted visible advantage | Benchmark's ordinary gap equals the control's | Benchmark's ordinary gap 0.02 below the control's |
|---:|---:|---:|
| 5 points | 15.5% | 2.9% |
| 10 points | 85.9% | 57.2% |
| 15 points | 99.9% | 98.9% |
| 20 points | 100% | 100% |

The 95% figure for ten points in Section 10 is withdrawn: it assumed no correction and a transport assumption that holds exactly. The pooled table also overstates what two of the models can do (A3).

**A3. Per-model power and the sparse control branch.** In the first audit the control bank's nonzero-gap counts were 12, 22, 3, 14 and 4 of 60 for OLMo-2-7B, SmolLM2-1.7B, Phi-3-mini, Qwen2.5-1.5B and Qwen2.5-7B. The guardrail (fewer than 30 nonzero gaps) will probably bind on a 300-item bank for Phi-3-mini and Qwen2.5-7B. The control component on the guardrail branch is the **empirical Bernstein interval at alpha/2** (Proposition 5, the branch the paper recommends); the originally registered Hoeffding fallback is reported beside it. The change matters: with the Hoeffding fallback the rule detects almost nothing for these two models even at a twenty-point advantage (Phi-3-mini: 0.1% with Hoeffding, 64.5% with Bernstein). Detection of the full claim rule by model, ordinary gaps equal, Bonferroni, 300 control items:

| Model | nothing planted | 5 pts | 10 pts | 15 pts | 20 pts | 30 pts |
|---|---:|---:|---:|---:|---:|---:|
| OLMo-2-7B | 0.1% | 14.5% | 88.6% | 100% | 100% | 100% |
| SmolLM2-1.7B | 0.2% | 8.3% | 55.6% | 96.2% | 100% | 100% |
| Phi-3-mini | 0.0% | 0.0% | 0.1% | 0.4% | 64.5% | 100% |
| Qwen2.5-1.5B | 0.0% | 9.6% | 75.2% | 99.6% | 100% | 100% |
| Qwen2.5-7B | 0.0% | 0.6% | 1.8% | 1.7% | 47.9% | 100% |

For Phi-3-mini and Qwen2.5-7B the registered rule detects a visible advantage only at about twenty points or more, because the width of the control component, not the audit sample, limits it. This is accepted as the registered design and is not changed after seeing the first audit. The paper will state, per model and once the data are in, whether the control guardrail bound. For a model where it did, a claim-rule null will be reported as ruling out only advantages of about twenty-five points or more, and the model's primary interval and its difference Delta-hat minus b_C-hat are reported in full so the reader can see what the data show. The deliverables of Section 9 are reported for every model regardless of what the rule does.

**A4. Freeze, redraft, re-freeze.** If the reading gate sends forms back for redrafting, the redrafted forms are read by both raters under the same rubric and the bank is frozen again as version 2 with a new hash. The version 1 hash stays in the log. No model is queried until every form in the bank has either passed the gate or been re-read after redrafting.

**A5. Replication check, Section 11.1.** The first audit used a 320-token budget for OLMo-2-7B, SmolLM2-1.7B and Phi-3-mini. For those three models the comparison between the first audit and this one is confounded by the budget and is reported as such. For the two Qwen models the first audit's 768-token reruns are used.

**A6. What a visible advantage means.** The statement in Section 10 that a ten-point visible advantage corresponds to about 40 points of gain on the leaked wording is withdrawn. It divided by the pooled visible share and assumed every audited parent is leaked. The four-model positive control (Study 9) gives per-model visible shares from -18% (StableLM-2-1.6B) to 68% (SmolLM2-1.7B), and the interval for the pooled share is wide. A ten-point visible advantage is therefore consistent with a gain on the leaked wording of about 15 points (a SmolLM2-like model), about 40 points (the pooled estimate), or no upper bound (a model whose visible share is near zero). The paper will say "20 points or more, possibly unbounded" where it previously said "roughly 40 points".

**A7. Disputed published answers.** Seven parents are scored against a published answer the drafters believe is wrong or arguably ambiguous (`extension/gold_disagreements.csv`). The mechanical verifier skips the answer check for those seven only. Their forms are still scored against the published answer, and a parent can contribute a gap only if a model answers one form differently from another. The primary analysis keeps them. A sensitivity analysis without the seven is reported.

**A8. The reading and its limits.** The seeded defects in the packets are of two gross kinds (a changed quantity and a dropped sentence), so the seeded-catch check does not test the raters on subtle changes of reasoning. A third rater from outside the author team on 100 of the rows is recommended and, if done, reported separately. The optional human-written control stratum of Section 6 is recommended and not required. If it is not done, the paper states that the control gap compares model-written with model-rewritten text, so the transport radius carries the whole difference between that and the benchmark's human-written originals.

**A9. Recorded deviations.** One control drafting batch (batch 07) was rewritten while the banks were being assembled, and four frozen control prompts differ from the drafter's final file (see the audit log). A line in the Study 9 pooling script that drops draws with pooled DiD public at or below 0.05 from the ratio is not in the Study 9 registration. It affects one of 20,000 draws and changes no reported number.


---

## Amendment 2 (23 October 2026, before any model was queried on the new banks and before any added control item was drafted)

Two things are done here. The first corrects the simulation that Amendment 1 relied on. The second changes the design in response to what the corrected simulation shows.

**B1. Correction to the Amendment 1 simulations.** The simulations behind Amendment 1 drew the audited parents with replacement from the first audit's gap distribution, so the true sampling variance of Delta-hat was Var/n. The registered intervals use the finite-population correction (the audit is 800 parents drawn without replacement from the 1,319 test items), so under that simulation the rule's interval was too narrow and the false-claim rates it reported were too high. The power script now has `--finite-frame`: each simulated audit draws a fresh frame of 1,319 gaps from the pooled distribution, samples 800 without replacement, and places the control mean relative to that frame's mean. All numbers below come from this version (`results/power/amendment2/`, 4,000 simulated audits per cell). The following Amendment 1 figures are superseded:

| Amendment 1 figure (300 control items) | Corrected |
|---|---|
| Unadjusted rule, false-claim rate at the edge, mismatch 0.02 | 1.3% per model (was 2.9%) |
| Unadjusted rule, mismatch 0.03 | 3.4% (was 6.7%) |
| Bonferroni rule at the edge, mismatch 0.02 | 0.2% per model (was 0.7%) |
| Bonferroni rule, mismatch 0.03 | 0.7% (was 2.1%) |
| Pooled power at 10 points, equal ordinary gaps | 88.7% (was 85.9%) |
| Pooled power at 10 points, benchmark gap 0.02 below control | 58.5% (was 57.2%) |

The decision in A1 stands: at the edge the unadjusted rule has a one-sided nominal rate of 2.5% per model, so over five models the family-wise rate can exceed 0.05 (1.3% per model in this simulation is 6.3% family-wise), and the Bonferroni rule is the primary claim rule. The per-model finding of A3 also stands at 300 control items: ten-point power is 92.2% (OLMo-2-7B), 56.5% (SmolLM2-1.7B), 0.1% (Phi-3-mini), 77.8% (Qwen2.5-1.5B) and 1.8% (Qwen2.5-7B). The rest of A3 (the empirical Bernstein branch for a sparse control bank) is unchanged.

**B2. The control bank is enlarged from 300 to 900 items.** At 300 items the control bank has too few nonzero gaps for Phi-3-mini and Qwen2.5-7B (3 of 60 and 4 of 60 in the first audit, so about 15 and 20 of 300), the nonzero-gap guardrail binds, and the claim rule detects nothing below about twenty points for those two models. With 900 items the expected number of nonzero gaps is about 45 and 60, the guardrail does not bind, and the rule has near-full power at ten points for all five models. Simulated claim-rule rates, Bonferroni (alpha 0.01 per model), 800 audited parents:

| Control items | Pooled, 10 points, equal ordinary gaps | Pooled, 10 points, benchmark gap 0.02 below control | Edge false-claim rate, mismatch 0.02 | Edge, mismatch 0.03 |
|---:|---:|---:|---:|---:|
| 300 | 88.7% | 58.5% | 0.2% | 0.7% |
| 900 | 99.8% | 93.2% | 0.4% | 1.8% |

| Model (equal ordinary gaps, Bonferroni) | 5 pts, 300 items | 10 pts, 300 items | 5 pts, 900 items | 10 pts, 900 items |
|---|---:|---:|---:|---:|
| OLMo-2-7B | 11.6% | 92.2% | 31.4% | 99.8% |
| SmolLM2-1.7B | 5.5% | 56.5% | 14.5% | 95.0% |
| Phi-3-mini | 0.0% | 0.1% | 66.8% | 99.9% |
| Qwen2.5-1.5B | 6.1% | 77.8% | 14.0% | 99.0% |
| Qwen2.5-7B | 0.7% | 1.8% | 49.4% | 100% |

With 900 items the Bonferroni edge false-claim rate over five models is at most about 2% at a mismatch of 0.02 (five times 0.4%) and about 9% at 0.03, which lies outside the registered null. The unadjusted rule at 900 items has an edge rate of 1.8% per model (6.0% at 0.03). These figures come from the first audit's gap distributions at a 320-token budget for three models. The real gaps under the 768-token budget may differ, so the paper reports per model whether the control guardrail bound.

The 600 added items are composed by the drafting procedure of the first 300: `extension/DRAFTING_INSTRUCTIONS.md`, unchanged, the same mechanical checks 1 to 7, the same novelty check against the GSM8K test and train questions. The specification is the same 10 structures, each with the same step and answer-type pattern, crossed with 60 settings that are all different from the first 30 (`code/paper10_make_control_addendum_batches.py`, `default_rng(20261029)`), identifiers `gsmctl_ext_301` to `gsmctl_ext_900`, 20 drafting batches (11 to 30) of 30 items. The first 300 items and their frozen file are not touched: `extension/frozen_banks/gsm8k_control_bank.csv`, SHA-256 `b47e55d96a7ea427e9d3a16a954326bcdfc50bae54ae0270ffc7842d0fa92bee`, stays as it is. The added items are frozen as a separate file, `extension/frozen_banks/gsm8k_control_bank_addendum.csv`, with its own SHA-256 recorded in the audit log and the manifest. The audit set is the union, 900 items and 2,700 forms. The assembly check that no two public-like forms overlap at token Jaccard 0.60 or more is run on the union.

**B3. Reading gate for the added items.** The order of Section 7 applies to the addendum: mechanical check, freeze and hash, human reading, then model runs. Both authors read, independently and under the same rubric, a random sample of 150 of the 1,200 added fresh forms (stratified by variant slot) with 8 seeded defects mixed in. Rule: 0 or 1 consensus defects in the 150 and at least 7 of 8 seeded defects caught by each rater passes the addendum and the defect rate is reported with its exact 95% upper limit. With 2 or 3, the defective items are redrafted, 100 further forms are read, and the addendum passes only if the new sample adds none. With 4 or more, the drafting batches containing the defects are redrafted and the reading repeated on a fresh sample. A redrafted addendum is frozen again as version 2 with a new hash and the version 1 hash stays in the log (A4). The reading of the original 300 control items proceeds as already registered.

**B4. Evaluation and cost.** Every model is evaluated on the 2,400 audit forms and the 2,700 control forms, 5,100 forms per model instead of 3,300. At the measured throughput of about 1,150 forms per hour for a 7B model on the two-GPU setting, this is roughly 15 GPU-hours for the five models. The evaluation kernels are rebuilt on the final frozen files before any is pushed, and each Kaggle run is started only with the author's go-ahead.

**B5. What does not change.** The 800 audit parents and their frozen forms, the claim rule (Proposition 3b, Bonferroni across five models, Bernstein on the sparse control branch), the radius grid, the secondary analyses, the 768-token budget and the order of events. The Section 10 detection statement is replaced by the 900-item table above, with the per-model rows.


---

## Amendment 3 (23 October 2026, after the 600 added control items were drafted and before they were frozen, read or queried)

Records a check added to the registered procedure for the added control items, what it found, and the sensitivity analysis it adds.

**C1. Blind solve of every added form.** The registered checks (Section 5) include the drafter's own answer for each fresh form. One drafting batch (batch 13) filled that column by copying the public-like answer instead of solving each form, so for it the check was empty. Before the freeze, every form of the 600 added items (1,800 forms) was therefore solved blind by twelve separate solver instances (`code/paper10_solve_check.py`): each saw only problem text, no answer, and never two forms of the same item. A solver wrote AMBIGUOUS if two reasonable readings gave different answers, and a note where it made a judgment call. Result: 1,800 forms solved, 7 disagreed with the stated answer and 3 were marked ambiguous, touching 9 items (306, 334, 423, 487, 577, 761, 820, 824, 877).

**C2. What was found and fixed.** One was a solver error (306: a solver reported the total instead of the change; the question was reworded to "how much change"). Eight were wording defects in the drafts: 334 (fresh form 1 did not say the 400 meters carried were part of the distance), 423 (fresh form 2 asked how much "it" keeps, which could mean the bigger portion or the whole co-op), 487 (fresh form 1 said "3 batches" where the fee is per order), 577 (flat fee and mileage unclear whether per car or per trip, in the public-like form and both fresh forms), 761 (fresh form 1 said the pump "moves" water without saying out of the reservoir), 820 (fresh form 1 said "through day 11", which counts nine nights), 824 (the quantity was 7.5 gallons, so pro rata and whole-gallon readings differed, and the fresh forms leaned differently; the item was rebuilt with 160 students so the quantity is exactly 10 gallons), and 877 (fresh form 2 said "brings 3 bridesmaids", which makes four people, and the public-like form did not say the fee was per client). The nine items were edited before the freeze, as a redraft under A4, rechecked with the registered mechanical checks (all 20 batches and their union passed), and then all 27 forms were solved blind again by three further instances, each seeing one form type only: 27 of 27 agreed with the stated answers and none was marked ambiguous. In addition, item 486 was redrafted before this check because its public-like form overlapped first-bank item 006 at 0.62 (limit 0.60).

**C3. Judgment-call notes, and a sensitivity analysis.** Solvers also noted a judgment call on 53 forms whose answer nevertheless agreed with the stated one (41 items outside the nine; 32 of them noted on a single form). Typical notes: a rate read as continuous, stages read as sequential, a fee read as one per order, a person counted among those sharing. These are the ordinary ambiguities of word problems. An ambiguity on one form but not its siblings would produce a spurious public-minus-fresh gap in the control bank, which raises b_C-hat and makes the claim rule more conservative, never less. Fixed in advance: the primary analysis keeps every item, and a sensitivity analysis drops the 41 items listed in `extension/solve_check/noted_items.csv` (SHA-256 in the audit log) from the control bank and recomputes b_C, Delta-hat minus b_C-hat, and the claim rule. The first 300 control items had no blind solve, so the sensitivity analysis applies to the added 600 only, and the paper says so.

**C4. Limits.** The solvers are language-model instances, as the drafters were, so their agreement with the drafts is not a human check. The reading gate of Amendment 2 B3 still applies in full. The blind solve checks answers and wording-level ambiguity on the forms; it does not check that a fresh form tells "the same problem" as its public-like form beyond what shows up as a different solved answer.

**C5. Recorded deviations in drafting.** Five drafters (batches 12, 16, 22, 25, 28) reported that scratch files in the shared scratchpad were overwritten by other drafters' content and that they briefly saw part of another batch's working data (item identifiers or fragments); each reported not using it, and the union check found no overlap among public-like forms at or above 0.60 other than the one in item 486 (against first-bank item 006). Several drafters listed the names (not the contents) of other draft files. One batch (13) hard-coded two intermediate counts in `solution_expr` (items 768 and 818) because floor division is not allowed.


---

## Amendment 4 (23 October 2026, before any model was queried on the new banks)

Made after a second independent review of the manuscript and registration. No design change: it corrects which gap distributions the power simulations used, fixes a reading the registration left open, and states the claim rule as it is implemented.

**D1. Power simulations recomputed at the extension's token budget.** The simulations of Amendments 1 and 2 resampled the first audit's gaps at a 320-token budget for all five models. The extension runs at 768 tokens, and the first audit has 768-token reruns for the two Qwen models (Amendment 1 of the first audit). `code/paper10_claim_rule_power.py --qwen-768` takes the Qwen models' gaps from those reruns and the other three models' from the first audit (no 768-token pilot exists for them); outputs are in `results/power/amendment4/`. The 768-token Qwen gaps are much sparser (Qwen2.5-7B: 16 of 200 audit parents and 0 of 60 control items with a nonzero gap; Qwen2.5-1.5B: 64 of 200 and 4 of 60). Changes to the figures of B2 (Bonferroni, 800 audited parents):

| Quantity | Amendment 2 (Qwen at 320 tokens) | Amendment 4 (Qwen at 768 tokens) |
|---|---:|---:|
| Ten-point power with 300 control items: Qwen2.5-1.5B | 77.8% | 0.5% |
| Ten-point power with 300 control items: Qwen2.5-7B | 1.8% | 0.0% |
| Ten-point power with 300 control items: pooled, equal ordinary gaps | 88.7% | 92.3% |
| Ten-point power with 900 control items: Qwen2.5-1.5B | 99.0% | 97.7% |
| Ten-point power with 900 control items: Qwen2.5-7B | 100% | 100% |
| Ten-point power with 900 control items: pooled, equal ordinary gaps | 99.8% | 100.0% |
| Ten-point power with 900 control items: pooled, benchmark gap 0.02 below control's | 93.2% | 96.8% |
| Edge false-claim rate, unadjusted, 300 / 900 items | 1.3% / 1.8% | 1.1% / 1.7% |
| Edge false-claim rate, Bonferroni, 900 items | 0.4% | 0.3% |

The other three models' rows are unchanged. The decision of Amendment 2 stands and is strengthened: with 300 control items three models (Phi-3-mini 0.1%, Qwen2.5-1.5B 0.5%, Qwen2.5-7B 0.0%) would have had almost no power at ten points, and with 900 every model has about 95% or more (lowest: SmolLM2-1.7B, 95.0%). The paper reports the Amendment 4 figures.

**D2. The control guardrail may bind.** At 768 tokens Qwen2.5-7B had no nonzero control gap in 60 items, and 3 of 60 for Phi-3-mini at 320 tokens, so the true rates are uncertain and the guardrail (fewer than 30 nonzero gaps in the control bank) may bind for either model, or for Qwen2.5-1.5B, with 900 items. Where it binds the control component is the empirical Bernstein interval of A3 and the simulations above already use it. The paper reports per model whether it bound.

**D3. A reading for a difference below minus the radius.** Section 9 registered readings for a negative Delta-hat and for a positive Delta-hat minus b_C-hat above rho*. It did not cover a Delta-hat minus b_C-hat well below zero. In the first audit's 768-token rerun Qwen2.5-1.5B has Delta-hat = -0.040 on 200 parents and b_C-hat = +0.058 on 60 control items, so Delta-hat minus b_C-hat = -0.098, with a 95% Proposition 3b interval of [-0.177, -0.020]. Registered now, before any run: if the interval for Delta minus b_C lies wholly below -rho* (that is, the upper end of the sensitivity interval at rho* is below zero), the paper reports that the control bank's ordinary form gap exceeds the benchmark's by more than the radius for that model, so the transport assumption fails in the conservative direction. This is not evidence about exposure, the claim rule does not fire, and the control gap is not used as a proxy for that model. The model's upper limit for tau at rho* and the tipping radius are still reported.

**D4. The claim rule as implemented.** The registered claim rule is one-sided: a model is reported as showing an exposure-consistent public-form advantage only if Delta-hat is positive, the primary interval for Delta excludes zero, and the lower end of the Proposition 3b sensitivity interval at rho* = 0.02 lies above zero, all at the Bonferroni level (alpha = 0.01 per model) as the primary reading and at 0.05 as the secondary one. `code/paper10_analyze_extension.py` implements exactly this.

**D5. Notes for transparency.** The mechanical answer check skips the seven parents with a disputed published answer (A7). The preparation deviations of the audit log are listed in the paper's Appendix B.9.
