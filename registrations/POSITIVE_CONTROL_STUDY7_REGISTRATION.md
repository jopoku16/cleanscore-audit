# CleanScore Study 7: a negative control on the fine-tuning procedure itself

DRAFT REGISTRATION. Nothing has been trained for this study and nothing scored.

## 1. What this is, and why it is not the thing the stopping rules forbid

A reviewer objected that the positive controls report intervals bootstrapped over
parents, which capture item sampling and nothing else. They do not capture
optimisation variability, they do not capture whatever a particular fine-tuning
run does to a model besides implanting the leak, and they do not capture
interference between parents that were trained on and parents that were not.
The objection is correct and the paper cannot answer it from the runs it has.

The obvious answer is more seeds. Every registration in this paper forbids that
by name: Studies 1, 2, 3 and 6 each say no additional seeds, and Study 6 says it
is the last ARC study whatever it finds. Those rules were written to stop an
experiment being repeated until it produced a convenient answer, and we are not
going to reinterpret four of them in a row. Section 4 says what we do instead.

What this study runs is not another positive control. It plants nothing. The
model is fine-tuned on the same mixture size, the same schedule, the same
optimiser and the same seed as Study 6, with the leak removed: all 1,000 training
records are background items, and no audited parent's wording appears anywhere.
The audit is then run exactly as before.

A run that plants nothing cannot be shopped for a favourable outcome, because it
has no favourable outcome available. It can only leave the paper as it is or
damage it. That asymmetry is why we judge it outside what the stopping rules
protect against, and we state the tension here rather than leaving a reader to
find it.

## 2. What it measures

Under the leak, Study 6's difference in differences on the public form was
+0.490. With the leak removed, the exposed and control halves are both untouched,
so the same statistic has nothing to detect and should be zero up to noise. Its
observed value is therefore an empirical null for the whole procedure: it
contains item sampling, optimisation variability, and any interference the
fine-tuning introduces between the two halves, none of which the parent bootstrap
can see.

Reported for each of the three form families:

1. The difference in differences with no leak present.
2. Its bootstrap interval over parents, for comparison with the same interval
   computed under the leak.
3. The change on the control parents, which says how much the fine-tuning moved
   the model in general.

## 3. Interpretation, fixed before the data exist

- **All three differences in differences within 0.05 of zero**: the procedure
  introduces no spurious effect at the size Study 6 reports, and the positive
  controls measure what they claim to measure. Study 6's +0.490 and +0.238 stand
  against an empirical null of approximately zero.
- **Any difference in differences beyond 0.05 in magnitude**: fine-tuning alone
  moves the statistic, the positive-control estimates are inflated or deflated by
  an amount this run measures, and every effect reported in Sections 7.11 to 7.14
  is reported with that offset stated beside it. We would not withdraw the
  studies, because the direction and size of the correction would be measured
  rather than guessed, but the abstract would carry it.
- **A difference in differences comparable to the planted effects**: the positive
  controls do not measure contamination and Sections 7.11 to 7.14 are withdrawn.

The third outcome would destroy the paper's central experimental contribution. It
is registered as a reportable outcome because a negative control that cannot fail
is not a control.

## 4. What we are not doing, and what the paper will say instead

We are not running additional seeds of any positive control. The registrations
forbid it and we keep them. The consequence is that optimisation variability
remains unmeasured for the positive controls, and the Limitations section will
say so in those words, together with the observation that a stopping rule written
to prevent outcome shopping also prevents replication, which is a real cost of
how we wrote them and a lesson for the next registration rather than a defence.

This study bounds the part of that concern that can be bounded without a second
seed: whether the procedure manufactures an effect when there is none to find.

## 5. Stopping rule

One run. No seeds, no variants, no repetition whatever it shows. If it fails for
infrastructure reasons it is repeated at the identical configuration and the
failure is logged.

## 6. Non-claims

This estimates nothing about contamination in any released model, and it does not
establish that the positive-control effects would replicate under a different
training seed. It measures whether the procedure produces an effect from nothing.
