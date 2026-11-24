# local-model-bench

A tiny benchmark lab for the local LLMs on my laptop (Ollama). Same
10 questions, every model, timed and scored - because study-bot and
lecture-notes-ai both depends on these models, and I wanted to know
which brain to trust, from my own data instead of a blog post.

## Results (my machine, CPU only)

| model | score | avg s/question |
| ----- | ----- | -------------- |
| qwen2.5:3b | 0.77 | 7.9 |
| llama3.2:1b | 0.63 | 4.9 |

Read the numbers honestly:
- qwen wins on quality, llama wins on speed - the classic tradeoff
- run-to-run noise is roughly ±0.10 (small models sample randomly)
- with only 10 questions, gaps below ~0.15 are not conclusive

## How it works

1. `data/questions.jsonl` - 10 questions (Chinese + English, including
   2 math traps), each with expected keywords
2. `src/evaluate.py` - one model, full run, printed + timed
3. `src/benchmark.py` - loops every model from `ollama list`, appends
   one row per model to `results.csv`. One model crashing doesn't
   stop the run - the failure becomes a row.
4. `src/app.py` - Streamlit leaderboard: cards, table, quality/speed
   charts, plus the methodology caveats printed next to the results

## Scoring method (deliberately crude)

score = fraction of the question's expected keywords that appear in
the answer. A fancy LLM-judge would be smoother but hides its
failures; keyword matching is transparent and good enough to rank
small models.

## Run it

- `pip install -r requirements.txt`
- `ollama pull qwen2.5:3b` # and any rivals you want to test
- `python src/benchmark.py` # long run on CPU - it's a benchmark
- `streamlit run src/app.py`

Add questions by appending lines to `data/questions.jsonl` -
the more (and harder) the better.