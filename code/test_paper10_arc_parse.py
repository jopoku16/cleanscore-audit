"""Synthetic tests of the Amendment 2 ARC letter parser. No model output and no audit item is used."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paper10_arc_parse import arc_user_message, parse_letter

CASES = [
    ("B", "B"), (" B", "B"), ("B.", "B"), ("B. buildings will be made safer", "B"), ("(C)", "C"),
    ("**D**", "D"), ("A) the first", "A"), ("B\nBecause the", "B"), ("C: weather", "C"),
    ("The answer is C.", "C"), ("Reasoning first. The answer is D", "D"), ("the Answer is: B", "B"),
    ("answer is A, then answer is B", "B"),
    ("A cell is the basic unit", None), ("A group of engineers", None), ("Because it is B", None),
    ("", None), ("   ", None), ("E", None), ("The answer is e", None), ("ABC", None), ("answer is Apples", None),
]

bad = [(text, want, parse_letter(text)) for text, want in CASES if parse_letter(text) != want]
assert not bad, bad

row = {"prompt": "Which is warm?", "optA": "ice", "optB": "snow", "optC": "fire", "optD": "frost"}
msg = arc_user_message(row)
assert msg.startswith("Answer the following multiple-choice science question.")
assert "Question: Which is warm?\nA. ice\nB. snow\nC. fire\nD. frost\n\nAnswer:" in msg
print(f"{len(CASES)} parser cases passed")
