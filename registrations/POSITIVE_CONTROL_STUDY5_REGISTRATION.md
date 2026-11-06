# CleanScore Positive Control, Study 5: does contamination transfer when the leak and the scorer speak the same language?

DRAFT REGISTRATION. Nothing has been trained and no item has been scored against
any model for this study. When it is locked, the date is recorded here and the
file does not change again except by a dated amendment.

## 1. What this is, and what it is not

Study 4 asked whether the transfer finding of Section 7.11 survives a
log-probability scoring path. It did not answer, because it failed its own
manipulation check: leaking an item lowered accuracy on that item by 22 points
against the control group, well below the registered floor of +0.05.

The cause is not in dispute and does not depend on any result. The exposure
record ended with the line `Answer: A.`, a letter. The ARC scorer never shows
the model an option list: it appends `Answer:` to the stem and ranks each
option's text by how likely that text is as the continuation. The training
taught the model to emit a letter and the instrument asked it for a sentence.
Both facts are readable in the two scripts without running anything.

**Study 4 is not retracted, amended, or replaced.** It is reported in full as a
failed manipulation, with its own figure and table, and this study does not
change a word of it. What follows is a separate study with its own registration,
run once, on the question Study 4 was unable to reach.

We state the obvious objection ourselves. Study 4's stopping rule says "no
further studies on ARC whatever the outcome", and this is a further study on
ARC. That rule exists to stop an experiment being repeated until it produces a
convenient answer, and we accept that a reader cannot verify our motives. What a
reader can verify is that the fault was in the instrument rather than in the
result, that it is provable from the code alone, that the failed study stays in
the paper at full length, and that the interpretation below is fixed before any
number exists. If that is not enough for a given reader, the honest position is
that Study 4 stands and this study is an addendum they may discount entirely.

## 2. The single change

The exposure record becomes:

```
Question: <public stem>
Answer: <text of the correct option>
```

No option list, and no letter. This is the form a leaked question-and-answer
pair takes when it is scraped rather than dumped, and it is the form the scorer
can register.

Everything else is held at Study 4's values: the same base model and revision,
the same 100 exposed parents from the same seed, the same 100 untouched control
parents, the same 1,000-record mixture with the same 900 background items, three
epochs, learning rate 2e-5, batch size 2 with gradient accumulation 8, seed
20260824, Adafactor, sequence budget 256, full-parameter float32 across both
T4s. One difference between two studies, so that the comparison between them is
itself informative.

### What this buys and what it costs

It buys a manipulation that the instrument can see. It costs the strength of the
manipulation check as evidence: the leak now mirrors the evaluation prompt
almost exactly, so a large effect on the public form is close to guaranteed by
construction and confirms only that fine-tuning works. **The manipulation check
is therefore a precondition here, not a finding.** Everything this study can
contribute lives in the other two arms, and we say so now so that a large number
on the public form is not later presented as though it were a result.

## 3. The bank was corrected first, and why that is not outcome-driven

Reading the deep-paraphrase items surfaced a fault that no mechanical check
covered. Options naming a technical term had often been rewritten into that
term's definition, and the definition sometimes repeated a word from the stem:
"radiant" became "energy carried by light" beside a stem about photosynthesis,
"eukaryote" became "a cell with a true nucleus" beside a stem about
membrane-bound structures. Three items had a worse problem, one of them a key
and a distractor that had drifted into overlapping.

A deep paraphrase exists to remove the memorised option string and change
nothing else. These changed the cognitive demand as well, so any gap between the
released fresh forms and the deep paraphrases would have confounded the two.

A sixth drafting rule is therefore added and the bank repaired under it:

> **Rule 6.** An option naming a technical term is reworded into another
> expression of that term, never into its definition, and no reworded option may
> repeat a content word from the stem that the public option did not contain.

Thirteen items were repaired. `paper10_check_rule6.py` enforces the second half
mechanically and, run against the uncorrected bank, independently flags seven of
the items the reading had already identified. The Study 4 bank is kept intact as
`arc_deep_paraphrase_pre_rule6.csv`, because Study 4's reported numbers belong to
the bank Study 4 actually ran on and must not move.

This repair was triggered by reading the items, which is a judgement about how a
question is built and requires no model and no result. It was applied before
anything was trained. The reading that the Study 4 registration made a
precondition, and which Study 4 ran without, is a precondition here too, and this
time the finding it produced is on the record before the run rather than after.

## 4. Exposed model, exposure, and analysis

Base: **StableLM-2-1.6B-Chat**, the revision used in Studies 3 and 4.

The 100 exposed parents are the same 100, drawn with `default_rng(20260824)` and
already written to
`data/positive_control_arc_exposure_seed20260824.csv`. They are not redrawn.

Neither the released fresh forms nor the deep paraphrases enter training, and the
script asserts that no held-out stem or option text appears anywhere in the
mixture before it starts.

Analysis is Study 4's, unchanged: difference in differences against the untouched
100 parents, bootstrap over parents at 20,000 draws, for each of

- **P**, the public wording, which is what was trained on,
- **F**, the two released fresh forms, stem rewritten and options verbatim,
- **G**, the deep paraphrase, stem and options both rewritten, on the 93 exposed
  parents that Amendment 1 left in the G arm.

G has no control counterpart, so it uses the control group's F change as its
counterfactual, and that substitution is checked on the 20 control parents that
carry a G form. If their F and G changes differ by more than 0.05 the assumption
is reported as failed and the G arm is reported descriptively only.

## 5. Interpretation, fixed before the data exist

- **DiD on P below 0.05**: the manipulation failed again, on a leak written to
  match the scorer. The study is reported as a failed manipulation and
  contributes nothing about transfer. No third attempt, on any format.
- **F and G both clearly positive**: contamination transfers on a
  log-probability scoring path, and survives a rewrite of the options that
  destroys every memorised string. This confirms Section 7.11 on a second
  benchmark and a second scoring path, and the abstract's generalisation stands.
- **F clearly positive, G near zero**: what transfers on ARC is the option
  string, not the knowledge. This does **not** confirm Section 7.11. It says the
  released ARC bank, whose fresh forms hold the options fixed, reports as
  transfer something a deeper rewrite shows to be memorisation, and the paper
  will say so.
- **F and G both near zero with P clearly positive**: contamination on ARC does
  not transfer at all. The GSM8K finding does not generalise across scoring
  paths and the abstract is narrowed to GSM8K.

The third and fourth outcomes weaken claims the paper currently makes. They are
registered as reportable outcomes for that reason.

## 6. Stopping rule

One run, one model, one seed, one exposure format. No dose escalation, no model
substitution, no additional seeds, and no third study on ARC under any
formatting, whatever this one finds. A repeat is permitted only for an
infrastructure failure, at the identical configuration, and is logged as one.

If this study also fails its manipulation check, the paper reports two failed
positive controls on ARC and leaves the cross-scoring-path question open. That is
a worse outcome for the paper than never having tried, and we are fixing it as
the reportable outcome now rather than deciding later.

## 7. Non-claims

This estimates nothing about contamination in any released model. It measures
whether a deliberate leak of ARC items, written in a form the scorer can
register, transfers to rewrites of those items at two rewrite depths, on one
1.6B model under one fine-tuning procedure.

## 8. Cost and what could go wrong

One Kaggle GPU session: clean audit, fine-tune, exposed audit, all three form
types in one session on one set of weights.

StableLM's ARC accuracy is near the four-option guessing floor, so if fine-tuning
degrades it toward 0.25 the difference in differences will be dominated by that
degradation; the control-parent change is reported beside every estimate so this
stays visible. The G arm rests on 93 parents and the assumption check on 20, so
its interval will be wide. Neither is a reason not to run it, and neither should
be discovered afterwards.
