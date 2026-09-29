# Balladesh-RAG

RAG assistant for the scanned Bengali PDF **Balladesh**.

## Stack

- **FastAPI** backend
- **Streamlit** frontend
- **LangChain** + **FAISS**
- **Groq** for chat
- **Tesseract** OCR (`ben` / `ben+eng`) for Bengali scans
- **sentence-transformers** multilingual embeddings

## Layout

```text
Balladesh-RAG/
├── backend/app/     # FastAPI app + OCR module
├── frontend/        # Streamlit UI (later)
├── data/            # Source PDF (Balladesh.pdf)
├── ocr_output/      # Cached OCR JSON (page_001.json, ...)
├── vectorstore/     # FAISS index (later)
└── tests/
```

## Status

- `GET /health` — ready
- OCR for pages 1–5 — ready (cached under `ocr_output/`)
- Chunking / embeddings / FAISS / RAG / Streamlit — not yet

## Ubuntu system dependencies (OCR)

Required for PDF → image rendering and Bengali OCR:

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-ben tesseract-ocr-eng poppler-utils
```

Verify:

```bash
tesseract --version
tesseract --list-langs   # should include ben and eng
pdftoppm -v
```

## Quick start (Ubuntu)

```bash
cd Balladesh-RAG
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

Place the book at `data/Balladesh.pdf`, then OCR the first 5 pages:

```bash
python -m backend.app.ocr --start 1 --end 5
```

Re-running the same command skips pages that already have JSON (cache).

Expected files:

```text
ocr_output/page_001.json
ocr_output/page_002.json
ocr_output/page_003.json
ocr_output/page_004.json
ocr_output/page_005.json
```

API (optional):

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check: http://localhost:8000/health
