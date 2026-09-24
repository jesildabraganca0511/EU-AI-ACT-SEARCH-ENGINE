import os
import time
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


PROJECT_ROOT=Path(__file__).resolve().parents[2]
INPUT_PATH = PROJECT_ROOT / "src" / "eu_ai_act_search_engine" / "results" / "eu_ai_output_chunked.json"

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"  
CHROMA_PATH= PROJECT_ROOT / "src" / "eu_ai_act_search_engine" / "results" / "chroma_db"
COLLECTION_NAME = "eu_ai_act_articles"


GROQ_MODEL = "openai/gpt-oss-120b"           # fast + cheap, good for a baseline
TOP_K = 5
 
 
# --- Setup (runs once) ---------------------------------------------------
 
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_collection(COLLECTION_NAME)
 
# Reads GROQ_API_KEY from the environment automatically.
groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])

def retrieve(query, top_k=TOP_K):
    query_embedding = embedding_model.encode([query]).tolist()
 
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
    )
 
    # Reshape Chroma's nested-list response into a flat list of chunks,
    # each carrying its text + metadata together — easier to work with
    # in the next step than Chroma's raw parallel-lists format.
    chunks = []
    for text, meta in zip(results["documents"][0], results["metadatas"][0]):
        chunks.append({
            "text": text,
            "article_number": meta["article_number"],
            "article_title": meta["article_title"],
        })
    return chunks



def build_prompt(query, chunks):
    # Each chunk gets labeled with its article number in the prompt itself,
    # so the model has something concrete to cite back.
    context_blocks = []
    for chunk in chunks:
        block = f"[{chunk['article_number']} - {chunk['article_title']}]\n{chunk['text']}"
        context_blocks.append(block)
    context = "\n\n---\n\n".join(context_blocks)
 
    prompt = f"""You are a compliance assistant answering questions about the EU AI Act.
 
Answer the question using ONLY the context below. For every claim you make,
cite the article it came from using this exact format: [Article N] or [Annex N].
If the context doesn't contain enough information to answer, say so explicitly
instead of guessing.
 
Context:
{context}
 
Question: {query}
 
Answer:"""
    return prompt



def generate(prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = groq_client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 60
                print(f"Generation failed ({e}), retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
    raise RuntimeError("Failed to generate response after multiple retries")
# --- Wire it all together, with latency logging per stage ------------------
 
def ask(query, top_k=TOP_K):
    t0 = time.perf_counter()
    chunks = retrieve(query, top_k)
    t1 = time.perf_counter()
 
    prompt = build_prompt(query, chunks)
    answer = generate(prompt)
    t2 = time.perf_counter()
 
    latency = {
        "retrieve_seconds": round(t1 - t0, 3),
        "generate_seconds": round(t2 - t1, 3),
        "total_seconds": round(t2 - t0, 3),
    }
 
    return {
        "query": query,
        "answer": answer,
        "sources": [c["article_number"] for c in chunks],
        "contexts": [c["text"] for c in chunks],
        "latency": latency,
    }
 
 
# --- Run a few test questions ------------------------------------------------
 
if __name__ == "__main__":
    test_questions = [
        "What are the requirements for high-risk AI systems?",
        "What counts as a high-risk AI use case?",
        "What penalties apply for non-compliance?",
    ]
 
    for question in test_questions:
        try:
            result = ask(question)
            print("=" * 70)
            print("Q:", result["query"])
            print("\nA:", result["answer"])
            print("\nSources:", result["sources"])
            print("Latency:", result["latency"])
            print()
        except Exception as e:
            print("=" * 70)
            print("Q:", question)
            print(f"FAILED: {e}")
            print()
 



