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
├── processed/       # Chunk JSON (chunks.json)
├── vectorstore/     # FAISS index (vectorstore/balladesh/)
└── tests/
```

## Status

- `GET /health` — ready
- OCR for all 121 pages — ready (cached under `ocr_output/`)
- Chunking — ready (`processed/chunks.json`)
- Multilingual embeddings + FAISS — ready
- Groq RAG / Streamlit — not yet

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

Place the book at `data/Balladesh.pdf`, then OCR (skips cached pages):

```bash
python -m backend.app.ocr --start 1 --end 121
```

Chunk OCR pages into RAG-ready pieces (no embeddings yet):

```bash
python -m backend.app.ingestion
```

Output: `processed/chunks.json` (each chunk has `chunk_id`, `page_number`, `text`).

Build the FAISS index from those chunks (skips rebuild if the index already exists):

```bash
python -m backend.app.db --build
```

Force a full rebuild:

```bash
python -m backend.app.db --build --force
```

Retrieval-only test (no Groq / no LLM):

```bash
python -m backend.app.db --query "বাংলা ভাষার উৎপত্তি কী?" --k 5
```

API (optional):

```bash
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check: http://localhost:8000/health
