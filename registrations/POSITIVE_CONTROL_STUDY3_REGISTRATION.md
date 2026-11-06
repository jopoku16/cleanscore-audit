# Positive Control, Study 3: Registered Protocol

Registered 2026-08-23, before either model was trained and before any audit item
was scored against either.

## 1. Why two more models

Studies 1 and 2 estimate the effect of leaking an item's public wording using
the unexposed half of the bank as a control. Study 1, on Qwen2.5-1.5B, gives
difference-in-differences estimates of +0.240 on the leaked wording and +0.175
on paraphrases the model never saw, both excluding zero. Study 2, on
SmolLM2-1.7B, gives +0.100 and +0.040, in the same direction and neither
excluding zero. Pooled, both components exclude zero.

The finding is therefore supported and not established: it rests on one
significant study, one inconclusive study, and significance only on pooling.
Two additional models give four independent estimates, which is enough to say
whether the direction is consistent across model families rather than a property
of one.

## 2. Models

Chosen because they are ungated, they fit full-parameter float32 training across
the two available accelerators, and they come from two families not yet used:

- allenai/OLMo-2-0425-1B-Instruct, revision
  48d788eca847d4d7548f375ad03d3c9312f6139e
- stabilityai/stablelm-2-1_6b-chat, revision
  f3fe67057c2789ae1bb1fe42b038da99840d4f13

With Qwen2.5-1.5B and SmolLM2-1.7B this gives four families: Qwen, SmolLM2,
OLMo and StableLM.

Neither model is in the audited panel of Section 7, so neither has a clean audit
on record. Each run therefore audits the base model first, then trains, then
audits the exposed model, all in one session with the unmodified evaluation
script and the unmodified bank.

## 3. Everything else is unchanged

Same hundred exposed parents from the same frozen assignment file, same hundred
unexposed controls, same nine hundred background records, same seed, three
epochs at learning rate 2e-5, full-parameter float32 sharded across both
accelerators, same evaluation settings, same analysis.

## 4. Primary outcome, fixed now

For each model, the difference-in-differences estimates

    DiD_public = (public accuracy change on exposed parents)
                 - (public accuracy change on unexposed parents)
    DiD_fresh  = (fresh accuracy change on exposed parents)
                 - (fresh accuracy change on unexposed parents)

with bootstrap intervals, and the four-model pooled estimate of each.

## 5. Secondary outcomes, fixed now

1. The count of models whose DiD_fresh point estimate is positive.
2. The four-model pooled transferred share with its interval.
3. The visible gap, DiD_public minus DiD_fresh, for each model. Studies 1 and 2
   gave +0.065 and +0.060 despite total effects differing by a factor of two and
   a half; whether that stability persists is recorded but was not predicted.
4. The manipulation check per model: the public-form difference-in-differences
   must reach +0.050, otherwise that model is reported as a failed manipulation
   and excluded from the pooled estimate, with the exclusion stated.

## 6. What would overturn the current reading

If two or more of the four models show a DiD_fresh point estimate at or below
zero while their DiD_public is clearly positive, the transfer seen in Study 1 is
not general and the paper will say so, reporting the models separately and
withdrawing the pooled claim.

## 7. Stopping rule

One run per model. No dose escalation, no model substitution, no additional
seeds, and no further models after these two whatever the outcome. The pooled
estimate is computed over exactly the studies whose manipulation check passes,
and the full set of runs is reported either way.

## 8. Non-claims

Four models remain a convenience sample of small open models trained by one
deliberate procedure. Nothing here estimates the transferred share under
whatever process contaminates models in the wild, and nothing here is a survey
of contamination in released models.
