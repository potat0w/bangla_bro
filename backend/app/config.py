"""Configuration placeholders. Loaded from environment / .env later."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

GROQ_API_KEY: str = ""
LLM_MODEL: str = "llama-3.3-70b-versatile"
EMBEDDING_MODEL: str = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

PDF_PATH: Path = PROJECT_ROOT / "data" / "Balladesh.pdf"
OCR_OUTPUT_DIR: Path = PROJECT_ROOT / "ocr_output"
VECTORSTORE_DIR: Path = PROJECT_ROOT / "vectorstore"

CHUNK_SIZE: int = 1000
CHUNK_OVERLAP: int = 150
TOP_K: int = 4

# ben+eng covers mixed Bangla/English CamScanner pages; use "ben" for Bangla-only
TESSERACT_LANG: str = "ben+eng"
OCR_DPI: int = 300
