"""
Ragas >= 0.4 evaluation using the collections API, with Groq as the judge LLM.

Install:  pip install "ragas>=0.4.3" openai sentence-transformers python-dotenv pandas
"""
import json
import math
import os
import time

import pandas as pd
from dotenv import load_dotenv
from openai import AsyncOpenAI

from ragas.embeddings import embedding_factory
from ragas.llms import llm_factory
from ragas.metrics.collections import (
    AnswerRelevancy,
    ContextPrecision,
    ContextRecall,
    Faithfulness,
)

# ------------------------------------------------------------
# Config
# ------------------------------------------------------------
# Must be a model ID your Groq account can use (see checkmodel.py output).
# gpt-oss-120b is a reasoning model, but its reasoning is returned separately
# from the answer; it still counts toward max_tokens, hence the larger budget
# and low reasoning effort below.
EVAL_MODEL = "openai/gpt-oss-120b"
EVAL_QUESTION_LIMIT = 5
OUTPUT_FILE = "ragas_baseline_scores.csv"
SLEEP_BETWEEN_ROWS = 2.0  # seconds; raise this if you still hit Groq 429s

load_dotenv()
os.environ["TOKENIZERS_PARALLELISM"] = "false"

if not os.environ.get("GROQ_API_KEY"):
    raise RuntimeError("GROQ_API_KEY is not set. Check your .env file.")

# ------------------------------------------------------------
# Load data
# ------------------------------------------------------------
with open("eval_results.json", "r", encoding="utf-8") as f:
    eval_results = json.load(f)

eval_results = eval_results[:EVAL_QUESTION_LIMIT]
print(f"Loaded {len(eval_results)} evaluation examples.")

existing_scores = {}
if os.path.exists(OUTPUT_FILE):
    previous_df = pd.read_csv(OUTPUT_FILE)
    existing_scores = previous_df.set_index("user_input").to_dict(orient="index")

for i, r in enumerate(eval_results):
    assert isinstance(r["question"], str), f"row {i}: question must be str"
    assert isinstance(r["answer"], str), f"row {i}: answer must be str"
    assert isinstance(r["ground_truth"], str), f"row {i}: ground_truth must be str"
    assert isinstance(r["contexts"], list) and all(
        isinstance(c, str) for c in r["contexts"]
    ), f"row {i}: contexts must be a list of strings"

# ------------------------------------------------------------
# Evaluator LLM: Groq via its OpenAI-compatible endpoint
# ------------------------------------------------------------
groq_client = AsyncOpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
    max_retries=5,   # the client retries 429s with backoff
    timeout=120.0,
)


# Fail fast if the model isn't available, instead of erroring on every row
from openai import OpenAI  # noqa: E402

_sync = OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1")
_available = {m.id for m in _sync.models.list().data}
if EVAL_MODEL not in _available:
    raise SystemExit(
        f"Model '{EVAL_MODEL}' is not available on your Groq account.\n"
        f"Available: {sorted(_available)}"
    )

llm = llm_factory(
    EVAL_MODEL,
    client=groq_client,
    temperature=0.0,
    max_tokens=4096,           # reasoning tokens count toward this
    reasoning_effort="low",    # if this raises a TypeError/unexpected-kwarg error, delete this line
)

# ------------------------------------------------------------
# Embeddings (only AnswerRelevancy needs them). Groq has no embeddings
# endpoint, so use a local sentence-transformers model.
# NOTE: this "huggingface" provider + interface="modern" combo is the one piece
# I could not confirm in the docs. If it errors, see the fallback in the notes.
# ------------------------------------------------------------
print("Loading embedding model...")
embeddings = embedding_factory(
    "huggingface",
    model="sentence-transformers/all-MiniLM-L6-v2",
    interface="modern",
)

# ------------------------------------------------------------
# Metrics
# ------------------------------------------------------------
faithfulness = Faithfulness(llm=llm)
context_precision = ContextPrecision(llm=llm)
context_recall = ContextRecall(llm=llm)
answer_relevancy = AnswerRelevancy(llm=llm, embeddings=embeddings, strictness=1)  # Groq rejects n>1


def safe_score(name, fn, **kwargs):
    """Return a float, or NaN if this metric fails on this row."""
    try:
        return float(fn(**kwargs).value)
    except Exception as e:  # noqa: BLE001
        msg = str(e)
        if any(s in msg for s in ("model_not_found", "invalid_api_key", "Error code: 401")):
            raise SystemExit(f"Fatal config error, stopping: {msg[:300]}")
        print(f"   [!] {name} failed: {type(e).__name__}: {msg[:200]}")
        return math.nan


def score_if_missing(name, fn, previous, **kwargs):
    if previous is not None and not pd.isna(previous):
        return float(previous)
    return safe_score(name, fn, **kwargs)


def run_ragas_evaluation():
    rows = []
    n = len(eval_results)
    print(f"\nScoring {n} questions ({n * 4} metric evaluations)...")

    for i, r in enumerate(eval_results, 1):
        print(f"[{i}/{n}] {r['question'][:70]}")
        q, a, ctx, ref = r["question"], r["answer"], r["contexts"], r["ground_truth"]
        previous = existing_scores.get(q, {})

        rows.append(
            {
                "user_input": q,
                "response": a,
                "reference": ref,
                "faithfulness": score_if_missing(
                    "faithfulness", faithfulness.score,
                    previous.get("faithfulness"),
                    user_input=q, response=a, retrieved_contexts=ctx,
                ),
                "context_precision": score_if_missing(
                    "context_precision", context_precision.score,
                    previous.get("context_precision"),
                    user_input=q, reference=ref, retrieved_contexts=ctx,
                ),
                "context_recall": score_if_missing(
                    "context_recall", context_recall.score,
                    previous.get("context_recall"),
                    user_input=q, reference=ref, retrieved_contexts=ctx,
                ),
                "answer_relevancy": score_if_missing(
                    "answer_relevancy", answer_relevancy.score,
                    previous.get("answer_relevancy"),
                    user_input=q, response=a,
                ),
            }
        )
        time.sleep(SLEEP_BETWEEN_ROWS)

    return pd.DataFrame(rows)


if __name__ == "__main__":
    results_df = run_ragas_evaluation()

    results_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSaved per-question results to: {OUTPUT_FILE}")

    print("\n" + "=" * 60)
    print("MEAN METRIC SCORES (NaN rows skipped)")
    print("=" * 60)
    for metric in ["faithfulness", "context_precision", "context_recall", "answer_relevancy"]:
        n_nan = results_df[metric].isna().sum()
        print(f"{metric:20s}: {results_df[metric].mean():.4f}   (NaN rows: {n_nan})")