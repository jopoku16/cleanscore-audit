# CleanScore Positive Control, Study 6: the deep-paraphrase arm without a counterfactual to assume

DRAFT REGISTRATION. No item has been written for this study, nothing has been
trained, and nothing has been scored. When it is locked the date is recorded here
and the file does not change except by a dated amendment.

## 1. The flaw this fixes, and why naming it needs no data

Study 5 planted 49 points of contamination on ARC and showed the audit blind to
all of it. Its deep-paraphrase arm, the only one that could separate a memorised
answer string from transferred knowledge, was demoted to descriptive by a check
the registration attached to it, and that demotion was correct under the rule as
written.

The rule was badly written, and it is ours. The deep paraphrase existed for the
100 exposed parents and for only 25 of the 100 control parents, so the control
group had no deep-paraphrase change of its own and the analysis substituted the
control group's fresh-form change instead. That substitution needed an
assumption, the assumption needed a check, and the check ran on 20 parents. A
20-item comparison cannot resolve a 0.05 tolerance: the standard error of a
difference of two proportions on 20 paired items is around 0.1 whatever the
data say, so the gate fires or holds close to a coin flip regardless of whether
the assumption is true. That is arithmetic about the design, available before
the study ran and independent of anything it found.

The fix is not a bigger check. It is to remove what the check was checking.

## 2. The single change

Deep paraphrases are written for the 75 control parents that lack one, so that
all 200 audited ARC parents carry all three form types.

The estimate for the deep-paraphrase arm then becomes what the public and fresh
arms already are: the exposed group's change on deep paraphrases minus the
control group's change on deep paraphrases. There is no substitution, no
assumption behind it, and no gate that can demote it. Sections 4 and 6 of the
Study 5 registration are unchanged in every other respect.

Everything else is held exactly at Study 5's values: the same base model and
revision, the same 100 exposed parents from the same seed, the same untouched
100, the same 1,000-record mixture, the same exposure format ending in the
correct option's text, three epochs, learning rate 2e-5, batch size 2 with
gradient accumulation 8, seed 20260824, Adafactor, sequence budget 256,
full-parameter float32 across both T4s.

## 3. The new items

The 75 new deep paraphrases are written under the six rules now in force,
including rule 6, which Study 5 added after reading the first bank:

> **Rule 6.** An option naming a technical term is reworded into another
> expression of that term, never into its definition, and no reworded option may
> repeat a content word from the stem that the public option did not contain.

They pass the same mechanical verifier as the existing bank and the rule 6
checker. Items whose options cannot be reworded, because they are equations,
bare quantities or proper nouns, are marked exempt on the same basis as
Amendment 1 to Study 4 and are excluded from the deep-paraphrase arm on both
sides. The exempt list is fixed before training and recorded.

The new items are written for control parents. A control parent is never trained
on, so no choice made while drafting its paraphrase can flatter the exposed
group; the drafter cannot know, and does not need to know, which way any
individual item will fall.

## 4. This study is also a replication, and that is registered

The public and fresh arms of Study 6 are a rerun of Study 5 under an identical
configuration. They are therefore a replication, and we fix now what a failure
to replicate means:

- If Study 6's difference in differences on the public form or the fresh forms
  falls outside Study 5's reported 95% interval, the replication is reported as
  failed, in the paper and not only in the log, and every number from both runs
  is presented side by side.
- A failed replication does not invalidate the deep-paraphrase arm of this run,
  which is internally controlled, but it would mean the two runs disagree and we
  would say so rather than choosing between them.

Saturation is expected on the public form, which reached 1.000 in Study 5, so
the public arm is censored from above in both runs and its agreement is weak
evidence either way. The fresh arm at 0.980 is close behind. We note this now so
that a tight agreement between two censored quantities is not later offered as
though it were a strong replication.

## 5. Interpretation, fixed before the data exist

The manipulation check is unchanged: a difference in differences on the public
form below 0.05 means the leak did not take, the study is reported as a failed
manipulation, and nothing about transfer is drawn from it in either direction.

Given a successful manipulation:

- **Deep-paraphrase effect clearly positive**: contamination on ARC reaches
  wording the model never saw, through a rewrite that destroys every memorised
  option string. Section 7.11's transfer finding holds on a second benchmark and
  a second scoring path, and the paper says so.
- **Deep-paraphrase effect indistinguishable from zero**: what transfers on ARC
  is the option string and not the knowledge. Section 7.11 does not generalise
  to this scoring path, the abstract is narrowed to GSM8K, and the released ARC
  bank is reported as blind to a form of contamination that only a deeper
  rewrite exposes.
- **Deep-paraphrase effect clearly positive but much smaller than the fresh-form
  effect**: both of the above in proportion. We report the ratio with its
  interval and describe the arm as partially transferring, without rounding it
  toward either clean story.

The second outcome contradicts a claim the paper currently makes in its
abstract. It is registered as a reportable outcome for exactly that reason.

## 6. Stopping rule, and the fact that this is the third study on ARC

One run, one model, one seed, one exposure format. No dose escalation, no model
substitution, no additional seeds.

**This is the last ARC study, whatever it finds.** Not the last unless it fails,
not the last unless the result is inconvenient: the last. If its manipulation
fails, the paper reports two failed manipulations and one success on ARC and
leaves the deep-transfer question open forever as far as this paper is
concerned. If its deep-paraphrase arm comes back at zero, that is the answer and
the abstract narrows.

We state plainly that this is the third registered study on the same benchmark
and that the argument for each successive one is weaker than the last. The
defence is the same each time and it is checkable: each correction was
identifiable without reference to any outcome. Study 5's was that the leak wrote
a letter while the scorer reads text, provable by reading two scripts. Study 6's
is that a 20-item check cannot resolve a 0.05 tolerance, provable by arithmetic.
Neither needed a result to notice, and both failed studies stay in the paper at
full length. A reader who finds that insufficient should read Sections 7.12 and
7.13 as the record and treat this one as an addendum.

## 7. Non-claims

This estimates nothing about contamination in any released model. It measures
whether a deliberate leak of ARC items, written in the form the scorer reads,
transfers to a rewrite that changes both the stem and the options, on one 1.6B
model under one fine-tuning procedure.

## 8. What could go wrong

The new items are drafted by a language model under written rules, as the
existing bank was, and inherit the same limitation: a mechanical check cannot
detect a shared drafting style, and rule 2 is a semantic condition no script can
enforce. The screening pass and its findings are released with the study.

The deep-paraphrase arm will rest on roughly 90 exposed and 90 control parents
after exemptions, so its interval will be wide, and a small true effect may not
be separable from zero. That is a limit on what the study can conclude, not a
reason to withhold it, and the interval is reported whatever it contains.
