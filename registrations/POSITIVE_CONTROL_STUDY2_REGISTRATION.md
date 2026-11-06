# Positive Control, Study 2: Registered Protocol

Registered 2026-08-22, before the second exposed model was trained and before
any audit item was scored against it.

## 1. Why a second model

Study 1 contaminated Qwen2.5-1.5B-Instruct with the public forms of a hundred
audited GSM8K parents and measured where the effect went, using the hundred
unexposed parents as a control for the general effects of fine-tuning. The
difference-in-differences estimates were +0.241 on the leaked wording and
+0.176 on paraphrases the model never saw, both with intervals excluding zero,
leaving +0.065 visible as a public-form gap. The transferred share is estimated
at 73% with a bootstrap interval of [19%, 168%].

Two things are unresolved. The interval on the share is wide, and the result
rests on one model, so it cannot distinguish a property of contamination from a
property of Qwen2.5-1.5B.

## 2. Design

Identical to Study 1 in every respect except the base model:
HuggingFaceTB/SmolLM2-1.7B-Instruct, revision
31b70e2e869a7173562077fd711b654946d38674, which is in the audited panel so its
clean audit is on record in Table 2 (Delta-hat = +0.045, half-width 0.058).

Same hundred exposed parents from the same frozen assignment file, same hundred
unexposed controls, same nine hundred background records, same seed, same
three epochs at learning rate 2e-5, full-parameter float32 training sharded
across both accelerators, same evaluation script, same bank, same analysis.

Using the same exposure assignment is deliberate: it makes the two studies
comparable item by item and means the second study is a replication rather than
a fresh draw.

## 3. Primary outcome, fixed now

The difference-in-differences transfer estimate for SmolLM2-1.7B:

    DiD_public = (public accuracy change on exposed parents)
                 - (public accuracy change on unexposed parents)
    DiD_fresh  = (fresh accuracy change on exposed parents)
                 - (fresh accuracy change on unexposed parents)

reported with bootstrap intervals over parents, together with the transferred
share DiD_fresh / DiD_public.

## 4. Secondary outcomes, fixed now

1. The pooled transfer estimate across both models, with its interval.
2. Whether the registered claim rule of the main audit fires for the exposed
   model, and the whole-bank Delta-hat against the clean audit on record.
3. The manipulation check: public-form accuracy on the leaked items must rise
   by at least five points over the clean model, otherwise the run is reported
   as a failed manipulation and excluded from the pooled estimate.

## 5. What would falsify the Study 1 reading

If DiD_fresh for this model is near zero while DiD_public is clearly positive,
the transfer seen in Study 1 is specific to Qwen2.5-1.5B and the paper will say
so, reporting the two models separately and withdrawing any general claim about
transfer.

## 6. Stopping rule

One run. No dose escalation, no model substitution, no second seed. The result
is reported whatever it shows, and the pooled estimate is computed over exactly
the two studies regardless of whether the second agrees with the first.

## 7. Non-claims

Two models are not a survey. Nothing here estimates how much contamination
exists in released models, and the transferred share measured under deliberate
fine-tuning need not equal the share under whatever process contaminates models
in the wild.
