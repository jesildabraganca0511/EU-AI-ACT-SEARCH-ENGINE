from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

PDF_PATH = DATA_DIR / "eu_ai_act.pdf"
ARTICLES_PATH = DATA_DIR / "eu_ai_output.json"
CHUNKS_PATH = DATA_DIR / "eu_ai_output_chunked.json"
CHROMA_PATH = DATA_DIR / "chroma_db"

EVAL_RESULTS_PATH = OUTPUTS_DIR / "eval_results.json"
RAGAS_SCORES_PATH = OUTPUTS_DIR / "ragas_baseline_scores.csv"
