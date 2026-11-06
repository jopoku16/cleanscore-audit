# CleanScore Real-Benchmark Audit: Registered Protocol

Registered 2026-08-21, before any audited model was queried with any audit item.
This document locks the design. Deviations must be reported as deviations.

## 1. Estimand

For each audited model m and benchmark B, the target is the finite-benchmark
public-form advantage Delta_N defined in the mathematical core: the mean over
benchmark parent items of original-form correctness minus mean fresh-form
correctness. The audit estimates Delta_N from a registered sample of n = 200
parent items per benchmark and reports the exposure-related component tau
only through the negative-control sensitivity interval with an explicit
transport radius. Each model-benchmark pair is a separate audit. No pooling
across models is a primary result.

## 2. Benchmarks and sampling frames

- Primary: GSM8K test split (openai/gsm8k, config "main"), N = 1319 parent
  items. Gold answer parsed from the "#### x" terminator, commas stripped.
- Secondary, held-out domain: ARC-Challenge test split (allenai/ai2_arc),
  restricted to items with exactly four answer options after mapping numeric
  labels 1-4 to A-D. Eligible frame: N = 1165.

Sampling: numpy default_rng(20260821); 200 indices drawn without replacement
from the GSM8K frame first, then 200 from the ARC eligible frame, in the order
implemented in the sampling script archived beside this document. Simple random
sampling, no strata. Sampled parent lists are frozen in
data/gsm8k_parents_200.csv and data/arc_parents_200.csv.

## 3. Matched forms

K = 2 fresh forms per parent item.

GSM8K rewrite rules: change names, entities, and sentence structure; preserve
every numeric quantity (as a multiset over digit tokens), the logical structure,
the units, and the final gold answer. No hints, no added or removed reasoning
steps. The two variants of a parent must differ from the original and from each
other.

ARC rewrite rules: rewrite the question stem only; the four options and the
answer key are kept verbatim and in the original order. The rewritten stem must
ask the same fact with the same required knowledge, with no option-word leakage
beyond what the original stem already contains.

Authoring protocol: variants are drafted by a language model from a
different provider and family than every audited model, under the written rules
above, then checked by a deterministic verification script
(code/paper10_verify_real_audit_items.py): numeric multiset preservation and
answer preservation for GSM8K; option/key integrity and stem dissimilarity for
ARC; length-ratio bounds 0.60-1.60 for rewritten text. Items failing
verification are rewritten before any model query. Human review by the authors
is recorded in the audit log. LLM-assisted authoring is disclosed in the
manuscript as a protocol property and a limitation.

Privacy: fresh forms and control banks are not posted publicly before scoring
completes. Evaluation runs use private Kaggle kernels.

## 4. Private negative-control banks

- GSM8K domain: 60 newly composed, never-public arithmetic word problems
  (public-like first form) each with 2 fresh forms under the same rewrite rules.
- ARC domain: 40 newly composed, never-public four-option science questions
  with 2 stem rewrites each.

Controls estimate the ordinary form gap b_C for each model under this writing
protocol. Because control items were never public, no audited model can have
seen them in training.

## 5. Models

All open weights, ungated, pinned revisions, evaluated as released (no
fine-tuning):

| Model | Revision |
|---|---|
| Qwen/Qwen2.5-1.5B-Instruct | 989aa7980e4cf806f80c7fef2b1adb7bc71aa306 |
| Qwen/Qwen2.5-7B-Instruct | a09a35458c702b33eeacc393d103063234e8bc28 |
| microsoft/Phi-3-mini-4k-instruct | f39ac1d28e925b323eae81227eaba4464caced4e |
| allenai/OLMo-2-1124-7B-Instruct | 470b1fba1ae01581f270116362ee4aa1b97f4c84 |
| HuggingFaceTB/SmolLM2-1.7B-Instruct | 31b70e2e869a7173562077fd711b654946d38674 |

OLMo-2 is included as the training-data-documented model: its pretraining and
post-training mixtures are public, which allows a qualitative cross-check of
any observed gap.

## 6. Querying and scoring

GSM8K: each item is presented once through the model's chat template as a
single user message:

    Solve the following math problem. Show your reasoning, then give the
    final answer on the last line in the form "The answer is <number>."

    <problem text>

Greedy decoding (do_sample=False), max_new_tokens = 320, float16 weights.
Scoring: the predicted answer is the number following the last occurrence of
"answer is" in the continuation; if absent, the last number token in the
continuation. Numbers are normalized (commas, "$", "%", trailing period
stripped; integer-valued floats equal integers). A continuation with no
parseable number scores incorrect and is retained. Exact numeric equality with
the gold answer scores 1, else 0.

ARC: no generation. For each of the four options, the score is the sum of
token log-probabilities of the option text conditioned on the chat-templated
question stem plus "Answer:", divided by the option's character length
(character-normalized). Predicted option = argmax; correctness = match with the
answer key. Unnormalized sum log-probability is recorded as a secondary
scoring; any disagreement between the two scorings is reported.

One evaluation per form. No repeated sampling, no prompt variation, no
post-hoc exclusions except a documented runtime failure of an entire batch, in
which case the batch is rerun; item-level outputs are never edited.

## 7. Inference

Per model-benchmark pair, with D_i in [-1, 1]:

- Point estimate: sample mean of D_i over the 200 sampled parents.
- Conservative interval: Hoeffding bound at alpha = 0.05.
- Practical interval: finite-population Wald interval with the finite
  population correction (N = 1319 or 1165).
- Guardrail (registered in the mathematical core): with n = 200, the Wald
  interval is primary unless fewer than 30 sampled parents have a nonzero gap,
  in which case the Hoeffding interval is primary and the Wald interval is
  descriptive.
- Control-bank interval for b_C: Wald with the control bank treated as the
  population of interest (no fpc), same alpha.
- Sensitivity interval for tau: Proposition 3 with alpha_Delta = alpha_C =
  0.025, reported over the transport-radius grid
  rho in {0, 0.01, 0.02, 0.05, 0.10}. The registered headline radius is
  rho* = 0.02.

Registered claim rule: a model-benchmark pair is reported as showing an
"exposure-consistent public-form advantage" only if the primary interval for
Delta excludes zero AND the sensitivity interval for tau at rho* = 0.02
excludes zero. All other configurations are reported descriptively. A null or
negative result is reported with the same prominence as a positive one.

Placebo check: the placebo-label identity is computed on every control-bank
parent per model; the mean placebo gap must be numerically zero up to floating
point when averaged over the label distribution.

Baseline comparisons on the same data: raw public-form score; Clean-Eval-style
fresh-form score (mean fresh-form accuracy); the unadjusted gap; and a
PaCoST-style paired comparison using the mean per-token log-probability of the
model's generated continuation (GSM8K) or of the chosen option (ARC) on
original versus fresh forms.

## 8. Deviations and reporting

Any deviation from this protocol is listed in a Deviations subsection of the
manuscript. Software or hardware failures are documented in the run manifest.
The audit is reported whether or not any gap is found.
