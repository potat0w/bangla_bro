"""FastAPI app: /health, /ask — thin wrapper over rag.ask()."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .db import index_exists
from .rag import ask as ask_rag
from .schemas import AskRequest, AskResponse

app = FastAPI(title="Balladesh-RAG")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "index_ready": index_exists(),
    }


@app.post("/ask", response_model=AskResponse)
def ask(req: AskRequest):
    try:
        return ask_rag(question=req.question)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to generate an answer.")
