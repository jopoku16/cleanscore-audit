# Real-audit Amendment 2

Declared 2026-11-06, before any model was queried on either arm below. It amends nothing in
REAL_AUDIT_REGISTRATION.md. It adds two robustness arms, reported beside the registered primary and never instead of it.
(Amendment 1, the 768-token rerun of the two Qwen models, is unchanged.)

## Why

A referee-style review of the manuscript raised two points about the registered audit. (1) The registered 320-token
budget truncated 25.3% (OLMo-2-7B), 14.5% (SmolLM2-1.7B) and 11.3% (Phi-3-mini) of GSM8K audit forms, and those three
models were not rerun; a post hoc check (results/truncation_check) found nearly equal truncation on public and fresh
forms but worst-case bounds too wide to settle the question. (2) The ARC arm is scored from option log probabilities, so
it needs more than generated text from the model under audit.

## Arm A: GSM8K at an adequate budget

Models: allenai/OLMo-2-1124-7B-Instruct, HuggingFaceTB/SmolLM2-1.7B-Instruct, microsoft/Phi-3-mini-4k-instruct, at the
pinned revisions of the registration. Items: the registered GSM8K audit forms (600) and control forms (180), unchanged.
Settings: the registered chat template, instruction and greedy decoding; max_new_tokens = 768; the Amendment 1 parser
(last "answer is" number, then last \boxed{} number, then last number); generation batch 4 (small models) and 2 (OLMo).
Code: the registered runner's `run_gsm8k`, imported unchanged.

## Arm B: ARC by generation (output-only)

Models: all five registered models. Items: the registered ARC audit forms (600) and control forms (120), unchanged.
Prompt (the chat template's single user turn, then the generation prompt):

    Answer the following multiple-choice science question. Reply with the letter of the correct option (A, B, C or D) only.

    Question: <stem>
    A. <option A>
    B. <option B>
    C. <option C>
    D. <option D>

    Answer:

Greedy decoding, max_new_tokens = 32. Parser (code/paper10_arc_parse.py, tested on synthetic strings only, 22 cases in
code/test_paper10_arc_parse.py): the reply is read as letter X if, after optional spaces, asterisks, brackets or quotes,
it starts with a capital letter A to D that is followed by end of text, a newline or one of `. ) ] : , *`; otherwise as the
letter in the last "answer is X" with X a capital A to D; otherwise the reply is invalid and counts as incorrect. Option
order, option text and answer keys are as in the registered banks. The prompt and the parser were fixed without
querying any model on any audit or control item.

## Analysis and reporting (fixed now)

- Same analysis code as the registered audit (code/paper10_analyze_real_audit.py): the audit estimate, the registered
  primary and guardrail rule, the Proposition 3 sensitivity interval at the registered radii, and the registered claim
  rule. Nothing about the interval, the radius or the claim rule changes.
- Arm A is analysed with the five models' GSM8K files at 768 tokens (the Amendment 1 files for the two Qwen models, the new
  files for the other three). Arm B is analysed with the five models' generated ARC files.
- A model's Arm A result is called adequate if truncation on its audit forms is at most 1%. Otherwise the actual rate is
  reported and the result is called partial.
- A model's Arm B result is called interpretable if at most 10% of its audit-form replies are invalid. Otherwise it is
  reported as not interpretable for that model. There is no re-prompting after outputs are seen. If a run fails for a technical
  reason (for example out of memory), it is rerun with a smaller batch and nothing else changed.
- If an Amendment 2 estimate meets the registered claim rule where the registered primary did not, that is reported as a
  result of this amendment, the registered primary stays the primary, and the abstract and conclusions are revised to say so.
- The registered ARC log-probability arm stays in the paper as the primary ARC result.
