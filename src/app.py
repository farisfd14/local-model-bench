# src/app.py
# Milestone 3: turn results.csv into a leaderboard you can look at.
# Streamlit reruns this whole file on every interaction, so it
# always shows the current CSV - just re-run benchmark.py and
# refresh the page.

import pandas as pd
import streamlit as st

RESULTS_PATH = "results.csv"

st.set_page_config(page_title="Local Model Bench", layout="wide")
st.title("Local Model Bench")
st.write("My laptop, my questions, my numbers - no blog benchmarks.")

# --- load data ---
# "a" in benchmark.py appends rows, so re-runs can duplicate models.
# drop_duplicates keeps only each model's LATEST row (keep="last").
df = pd.read_csv(RESULTS_PATH)
df = df.drop_duplicates(subset="model", keep="last")

ok = df[df["note"] == "ok"]
failed = df[df["note"] != "ok"]

# --- headline cards ---
c1, c2, c3 = st.columns(3)
c1.metric("models benched", len(df))
if len(ok):
    best = ok.sort_values("score", ascending=False).iloc[0]
    c2.metric("smartest", best["model"], f"{best['score']:.2f}")
    fastest = ok.sort_values("avg_seconds").iloc[0]
    c3.metric("fastest", fastest["model"], f"{fastest['avg_seconds']:.1f}s")

# --- leaderboard table ---
st.subheader("Leaderboard")
show = df.sort_values("score", ascending=False).copy()
st.dataframe(show, use_container_width=True, hide_index=True)

# --- charts: two different lenses on the same data ---
col_a, col_b = st.columns(2)
with col_a:
    st.subheader("Quality (score)")
    st.bar_chart(ok.set_index("model")["score"])
with col_b:
    st.subheader("Speed (avg seconds per question, lower = better)")

# --- failures, if any: a benchamrk that hides failures is lying ---
if len(failed):
    st.subheader("Failed models (this is data too)")
    st.dataframe(failed, use_container_width=True, hide_index=True)

# --- the fine print: methodology honesty ---
with st.expander("How scoring works (read before trusting this)"):
    st.markdown(
        "- **10 questions**, mix of Chinese and English, including 2 math traps\n"
        "- **score** = fraction of expected keywords found in the answer "
        "(crude but transparent)\n"
        "- **avg_seconds** = CPU generation time per question\n"
        "- run-to-run noise is roughly ±0.10 on score (small models sample "
        "randomly)\n"
        "- with 10 questions, differnces below ~0.15 are not conclusive"
    )