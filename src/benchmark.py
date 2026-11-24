# src/benchmark.py
# Milestone 2: run the full question set through EVERY model in
# Ollama and save a results table (results.csv).
#
# Flow:
#   1. ask Ollama "which models do I have?" (GET /api/tags)
#   2. for each model: run all questions, score them, average the time
#   3. append one row per model to results.csv
#      (csv = the lazy person's database: human-readable AND
#       pandas-readable when we build the dashboard in M3)
#
# Robustness rule from price-alert-bot: one model failing mist not
# kill the whole run - record the failure as a row and keep going.

import csv
import json
import time

import requests

from evaluate import score_answer   # reuse M1's scoring

OLLAMA_URL = "http://localhost:11434/api/generate"
TAGS_URL = "http://localhost:11434/api/tags"
RESULTS_PATH = "results.csv"

_session = requests.Session()
_session.trust_env = False  # localhost: no proxy


def list_models():
    """Ask Ollama what's installed -> list of model names."""
    resp = _session.get(TAGS_URL, timeout=30)
    return [m["name"] for m in resp.json()["models"]]


def ask_model(model, question):
    """One question to one model. Returns (answer, seconds)."""
    start = time.time()
    resp = _session.post(OLLAMA_URL, json={
        "model": model,
        "prompt": question,
        "stream": False,
    }, timeout=300)
    return resp.json()["response"].strip(), time.time() - start


def pick_answer(data: dict) -> str:
    strings = [v for v in data.values() if isinstance(v, str)]
    return max(strings, key=len).strip()


def run_model(model, questions):
    """Score one model on the whole set -> (score, avg_seconds)."""
    total_score, total_time = 0.0, 0.0
    for q in questions:
        answer, elapsed = ask_model(model, q["question"])
        total_score += score_answer(answer, q["keywords"])
        total_time += elapsed
    n = len(questions)
    return total_score / n, total_time / n


def main():
    with open("data/questions.jsonl", encoding="utf-8") as f:
        questions = [json.loads(line) for line in f if line.strip()]

    models = list_models()
    print(f"found {len(models)} models: {models}")

    # create results.csv with a header if it doesn't exist yet
    new_file = not __import__("os").path.exists(RESULTS_PATH)
    with open(RESULTS_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if new_file:
            writer.writerow(["model", "score", "avg_seconds", "note"])
        
        for model in models:
            print(f"\nbenchmarking {model}...")
            try:
                score, avg_time = run_model(model, questions)
                note = "ok"
                print(f"  score {score:.2f}  avg {avg_time:.1f}s")
            except Exception as error:
                # model crashed / ran out of RAM / not usable - record it
                score, avg_time, note = 0.0, 0.0, f"FAILED: {error}"
                print(f"  {note}")
            writer.writerow([model, f"{score:.2f}", f"{avg_time:.1f}", note])

    print(f"\nsaved {RESULTS_PATH}")


if __name__ == "__main__":
    main()