# CleanScore Study 8: replication across training seeds, run under an explicit override

DRAFT REGISTRATION. Nothing has been trained for this study.

## 1. This breaks a stopping rule on purpose, and says so

Studies 1, 2, 3 and 6 each forbid additional seeds by name. Study 6 further
declares itself the last study on ARC whatever it finds. This study runs three
additional training seeds of Study 6. It therefore breaks those rules, and it is
not an interpretation of them.

The decision was taken by the authors after an external review observed that
every interval on a positive-control effect is bootstrapped over parents and so
captures item sampling and nothing else, leaving optimisation variability
unmeasured. The authors judged the missing robustness check more valuable than
the rule, and the override is recorded here, in the audit log, and in the paper
so that a reader weighs it rather than discovers it.

What the rules were protecting against is repetition until a convenient answer
appears. The commitments in Section 3 are what stand in for the rule now, and
they are stricter in the only direction that matters: every seed is reported, no
seed may be excluded for any reason, and the single-seed result already in the
paper stays exactly as it is.

## 2. Design

Three additional training seeds, run against Study 6's configuration in every
other respect: the same base model and revision, the same exposure format ending
in the correct option's text, the same 1,000-record mixture, three epochs,
learning rate 2e-5, batch size 2 with gradient accumulation 8, Adafactor,
sequence budget 256, and the complete deep-paraphrase bank covering all 200
parents.

**The exposure assignment does not vary.** The same 100 parents are leaked in
every seed, drawn once with `default_rng(20260824)`. Which items are leaked is
what the parent bootstrap already varies; what it cannot vary is the training
run, so that is the only thing changed here. The seed governs the trainer and the
order of the mixture.

The clean audit is not rerun. It is deterministic and Study 6 archived it.

Seeds: 20260828, 20260829, 20260830. Fixed here before any of them is run.

## 3. Commitments that replace the rule

1. **All three seeds are reported**, in a table, with their individual estimates,
   whatever they show. No seed is dropped for any reason including a failed
   manipulation check.
2. **The headline becomes the four-seed spread**, not a selected seed. Study 6's
   seed is one of the four and carries no special status in the pooled summary,
   though it remains separately reported as the registered single-seed result.
3. **A failed manipulation on any seed is reported as such** and is included in
   the spread rather than excluded from it.
4. **No fourth attempt.** If these three produce an inconvenient picture, that
   picture is what the paper reports. There is no seed budget left after this.

## 4. Interpretation, fixed before the data exist

Let the four public-form effects be the three new seeds plus Study 6's.

- **All four within 0.10 of each other**: optimisation variability is small
  relative to the planted effect, the parent bootstrap was not badly
  understating uncertainty, and Sections 7.13 and 7.14 stand as written with the
  spread reported beside them.
- **Spread comparable to the effect itself**: the single-seed intervals in
  Sections 7.13 and 7.14 understate uncertainty substantially. Those sections
  keep their point estimates and gain the across-seed range as the honest
  interval, and the abstract is rewritten to quote the range.
- **Any seed failing its manipulation check**: the effect is not reliably
  implantable at this dose, which would qualify every ARC conclusion in the
  paper. Reported prominently rather than as a footnote.
- **The deep-paraphrase arm crossing zero on any seed**: Section 7.14's central
  claim, that contamination reaches wording the model never saw, is reported as
  holding on some seeds and not others, and the abstract is narrowed accordingly.

The last two outcomes would weaken the paper's strongest results. They are
registered because a replication that can only confirm is not a replication.

## 5. Non-claims

Three extra seeds bound optimisation variability for one model, one dose and one
benchmark. They say nothing about variability across models, and nothing about
whether the effect would survive a different fine-tuning procedure.
