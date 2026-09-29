"""Configuration for Balladesh-RAG.

Paths are project-relative. Tunables (chunk size, models, OCR) can be
overridden via environment variables — same idea as DocuMind's config.
"""

from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

PROJECT_ROOT = Path(__file__).resolve().parents[2]

GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "")
LLM_MODEL: str = os.environ.get("LLM_MODEL", "llama-3.3-70b-versatile")
EMBEDDING_MODEL: str = os.environ.get(
    "EMBEDDING_MODEL",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)

PDF_PATH: Path = PROJECT_ROOT / os.environ.get("PDF_PATH", "data/Balladesh.pdf")
OCR_OUTPUT_DIR: Path = PROJECT_ROOT / os.environ.get("OCR_OUTPUT_DIR", "ocr_output")
VECTORSTORE_DIR: Path = PROJECT_ROOT / os.environ.get("VECTORSTORE_DIR", "vectorstore")
# Intermediate chunk dump (FAISS comes later; DocuMind writes straight to FAISS)
CHUNKS_PATH: Path = VECTORSTORE_DIR / "chunks.json"

# DocuMind-style splitter knobs (Balladesh defaults tuned for OCR pages)
CHUNK_SIZE: int = int(os.environ.get("CHUNK_SIZE", "700"))
CHUNK_OVERLAP: int = int(os.environ.get("CHUNK_OVERLAP", "120"))
TOP_K: int = int(os.environ.get("TOP_K", "4"))

# ben+eng covers mixed Bangla/English CamScanner pages; use "ben" for Bangla-only
TESSERACT_LANG: str = os.environ.get("TESSERACT_LANG", "ben+eng")
OCR_DPI: int = int(os.environ.get("OCR_DPI", "300"))
