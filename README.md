# EU AI Act Search Engine

A retrieval-augmented generation (RAG) assistant that answers questions about the **EU AI Act (Regulation (EU) 2024/1689)** with answers grounded in the text of the Act and cited by article.

> **Example**
> **Q:** What are the requirements for high-risk AI systems?
> **A:** High-risk AI systems must achieve an appropriate level of accuracy, robustness and cybersecurity throughout their lifecycle [Article 15], be subject to human oversight [Article 14] …

<!-- Add a screenshot or GIF of the assistant answering a question here -->

## How it works

```
EUR-Lex PDF ──► Ingestion ──► Chunking ──► Embedding ──► ChromaDB
                (split by     (1,000 chars,  (all-MiniLM-     │
                 article,      100 overlap)   L6-v2)          │
                 validated                                    ▼
                 with Pydantic)                User question ─► Retrieve top-5 chunks
                                                                    │
                                                                    ▼
                                              Groq LLM (gpt-oss-120b) answers using ONLY
                                              the retrieved context, citing [Article N]
                                                                    │
                                                                    ▼
                                              Ragas evaluation (LLM-as-judge)
```

| Stage | File | What it does |
|---|---|---|
| Ingestion | `ingestion.py` | Downloads the Act from EUR-Lex, strips headers/footers, splits it into articles, validates each with Pydantic |
| Chunking | `chunking.py` | Splits articles into overlapping chunks, keeping article number and title as metadata |
| Embedding | `embedding.py` | Embeds chunks with `all-MiniLM-L6-v2` and stores them in a persistent ChromaDB collection |
| Retrieval + generation | `retrieval_generation.py` | Retrieves the top-k chunks and prompts the LLM to answer only from that context, with article citations |
| Evaluation | `eval_set.py`, `score_ragas.py` | 20 hand-written questions with ground-truth answers; scored with Ragas |

## Evaluation (baseline)

Scored with Ragas, using Groq `gpt-oss-120b` as the judge, on the first 5 questions of the eval set:

| Metric | Score |
|---|---|
| Faithfulness | **1.00** |
| Answer relevancy | 0.69 |
| Context precision | 0.58 |
| Context recall | 0.53 |

**What this shows:** the model does not hallucinate beyond the retrieved context (faithfulness = 1.0), but **retrieval is the bottleneck**. For some questions, the right articles are not in the top 5. For one question (penalties), retrieval missed completely.

**Next steps:** article-aware chunking, hybrid search (BM25 + embeddings), a re-ranker, and scoring the full 20-question set.

## Quickstart

Requires [uv](https://docs.astral.sh/uv/) and a free [Groq API key](https://console.groq.com/).

```bash
git clone https://github.com/jesildabraganca0511/EU-AI-ACT-SEARCH-ENGINE.git
cd EU-AI-ACT-SEARCH-ENGINE
uv sync
cp .env.example .env          # then add your GROQ_API_KEY

# Build the index (run once)
uv run python -m eu_ai_act_search_engine.ingestion
uv run python -m eu_ai_act_search_engine.chunking
uv run python -m eu_ai_act_search_engine.embedding

# Ask questions
uv run python -m eu_ai_act_search_engine.retrieval_generation

# Evaluate
uv run python -m eu_ai_act_search_engine.eval_set
uv run python -m eu_ai_act_search_engine.score_ragas
```

## Tech stack

Python · uv · ChromaDB · Sentence-Transformers · Groq · Pydantic · Ragas · GitHub Actions (CI: ruff lint + import checks)

## Project structure

```
src/eu_ai_act_search_engine/   pipeline code
data/                          source PDF and processed JSON (generated, not committed)
outputs/                       evaluation results
tests/                         unit tests
.github/workflows/ci.yml       CI
```

## Limitations

- Fixed-size character chunking can split an article mid-sentence.
- Evaluated on a small set of questions so far.
- This is not legal advice.

## Author

Jesilda Braganca, MSc Computing (AI), Dublin City University · [LinkedIn](https://www.linkedin.com/in/YOUR-HANDLE)