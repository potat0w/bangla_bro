# Balladesh-RAG

RAG assistant for the scanned Bengali PDF **Balladesh**.

## Stack

- **FastAPI** backend
- **Streamlit** frontend
- **LangChain** + **FAISS**
- **Groq** for chat
- **Tesseract** OCR (`ben`) for Bengali scans
- **sentence-transformers** multilingual embeddings

## Layout

```text
Balladesh-RAG/
├── backend/app/     # FastAPI app
├── frontend/        # Streamlit UI (later)
├── data/            # Source PDF
├── ocr_output/      # Cached OCR text
├── vectorstore/     # FAISS index
└── tests/
```

## Status

Scaffold only. Implemented so far: `GET /health`.

## Quick start (Ubuntu)

```bash
cd Balladesh-RAG
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env and set GROQ_API_KEY when you need chat

uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check: http://localhost:8000/health

## System deps (later, for OCR)

```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-ben poppler-utils
```
