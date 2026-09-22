import json
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, context_precision, context_recall, answer_relevancy
from ragas.llms import llm_factory
import os
from google import genai


#Load the results from eval_results.json


with open("eval_results.json", "r", encoding="utf-8") as f:
    eval_results = json.load(f)

dataset=Dataset.from_dict(
    {
        "question": [r["question"] for r in eval_results],
    "answer": [r["answer"] for r in eval_results],
    "contexts": [r["contexts"] for r in eval_results],
    "ground_truth": [r["ground_truth"] for r in eval_results],
    }
)


client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
evaluator_llm = llm_factory("gemini-2.0-flash", provider="google", client=client)
 
 
print(f"Scoring {len(eval_results)} questions with Ragas...")
 
scores = evaluate(
    dataset,
    metrics=[faithfulness, context_precision, context_recall, answer_relevancy],
    llm=evaluator_llm,
)
 
print("\n" + "=" * 50)
print("BASELINE SCORES (Day 3-4)")
print("=" * 50)
print(scores)
 

results_df = scores.to_pandas()
results_df.to_csv("ragas_baseline_scores.csv", index=False)
print("\nSaved per-question breakdown to ragas_baseline_scores.csv")


