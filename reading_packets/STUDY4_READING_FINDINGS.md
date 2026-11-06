# Deep-paraphrase bank: screening pass

This is a machine screening of all 125 items, not the human reading the
registration asks for. It cannot be that reading: the same model family drafted
these items, so it shares whatever blind spots put a fault in them in the first
place, and an item that reads correctly to the drafter is exactly the item a
drafter-shaped check will pass. Its only purpose is to cut the number of items a
person has to weigh carefully.

Three items need a human decision. One pattern runs through the whole bank and
matters more than any single item.

---

## Items to adjudicate

### 1. arcc_test_0407 — the key and a distractor now overlap

Public options: A observation, B hypothesis, **C conclusion**, **D inference**.
Key is D.

Deep paraphrase: A "something observed", B "a proposed explanation to be
tested", C "a judgement reached at the end", **D "a conclusion drawn from what
was seen"**.

Option D now contains the word "conclusion", which is what option C was. A
reader who takes C at its ordinary meaning and D at its wording can defensibly
choose either. This is the one item in the bank where a distractor has plausibly
become defensible, which is the failure rule 2 exists to prevent.

**Suggested fix:** render D as "a judgement that goes beyond what was directly
seen" and C as "a summary of the completed investigation".

### 2. arcc_test_0699 — the correct option now restates the stem

Stem: "Liquid water turning into water vapour is which process?"
Option C: "turning to vapour". Key is C.

The public option was "evaporation", which required knowing the term. The
paraphrase hands the answer back in the question's own words. The key is still
correct and no distractor became correct, so it passes rule 2 as written, but the
item no longer measures anything and should not sit in a bank used to compare
difficulty.

**Suggested fix:** "the change from liquid to gas at the surface".

### 3. arcc_test_0677 — a distractor may have widened into a second correct answer

Public options: A growth, B dormancy, C hibernation, D metamorphosis. Key is A,
the stage shared by a tree and a frog.

Deep paraphrase: A "getting bigger", **B "a resting period"**, C "sleeping
through winter", D "a change of body form".

"Dormancy" is a botanical term that a reader may not apply to a frog. "A resting
period" plainly does apply to both a tree in winter and a frog in torpor, so B
has arguably become a second correct answer. Judgement call, and it is yours.

**Suggested fix:** narrow B to "a pause in growth through the cold months".

---

## The pattern that matters more

Across the bank, options that named a technical term were frequently replaced by
that term's definition rather than by another way of saying the term. A sample,
all of them key options:

| Item | Public option | Deep paraphrase |
|---|---|---|
| arcc_test_0994 | radiant | energy carried by light |
| arcc_test_1067 | eukaryote | a cell with a true nucleus |
| arcc_test_0901 | parasitism | one organism living at another's expense |
| arcc_test_0683 | kidneys | organs that filter the blood |
| arcc_test_0133 | weight | force of gravity on the body |
| arcc_test_1039 | Van Allen belts | belts of trapped charged particles |
| arcc_test_0224 | sunlight | energy arriving from the Sun |

Each is faithful. Together they change what the items measure, from recalling a
term to recognising a description, and in several cases the description echoes a
word already in the stem: arcc_test_0994 asks about *photosynthetic* algae and
offers "energy carried by light"; arcc_test_1067 mentions *membrane-bound*
structures and offers "a cell with a true nucleus"; arcc_test_0683 asks what
removes waste *from the blood* and offers "organs that filter the blood".

This is not a rule 2 violation. No key moved and no distractor became correct.
It is a measurement problem, and it has one consequence that outlives Study 4.

**A deep paraphrase was supposed to do one thing: remove the memorised option
string. These do two things: they remove the string and they change the
cognitive demand.** Any comparison between the released fresh forms and the deep
paraphrases therefore confounds the two, and a smaller effect on the deep
paraphrases cannot be attributed to the missing string alone.

For the difference in differences this mostly cancels, because a difficulty shift
that is the same before and after fine-tuning subtracts out, and the measured
baselines say the rewrite made items harder rather than easier overall: on the
exposed parents the clean model scored 0.460 on the public forms and 0.387 on the
deep paraphrases. It does not cancel for any comparison of levels, and it does not
cancel for the interpretation the deep paraphrase was built to support.

**Consequence for any future study on this bank:** the drafting rules need a
sixth clause, and the affected items need rewriting under it before, not after,
anything is trained.

> **Rule 6.** An option naming a technical term is reworded into another
> expression of that term, never into its definition, and no reworded option may
> repeat a content word that appears in the stem.

## Consistency note, no action needed

Amendment 1 exempts items whose options are proper nouns, on the ground that a
proper noun cannot be reworded without naming a different thing. arcc_test_1039
reworded "Van Allen belts" and stayed in the G arm. That is defensible, because
it was rewritten into a description rather than renamed, but it is the same move
the amendment declined to make for Pluto and Saturn. Recording it so the
exemption list reads as a judgement rather than a rule that was applied unevenly.

---

# Second screening pass: the 75 control-parent items added for Study 6

Run 2026-08-27, after Study 8, covering the 75 deep-paraphrase items written for
Study 6's control parents. Those had passed the mechanical verifier and the rule
6 checker but had never been screened for meaning. This closes that gap for the
bank as a whole: all 200 items have now had a machine screening.

It remains a machine screening. The same model family drafted these items, so it
shares whatever blind spot put a fault in them, and a human reading has still not
happened. Nothing below should be read as one.

## Result

Of the 75, twelve are exempt because their options cannot be reworded, leaving 63
screened against their public originals for rule 2: does the rewording make a
distractor correct, or the key wrong?

**No rule 2 violation was found in any of the 63.** In every item the keyed option
still names the same thing it named before, and no distractor was widened into a
second defensible answer.

## Four things worth recording anyway

**arcc_test_0115 changed a distractor's truth value.** The public option C reads
"The atom increases in atomic mass"; the rewrite reads "The atom's mass number
rises". An atom that gains an electron does gain a little mass, so the public
option is arguably slightly true, while mass number counts protons and neutrons
and does not change at all. The rewrite is therefore more clearly false than the
original. That makes the item cleaner rather than broken, and the key is
untouched, but it is a change in content and not only in wording.

Three ambiguities are inherited from the public originals and were preserved
rather than introduced. In **arcc_test_0222** the key is "folded rock" while a
distractor is "plate tectonics", and the Alps, Appalachians and Himalayas are
formed by plate tectonics; the same tension is in the ARC original. In
**arcc_test_0319** the key is sand while a distractor is water, and water has the
higher heat capacity. In **arcc_test_0445** the key is squirrels burying acorns
while a distractor is returning nutrients to the soil, which is arguably what
burying acorns does. A paraphrase cannot repair a question that was already
ambiguous, and rewriting these to remove the ambiguity would have made the deep
paraphrase easier than the form it is compared against.

## The three items flagged in the first 125

The bank was not edited. Studies 6 and 8 had already run on it, and removing items
after seeing results is the move that makes a bank untrustworthy; the same choice
was made for the 21 near-copy GSM8K forms in Section 7.7.

What was done instead is to measure what the three are worth.
paper10_flagged_item_sensitivity.py drops all three from the deep-paraphrase arm
and recomputes the estimate on all four training seeds. The effect moves by
between +0.0033 and +0.0051, in the direction of a slightly larger effect, and
stays positive on every seed. The flagged items are not carrying the result, and
a reader who disagrees with any judgement about them can see that it does not
change the conclusion.
