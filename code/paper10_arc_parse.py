"""Prompt and answer-letter parser for the output-only ARC arm (real-audit Amendment 2).

Kept free of torch and transformers so that the rule can be tested on synthetic strings.
The rule is fixed in REAL_AUDIT_AMENDMENT2.md before any model is queried on it.
"""

from __future__ import annotations

import re

ARC_INSTRUCTION = (
    "Answer the following multiple-choice science question. "
    "Reply with the letter of the correct option (A, B, C or D) only.\n\n"
)


def arc_user_message(row: dict) -> str:
    return (
        ARC_INSTRUCTION
        + f"Question: {row['prompt']}\n"
        + f"A. {row['optA']}\nB. {row['optB']}\nC. {row['optC']}\nD. {row['optD']}\n\n"
        + "Answer:"
    )


# Rule 1: the reply starts with a letter A to D that is a token of its own (a letter followed by
# end of text, a newline or one of . ) : ,). "A cell is" does not match. Rule 2: the last
# "answer is X". Otherwise the reply is invalid and counts as incorrect.
_START = re.compile(r"^[\s\*\(\[\"']*([ABCD])\s*(?:[\.\)\]:,\*]|$|\n)")
_ANSWER_IS = re.compile(r"answer is\s*[:\*\(\[]*\s*([ABCD])(?![A-Za-z])", re.IGNORECASE)


def parse_letter(continuation: str) -> str | None:
    text = continuation.strip()
    match = _START.match(text)
    if match:
        return match.group(1)
    found = _ANSWER_IS.findall(text)
    # the letter must be written in capitals; the case-insensitive flag is for the words "answer is"
    found = [f for f in found if f in "ABCD"]
    if found:
        return found[-1]
    return None
