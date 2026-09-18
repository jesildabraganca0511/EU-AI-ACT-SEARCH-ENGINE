import json
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer

PROJECT_ROOT=Path(__file__).resolve().parents[2]
INPUT_PATH = PROJECT_ROOT / "src" / "eu_ai_act_search_engine" / "results" / "eu_ai_output_chunked.json"

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"  # or any other suitable model
CHROMA_PATH= PROJECT_ROOT / "src" / "eu_ai_act_search_engine" / "results" / "chroma_db"
COLLECTION_NAME = "eu_ai_act_articles"
