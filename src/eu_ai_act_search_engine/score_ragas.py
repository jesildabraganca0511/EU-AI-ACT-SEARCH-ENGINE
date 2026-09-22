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

dataset=Dataset.from_dict