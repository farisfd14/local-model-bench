# src/evaluate.py
# Milestone 1: ask ONE model ONE question, time it, score it.
#
# Scoring is deliberately simple and honest:
#   correct = how many of the question's keywords appear in the answer
#   score = correct / total keywords
# This is crude (a model could keyword-stuff) but it's transparent -
# the README will say exactly how scoring works. fancy LLM-judges hide
# their failures; keyword matching hides nothing.

import json
import time

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "qwen2.5:3b"    # change to any model from `ollama list`

_session = requests.Session()
_session.trust_env = False  # localhost: no proxy


def pick_answer(data: dict) -> str:
    strings = [v for v in data.values() if isinstance(v, str)]
    return max(strings, key=len).strip()


def ask(question: str) -> tuple[str, float]:
    """Returns (answer_text, seconds_it_took)."""
    start = time.time()
    resp = _session.post(OLLAMA_URL, json={
        "model": MODEL,
        "prompt": question,
        "stream": False,
    }, timeout=300)
    elapsed = time.time() - start
    return pick_answer(resp.json()), elapsed


def score_answer(answer: str, keywords: list) -> float:
    """Fraction of expected keywords found in the answer."""
    hits = sum(1 for kw in keywords if kw.lower() in answer.lower())
    return hits / len(keywords)


def main():
    with open("data/questions.jsonl", encoding="utf-8") as f:
        questions = [json.loads(line) for line in f if line.strip()]

    total_score, total_time = 0.0, 0.0
    for q in questions:
        answer, elapsed = ask(q["question"])
        score = score_answer(answer, q["keywords"])
        total_score += score
        total_time += elapsed
        mark = "OK " if score == 1.0 else f"{score:.1f}"
        print(f"[{mark}] {q['question'][:30]}  ({elapsed:.1f}s)")
        print(f"    - > {answer[:100]}")

    n = len(questions)
    print(f"\nMODEL: {MODEL}")
    print(f"score: {total_score / n:.2f}  ({total_score:.1f}/{n})")
    print(f"avg time per qeustion: {total_time / n:.1f}s")


if __name__ == "__main__":
    main()