"""Run the registered CleanScore real-benchmark audit for one or more models.

Implements REAL_AUDIT_REGISTRATION.md section 6 exactly:
- GSM8K-style items: chat template, greedy decoding, max_new_tokens=320,
  answer parsed from the last "answer is" (fallback: last number), numeric
  normalization, one evaluation per form.
- ARC-style items: no generation; per-option sum of token log probabilities of
  " <option text>" conditioned on the chat-templated stem plus "Answer:",
  character-normalized as primary scoring, raw sum recorded as secondary.
- Per-token mean log probability of the greedy continuation (GSM8K) and of
  each option (ARC) recorded for the PaCoST-style confidence baseline.

The run is resumable at the model level: a model whose four output files all
exist is skipped.
"""

from __future__ import annotations

import argparse
import csv
import json
import platform
import re
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

REQUIRED = ("gsm8k_results.csv", "gsm8k_control_results.csv", "arc_results.csv", "arc_control_results.csv")

GSM8K_INSTRUCTION = (
    'Solve the following math problem. Show your reasoning, then give the '
    'final answer on the last line in the form "The answer is <number>."\n\n'
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+", required=True, help="Entries of the form name@revision")
    parser.add_argument("--items-dir", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--max-new-tokens", type=int, default=320)
    parser.add_argument("--gen-batch-small", type=int, default=8)
    parser.add_argument("--gen-batch-large", type=int, default=4)
    parser.add_argument("--score-batch", type=int, default=16)
    parser.add_argument("--amended-parser", action="store_true", help="Amendment 1: accept boxed{} answers")
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def normalize_number(text: str) -> str | None:
    text = text.replace(",", "").replace("$", "").replace("%", "").strip().rstrip(".")
    match = re.fullmatch(r"-?\d+(?:\.\d+)?", text)
    if not match:
        return None
    value = float(text)
    if value == int(value):
        return str(int(value))
    return str(value)


def extract_prediction(continuation: str, amended: bool = False) -> str | None:
    """Registered parser; Amendment 1 adds a LaTeX boxed{} path between the two registered steps."""
    matches = re.findall(r"answer is\s*\$?(-?[\d,]+(?:\.\d+)?)", continuation, flags=re.IGNORECASE)
    if matches:
        return normalize_number(matches[-1])
    if amended:
        boxed = re.findall(r"\\boxed\{([^{}]*)\}", continuation)
        if boxed:
            inner = re.findall(r"-?[\d,]+(?:\.\d+)?", boxed[-1])
            if inner:
                return normalize_number(inner[-1])
    numbers = re.findall(r"-?[\d,]+(?:\.\d+)?", continuation)
    if numbers:
        return normalize_number(numbers[-1])
    return None


def chat_prompt(tokenizer, user_message: str) -> str:
    return tokenizer.apply_chat_template(
        [{"role": "user", "content": user_message}],
        tokenize=False,
        add_generation_prompt=True,
    )


def run_gsm8k(model, tokenizer, rows, batch_size: int, max_new_tokens: int, label: str, amended: bool = False):
    device = next(model.parameters()).device
    tokenizer.padding_side = "left"
    results = []
    for start in range(0, len(rows), batch_size):
        batch = rows[start : start + batch_size]
        prompts = [chat_prompt(tokenizer, GSM8K_INSTRUCTION + row["prompt"]) for row in batch]
        inputs = tokenizer(prompts, return_tensors="pt", padding=True, add_special_tokens=False).to(device)
        with torch.no_grad():
            generated = model.generate(
                **inputs,
                do_sample=False,
                max_new_tokens=max_new_tokens,
                pad_token_id=tokenizer.pad_token_id,
                return_dict_in_generate=True,
                output_scores=True,
            )
        transition = model.compute_transition_scores(generated.sequences, generated.scores, normalize_logits=True)
        width = inputs["input_ids"].shape[1]
        for row, sequence, scores in zip(batch, generated.sequences, transition):
            new_tokens = sequence[width:]
            keep = new_tokens != tokenizer.pad_token_id
            n_tokens = int(keep.sum())
            logprob_sum = float(scores[: len(new_tokens)][keep].sum()) if n_tokens else 0.0
            continuation = tokenizer.decode(new_tokens, skip_special_tokens=True)
            pred_reg = extract_prediction(continuation, amended=False)
            pred_amd = extract_prediction(continuation, amended=True)
            prediction = pred_amd if amended else pred_reg
            gold = normalize_number(str(row["answer"]))
            results.append(
                {
                    "parent_id": row["parent_id"],
                    "form_id": row["form_id"],
                    "form_type": row["form_type"],
                    "answer": row["answer"],
                    "prediction": prediction or "",
                    "correct": int(prediction is not None and prediction == gold),
                    "prediction_registered": pred_reg or "",
                    "correct_registered": int(pred_reg is not None and pred_reg == gold),
                    "prediction_amended": pred_amd or "",
                    "correct_amended": int(pred_amd is not None and pred_amd == gold),
                    "n_generated_tokens": n_tokens,
                    "sum_logprob": round(logprob_sum, 4),
                    "mean_logprob": round(logprob_sum / n_tokens, 6) if n_tokens else 0.0,
                    "continuation": continuation.replace("\n", " ").strip(),
                }
            )
        print(f"[{label}] generated {min(start + batch_size, len(rows))}/{len(rows)}", flush=True)
    return results


def score_options(model, tokenizer, context: str, options: list[str], batch_size: int):
    device = next(model.parameters()).device
    tokenizer.padding_side = "right"
    context_ids = tokenizer(context, add_special_tokens=False)["input_ids"]
    sequences = [context_ids + tokenizer(" " + option, add_special_tokens=False)["input_ids"] for option in options]
    scores = []
    for start in range(0, len(sequences), batch_size):
        chunk = sequences[start : start + batch_size]
        longest = max(len(seq) for seq in chunk)
        input_ids = torch.full((len(chunk), longest), tokenizer.pad_token_id, dtype=torch.long)
        attention = torch.zeros((len(chunk), longest), dtype=torch.long)
        for i, seq in enumerate(chunk):
            input_ids[i, : len(seq)] = torch.tensor(seq)
            attention[i, : len(seq)] = 1
        input_ids = input_ids.to(device)
        attention = attention.to(device)
        with torch.no_grad():
            logits = model(input_ids=input_ids, attention_mask=attention).logits.float()
        logprobs = torch.log_softmax(logits, dim=-1)
        for i, seq in enumerate(chunk):
            option_len = len(seq) - len(context_ids)
            total = 0.0
            for pos in range(len(context_ids), len(seq)):
                token = seq[pos]
                total += float(logprobs[i, pos - 1, token])
            scores.append((total, option_len))
    return scores


def run_arc(model, tokenizer, rows, batch_size: int, label: str):
    results = []
    for index, row in enumerate(rows):
        stem_prompt = chat_prompt(tokenizer, row["prompt"]) + "Answer:"
        options = [row["optA"], row["optB"], row["optC"], row["optD"]]
        scored = score_options(model, tokenizer, stem_prompt, options, batch_size)
        norm = [total / max(1, len(option)) for (total, _), option in zip(scored, options)]
        raw = [total for total, _ in scored]
        letters = ["A", "B", "C", "D"]
        pred_norm = letters[max(range(4), key=lambda i: norm[i])]
        pred_raw = letters[max(range(4), key=lambda i: raw[i])]
        mean_lp = [total / max(1, n_tok) for total, n_tok in scored]
        results.append(
            {
                "parent_id": row["parent_id"],
                "form_id": row["form_id"],
                "form_type": row["form_type"],
                "answerKey": row["answerKey"],
                "pred_norm": pred_norm,
                "pred_raw": pred_raw,
                "correct": int(pred_norm == row["answerKey"]),
                "correct_raw": int(pred_raw == row["answerKey"]),
                "chosen_mean_logprob": round(mean_lp[letters.index(pred_norm)], 6),
                "lp_norm_A": round(norm[0], 6),
                "lp_norm_B": round(norm[1], 6),
                "lp_norm_C": round(norm[2], 6),
                "lp_norm_D": round(norm[3], 6),
            }
        )
        if (index + 1) % 60 == 0 or index + 1 == len(rows):
            print(f"[{label}] scored {index + 1}/{len(rows)}", flush=True)
    return results


def main() -> None:
    args = parse_args()
    banks = {
        "gsm8k_results.csv": read_csv(args.items_dir / "gsm8k_matched_forms.csv"),
        "gsm8k_control_results.csv": read_csv(args.items_dir / "gsm8k_control_bank.csv"),
        "arc_results.csv": read_csv(args.items_dir / "arc_matched_forms.csv"),
        "arc_control_results.csv": read_csv(args.items_dir / "arc_control_bank.csv"),
    }
    for entry in args.models:
        name, _, revision = entry.partition("@")
        safe = name.replace("/", "--")
        out = args.out_dir / safe
        if all((out / fn).is_file() for fn in REQUIRED):
            print(f"Skipping completed model {name}", flush=True)
            continue
        print(f"Loading {name}@{revision}", flush=True)
        tokenizer = AutoTokenizer.from_pretrained(name, revision=revision)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        if torch.cuda.is_available():
            model = AutoModelForCausalLM.from_pretrained(
                name,
                revision=revision,
                torch_dtype=torch.float16,
                device_map="auto",
                low_cpu_mem_usage=True,
            )
        else:
            model = AutoModelForCausalLM.from_pretrained(name, revision=revision, torch_dtype=torch.float32)
        model.eval()
        n_params = sum(p.numel() for p in model.parameters())
        gen_batch = args.gen_batch_small if n_params < 4e9 else args.gen_batch_large
        out.mkdir(parents=True, exist_ok=True)
        environment = {
            "model": name,
            "revision": revision,
            "n_parameters": n_params,
            "torch": torch.__version__,
            "python": platform.python_version(),
            "cuda_device": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
            "gen_batch": gen_batch,
            "max_new_tokens": args.max_new_tokens,
            "decoding": "greedy",
            "amended_parser": args.amended_parser,
        }
        with (out / "environment.json").open("w", encoding="utf-8") as handle:
            json.dump(environment, handle, indent=2)
        write_csv(out / "gsm8k_results.csv", run_gsm8k(model, tokenizer, banks["gsm8k_results.csv"], gen_batch, args.max_new_tokens, f"{safe}/gsm8k", args.amended_parser))
        write_csv(out / "gsm8k_control_results.csv", run_gsm8k(model, tokenizer, banks["gsm8k_control_results.csv"], gen_batch, args.max_new_tokens, f"{safe}/gsm8k-control", args.amended_parser))
        write_csv(out / "arc_results.csv", run_arc(model, tokenizer, banks["arc_results.csv"], args.score_batch, f"{safe}/arc"))
        write_csv(out / "arc_control_results.csv", run_arc(model, tokenizer, banks["arc_control_results.csv"], args.score_batch, f"{safe}/arc-control"))
        del model
        torch.cuda.empty_cache()
        print(f"Completed {name}", flush=True)
    print("All requested models evaluated.", flush=True)


if __name__ == "__main__":
    main()
