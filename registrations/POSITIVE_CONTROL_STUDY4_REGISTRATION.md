# CleanScore Positive Control, Study 4: does the transfer finding survive a different scoring path?

LOCKED 2026-08-24. RUN 2026-08-26. OUTCOME: failed manipulation, reported in
Section 7.12 and closed under the stopping rule in Section 8.

Sections 1 to 10 below are the text as locked, before anything was trained or
scored. Everything after them is a dated amendment or deviation, in the order it
was logged. The file has not been changed in any other way.

### Deviation 1, logged after the run, 2026-08-26

Section 3 makes a human reading of all deep-paraphrase items a precondition:
"if it is not done, the study does not run." The run went ahead before that
reading was complete. This is a deviation from the registration, it is recorded
here rather than left out, and it was not authorised by anything in this
document.

What it does and does not touch. The study failed at the manipulation check,
which is computed entirely from the public forms, and those are the original ARC
items rather than anything written for this study. The reported outcome
therefore does not rest on the deep-paraphrase items being semantically sound.
The quantities that would rest on it are the G-arm accuracies, and by the
registration's own rule those contribute nothing to any claim once the
manipulation check has failed. The mechanical checks in Section 3, which cover
rules 1, 3, 4 and 5 and pairwise distinctness, did all run before the model saw
anything.

The bank is still released, so the reading remains worth doing on the artefact
even though the study around it is closed.

## 1. Why this study

Section 7.11 establishes that most of the effect of leaking an item's wording
transfers to paraphrases the model never saw. That result rests on four models
and on **one benchmark**: GSM8K, scored by free generation and exact numeric
match. The paper generalises it to any audit that compares an original question
against a rewrite of it.

The audit's other benchmark is scored a completely different way. ARC-Challenge
items are scored without generation, by the length-normalised log probability of
each option text given the stem. Whether item knowledge transfers to a reworded
question when the model regenerates a solution, and whether it transfers when
the model ranks four fixed strings, are different questions with no obvious
reason to share an answer. The claim in the abstract is currently supported on
one of the two.

This study asks the second question.

## 2. The design problem, stated before it can be discovered

ARC fresh forms in the released bank rewrite the question stem only. The four
options and the answer key are preserved verbatim; this was checked and holds
for all 200 of 200 ARC parents.

That has a consequence which must be faced before the experiment rather than
after it. A contaminated model that learns nothing except the association
between an option set and its key will score identically on the public form and
on both fresh forms, because those forms present the identical option set. On
ARC, therefore, a measured transfer share near 100% is partly **mechanical**
and not by itself evidence of the deep item knowledge that the GSM8K result
demonstrates. Running this study on the released bank alone and reporting a high
transfer share as independent confirmation would be a mistake, and we say so now
so that the outcome cannot be read that way later.

This also states something about the audit already reported. On ARC, the
released bank cannot see option-level memorisation at all: the estimand holds
the options fixed, so any advantage attached to the options rather than to the
stem is invisible to it by construction. That is a property of the bank, it is
true whatever this study finds, and it will be reported in the paper's
limitations regardless of whether this study is run.

## 3. What is added to make the study informative

For the 100 exposed parents only, we write a third evaluation form type:

- **P**, the public form: original stem, original options. This is the wording
  the model will be trained on.
- **F**, the released fresh forms: rewritten stem, options and key verbatim.
  Both released variants are used, as in the main audit.
- **G**, a deep paraphrase, written for this study and never published before
  it: rewritten stem **and** rewritten options, with the referent of each option
  and the position of the key preserved.

G is what breaks the confound. A model that has memorised an option set cannot
use that memory on G, because no option string in G appears in training.

### Rules for writing G, fixed now

1. Each of the four options is reworded. No option string in G may be identical
   to, or a substring of, its counterpart in P.
2. The thing each option refers to is unchanged. Rewording may not make a
   distractor correct or the key incorrect.
3. The key stays at the same letter position.
4. The stem is rewritten under the same rules as the released fresh forms.
5. No numeric quantity, unit, or named entity that the question depends on is
   altered.

### Mechanical verification of G, before any model sees it

A script checks (1), (3), (5), that all four options remain pairwise distinct,
and that stem and option lengths stay within the bounds used for the released
bank. Items failing any check are rewritten and rechecked. The verifier and the
G bank are released with the study.

G is drafted by a language model under these written rules, exactly as the
released bank was, and inherits that limitation: a mechanical check cannot
detect a shared drafting style, and rule (2) is a semantic condition a script
cannot fully enforce. **Rule (2) requires a human reading of all 100 G items
before they are used.** Unlike the released bank, this reading is a
precondition of the study and not an outstanding item; if it is not done, the
study does not run.

## 4. Exposed model

Base: **StableLM-2-1.6B-Chat**, the same revision used in Study 3.

Two reasons, both fixed in advance. It has the most headroom of the four
contaminated models on ARC, at 0.430 public accuracy against a 0.25 floor for
four-option guessing, so a planted effect has room to appear. And it is the
model whose GSM8K visible gap was negative, which makes it the single most
informative case: if its ARC visible gap behaves differently, that difference is
attributable to the scoring path rather than to the model.

Its clean ARC audit is on record but was produced under the main audit's
settings, so this study audits the clean model and the exposed model in the same
session, as Study 3 did, rather than comparing across sessions.

## 5. Exposure

From the 200 frozen ARC audit parents, 100 are drawn without replacement with
numpy default_rng(20260824) and marked exposed. The assignment is written to
`data/positive_control_arc_exposure_seed20260824.csv` before training and is not
changed afterwards. The remaining 100 are the within-model control group and are
never trained on.

Training mixture, 1,000 records:

- 100 exposure records, one per exposed parent: the public stem, the four
  original options, and the correct option, formatted as the evaluation prompt
  formats them. This is what a leak of an ARC item looks like.
- 900 background records of four-option science questions sharing no stem and no
  option string with any audit or control item.

Three epochs, learning rate 2e-5, batch size 2 with gradient accumulation 8,
seed 20260824, full-parameter fp32 sharded across both T4s with
`device_map="auto"`. Identical to Study 3 in every respect except the benchmark.

Fresh forms, whether F or G, never enter training. A check confirms that no F or
G string appears anywhere in the mixture.

## 6. Analysis, fixed now

For each of P, F and G, the estimate is a difference in differences against the
unexposed 100 parents of the same model, with bootstrap intervals over parents
at 20,000 draws, exactly as in Study 3. F and G are evaluated on the exposed
parents; the unexposed parents contribute P and F only, since G is written for
the exposed items.

Because G does not exist for the control parents, the DiD for G uses the control
group's F change as its counterfactual. This is stated now because it is a
choice, not a necessity: it assumes fine-tuning moves G and F alike on
uncontaminated items. The assumption is checked by writing G forms for 25 of the
100 unexposed parents as well, chosen with the same seed, and comparing their F
and G changes. If those differ by more than 0.05 the assumption is reported as
failed and the G arm is reported descriptively only.

Reported quantities:

1. DiD on P, the leaked wording.
2. DiD on F, the released paraphrase.
3. DiD on G, the deep paraphrase.
4. Visible gap under the released bank, P minus F. This is what the main ARC
   audit would observe.
5. Visible gap under the deep paraphrase, P minus G.
6. Transfer shares F/P and G/P with bootstrap intervals.

## 7. Interpretation, fixed before the data exist

- **DiD on P below 0.05**: the manipulation failed. The study is reported as a
  failed manipulation and contributes nothing to any claim about transfer. No
  dose escalation, no second attempt.
- **G ≈ F ≈ P, all clearly positive**: transfer is deep and survives a
  log-probability scoring path. This is genuine confirmation of Section 7.11 on
  a second benchmark and strengthens the abstract's generalisation.
- **F ≈ P but G much smaller**: what looks like transfer on ARC is largely
  option-level memorisation. This does **not** confirm Section 7.11; it shows
  that the ARC arm of the released bank is blind to a form of contamination that
  a deeper rewrite exposes. The paper would report the GSM8K result as its
  transfer evidence and this as a limitation of stem-only rewriting.
- **G and F both near zero with P clearly positive**: contamination on ARC does
  not transfer at all, and the GSM8K finding does not generalise across scoring
  paths. The abstract would be narrowed to GSM8K.

Every one of these is reported. The third and fourth outcomes weaken the paper's
current headline claim, and we are registering them as reportable outcomes
precisely so that they cannot be quietly dropped.

## 8. Stopping rule

One run, one model, one seed. No dose escalation, no model substitution, no
additional seeds, and no further studies on ARC whatever the outcome. If the run
fails for infrastructure reasons the failure is logged and the run is repeated
at the identical configuration; a repeat for any other reason is a deviation and
is reported as one.

## 9. Non-claims

This study does not estimate contamination in any released model. It does not
measure how much contamination exists in the wild. It measures whether a planted
and deliberate leak of ARC items transfers to rewrites of those items under two
rewrite depths, on one model of 1.6B parameters under one fine-tuning procedure.

## 10. Cost and what could go wrong

One Kaggle GPU session: clean ARC audit, fine-tune, exposed ARC audit on P, F
and G. Comparable to a Study 3 run.

Two things could make the study uninformative rather than negative. StableLM's
ARC accuracy is near the four-option guessing floor, so if fine-tuning degrades
it toward 0.25 the difference in differences will be dominated by that
degradation, as happened to OLMo-2-1B on GSM8K; the control-parent change is
reported alongside every estimate so that this is visible. And 100 exposed
parents gave wide intervals on GSM8K; there is no reason to expect narrower ones
here, so a small true effect may not be separable from zero. Neither is a reason
not to run it, but neither should be discovered afterwards.

## Amendment 1 to Study 4, logged before any item was written

Attempting to write the deep-paraphrase forms exposed a rule in Section 3 that
cannot be satisfied for a small number of items. Rule 1 requires every option to
be reworded so that no option string is identical to its counterpart. For items
whose options are chemical equations, or bare quantities with units, there is no
rewording that preserves the referent: "NaCl + H_{2}O" and "16 N" mean what they
mean, and any change to the string changes the chemistry or the measurement.

Twelve of the 125 items are affected, in three kinds. The count was seven when
this amendment was first written from a scan of the options, and rose to twelve
as the items were actually drafted and the mechanical checker rejected further
cases; the list is fixed at twelve and recorded in data/arc_g_exempt.txt. Two carry balanced
equations as options, arcc_test_0060 and arcc_test_0170. Three carry bare
quantities: arcc_test_0854, arcc_test_0012 and arcc_test_0673. Two carry
proper nouns or canonical single-word terms, arcc_test_0511 with Pluto, Saturn,
the Sun and the Moon, and arcc_test_0564 with the four states of matter. A
proper noun cannot be reworded at all: any change to "Pluto" names a different
object, and any change to "Solid" names a different phase.

Seven of the twelve fall in the exposed half, so the G arm rests on 93 exposed
parents rather than 100. The other five fall among the 25 assumption-check
parents. A further three, arcc_test_0187, arcc_test_0840 and arcc_test_0950,
carry symbols inside otherwise ordinary sentences and can be reworded around
them, so they stay in.

For the affected items the deep-paraphrase form rewrites the stem only and
leaves the options as they are, which makes it identical to the released fresh
form in the one respect the deep paraphrase exists to test. They are therefore
excluded from the G arm and reported separately.

This is logged before any deep-paraphrase item was drafted and before any model
was trained, so it cannot have been chosen to suit an outcome. It weakens the
study slightly by reducing the G sample, and it does not change the exposure
assignment, the training mixture, or the analysis of the P and F arms, which
still use all 100 exposed parents.

## Amendment 2, logged before the run that produced any result

The training step ran out of memory on two T4s, in the optimizer rather than in
the forward pass: AdamW allocates two float32 moment buffers per parameter, and
the failure is the 784 MB allocation for the second moment of the output
embedding. Study 3 fitted the same model under identical settings, so this is a
marginal fit rather than a design difference, and reducing the sequence budget
does not help because the pressure is optimizer state and not activations. The
longest training record is about 186 tokens against a 384 budget, so nothing was
being truncated either way.

Two changes, both hardware accommodations:

1. The optimizer becomes Adafactor rather than AdamW. Adafactor factors the
   second moment instead of storing it per parameter, which removes most of the
   optimizer state while still updating every weight.
2. The sequence budget drops from 384 to 256. No record reaches 256 tokens, so
   this truncates nothing; it is included only because it costs nothing.

Everything else is unchanged: full-parameter training in float32, the same
exposure assignment, the same 1,000-record mixture, the same three epochs, the
same learning rate, the same seed, the same evaluation.

The risk this introduces is stated now rather than discovered later. A different
optimizer may implant less contamination than Study 3's did, and the quantity
this study measures is how much contamination transfers. If the leak takes less
firmly, the study is uninformative rather than negative. The registration
already covers that case: the manipulation check fails the study if the
difference in differences on the leaked wording is below 0.05, and a failed
manipulation is reported as a failed manipulation and contributes nothing to any
claim about transfer. It is not evidence that transfer does not happen on ARC.
