"""Build the FAISS vector store and persist it to disk.

Same architecture as DocuMind's ``db.py``:
- FAISS in memory, saved under a collection subdirectory
- load existing index when present
- build only when missing or explicitly forced

Balladesh difference: documents come from ``processed/chunks.json``
(OCR → chunk pipeline), not live PDF ingest.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from .config import (
    CHUNKS_PATH,
    COLLECTION,
    EMBEDDING_MODEL,
    TOP_K,
    VECTORSTORE_DIR,
)
from .embeddings import get_embeddings

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# DocuMind: INDEX_DIR / collection. Balladesh: VECTORSTORE_DIR / collection.
INDEX_DIR = VECTORSTORE_DIR


def _path(collection: str) -> Path:
    return INDEX_DIR / collection


def index_exists(collection: str | None = None) -> bool:
    name = collection or COLLECTION
    return (_path(name) / "index.faiss").exists()


def _load(collection: str) -> FAISS | None:
    """Load a collection from disk, or return None if it doesn't exist."""
    path = _path(collection)
    if (path / "index.faiss").exists():
        return FAISS.load_local(
            str(path),
            get_embeddings(),
            allow_dangerous_deserialization=True,
        )
    return None


def _save(store: FAISS, collection: str) -> None:
    path = _path(collection)
    path.mkdir(parents=True, exist_ok=True)
    store.save_local(str(path))


def get_retriever(collection: str, k: int):
    """Return a retriever over a FAISS collection."""
    store = _load(collection)
    if store is None:
        raise ValueError(
            f"Collection '{collection}' not found. "
            "Build the index first: python -m backend.app.db --build"
        )
    return store.as_retriever(search_kwargs={"k": k})


def get_store(collection: str | None = None) -> FAISS:
    name = collection or COLLECTION
    store = _load(name)
    if store is None:
        raise ValueError(
            f"Collection '{name}' not found. "
            "Build the index first: python -m backend.app.db --build"
        )
    return store


def add_documents_to_collection(collection: str, docs) -> FAISS:
    """Embed and persist a list of LangChain Document objects (DocuMind pattern)."""
    usable = [d for d in docs if (d.page_content or "").strip()]
    if not usable:
        raise ValueError("No usable chunk text found to index.")

    existing = _load(collection)
    if existing is None:
        store = FAISS.from_documents(usable, get_embeddings())
    else:
        existing.add_documents(usable)
        store = existing
    _save(store, collection)
    return store


def chunks_to_documents(chunks: list[dict]) -> list[Document]:
    """Convert processed chunk dicts into LangChain Documents with metadata."""
    docs: list[Document] = []
    for chunk in chunks:
        text = chunk.get("text") or ""
        if not str(text).strip():
            continue
        page_number = int(chunk["page_number"])
        chunk_id = str(chunk["chunk_id"])
        docs.append(
            Document(
                page_content=text,
                metadata={
                    "page_number": page_number,
                    "chunk_id": chunk_id,
                    # DocuMind rag_chain reads metadata["page"]
                    "page": page_number,
                },
            )
        )
    return docs


def load_chunks(chunks_path: Path | None = None) -> list[dict]:
    path = Path(chunks_path) if chunks_path else CHUNKS_PATH
    if not path.is_file():
        raise FileNotFoundError(
            f"Chunks file not found: {path}\n"
            "Run chunking first: python -m backend.app.ingestion"
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    chunks = data.get("chunks")
    if not isinstance(chunks, list) or not chunks:
        raise ValueError(f"No chunks found in {path}")
    return chunks


def build_index(
    collection: str | None = None,
    chunks_path: Path | None = None,
    force: bool = False,
) -> dict:
    """
    Build FAISS from processed/chunks.json.

    If an index already exists and force is False, load it and skip rebuild.
    """
    name = collection or COLLECTION
    if index_exists(name) and not force:
        store = get_store(name)
        count = store.index.ntotal
        logger.info(
            "Existing FAISS index found at %s — loading without rebuild (%s vectors).",
            _path(name),
            count,
        )
        return {
            "collection": name,
            "index_path": str(_path(name)),
            "vectors": count,
            "rebuilt": False,
            "embedding_model": EMBEDDING_MODEL,
        }

    if force and index_exists(name):
        # Replace collection directory for a clean rebuild
        import shutil

        shutil.rmtree(_path(name))
        logger.info("Removed existing index at %s (--force).", _path(name))

    chunks = load_chunks(chunks_path)
    docs = chunks_to_documents(chunks)
    logger.info(
        "Building FAISS index for %s documents (model=%s)...",
        len(docs),
        EMBEDDING_MODEL,
    )
    store = add_documents_to_collection(name, docs)
    count = store.index.ntotal
    logger.info("Indexed %s vectors → %s", count, _path(name))
    return {
        "collection": name,
        "index_path": str(_path(name)),
        "vectors": count,
        "rebuilt": True,
        "embedding_model": EMBEDDING_MODEL,
        "source_chunks": len(chunks),
    }


def search(
    query: str,
    k: int | None = None,
    collection: str | None = None,
) -> list[dict]:
    """Retrieval-only: top-k similar chunks with scores (no LLM)."""
    name = collection or COLLECTION
    top_k = k if k is not None else TOP_K
    store = get_store(name)
    pairs = store.similarity_search_with_score(query, k=top_k)

    results: list[dict] = []
    for rank, (doc, score) in enumerate(pairs, start=1):
        meta = doc.metadata or {}
        results.append(
            {
                "rank": rank,
                "page_number": meta.get("page_number", meta.get("page")),
                "chunk_id": meta.get("chunk_id"),
                "score": float(score),
                "text": doc.page_content,
            }
        )
    return results


def _print_results(query: str, results: list[dict]) -> None:
    logger.info("Query: %s", query)
    logger.info("")
    for item in results:
        snippet = (item["text"] or "").replace("\n", " ")
        if len(snippet) > 280:
            snippet = snippet[:277] + "..."
        logger.info("Result %s", item["rank"])
        logger.info("Page: %s", item["page_number"])
        logger.info("Chunk: %s", item["chunk_id"])
        logger.info("Score: %s", item["score"])
        logger.info("Text: %s", snippet)
        logger.info("")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Balladesh FAISS index build / retrieval test (no LLM)."
    )
    parser.add_argument(
        "--build",
        action="store_true",
        help="Build FAISS from processed/chunks.json (skips if index exists)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="With --build, delete and rebuild an existing index",
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Bangla (or English) retrieval query — no LLM, FAISS only",
    )
    parser.add_argument(
        "--k",
        type=int,
        default=5,
        help="Top-k results for --query (default: 5)",
    )
    parser.add_argument(
        "--collection",
        type=str,
        default=COLLECTION,
        help=f"FAISS collection name (default: {COLLECTION})",
    )
    parser.add_argument(
        "--chunks",
        type=Path,
        default=CHUNKS_PATH,
        help=f"Path to chunks.json (default: {CHUNKS_PATH})",
    )
    args = parser.parse_args(argv)

    if not args.build and not args.query:
        parser.error("Specify --build and/or --query")

    try:
        if args.build:
            info = build_index(
                collection=args.collection,
                chunks_path=args.chunks,
                force=args.force,
            )
            logger.info(
                "Vectors indexed: %s | path: %s | rebuilt: %s",
                info["vectors"],
                info["index_path"],
                info["rebuilt"],
            )

        if args.query:
            results = search(
                query=args.query,
                k=args.k,
                collection=args.collection,
            )
            _print_results(args.query, results)
    except (FileNotFoundError, ValueError, OSError) as exc:
        logger.error("%s", exc)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
