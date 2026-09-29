"""Build the LCEL RAG chain: retriever -> prompt -> Groq -> parser.

Same architecture as DocuMind's ``rag_chain.py``, with a stricter grounded
prompt for Bangla/English Balladesh answers and FAISS-derived sources.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from functools import lru_cache

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from .config import CHUNKS_PATH, COLLECTION, TOP_K, get_settings
from .db import get_retriever

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are a careful reading assistant for the Bangla book Balladesh.\n"
    "Answer the user's question using ONLY the book context provided below.\n"
    "Rules:\n"
    "- Use only facts that appear in the context. Do not invent details.\n"
    "- Do not invent or guess page numbers.\n"
    "- If the answer is not supported by the context, say clearly that the "
    "information was not found in the provided book context.\n"
    "- If the user asks in Bangla, answer in Bangla. If they ask in English, "
    "answer in English.\n"
    "- Keep the answer natural and readable.\n"
    "- Do not mention FAISS, embeddings, chunks, retrieval, or other internal "
    "system details unless the user explicitly asks about the system.\n\n"
    "Context:\n{context}"
)

_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "{question}"),
    ]
)


@lru_cache(maxsize=1)
def _get_llm() -> ChatGroq:
    """Lazily build ChatGroq. Reads GROQ_API_KEY on first call (DocuMind pattern)."""
    s = get_settings()
    return ChatGroq(model=s.llm_model, api_key=s.groq_api_key, temperature=0)


def _format_docs(docs) -> str:
    return "\n\n".join(
        f"[{i}] (page {doc.metadata.get('page_number', doc.metadata.get('page', '?'))}) "
        f"{doc.page_content}"
        for i, doc in enumerate(docs, start=1)
    )


def _make_sources(docs) -> list[dict]:
    """Build sources from FAISS document metadata (never from the LLM)."""
    sources: list[dict] = []
    seen: set[str] = set()
    for doc in docs:
        meta = doc.metadata or {}
        chunk_id = meta.get("chunk_id")
        page = meta.get("page_number", meta.get("page"))
        key = str(chunk_id) if chunk_id is not None else f"{page}:{doc.page_content[:40]}"
        if key in seen:
            continue
        seen.add(key)
        snippet = (doc.page_content or "").replace("\n", " ").strip()
        if len(snippet) > 200:
            snippet = snippet[:197] + "..."
        sources.append(
            {
                "page": page,
                "chunk_id": chunk_id,
                "snippet": snippet,
            }
        )
    return sources


def _expand_same_page_context(docs: list[Document]) -> list[Document]:
    """If FAISS hits a thin heading chunk, pull sibling chunks from that page.

    Does not rebuild FAISS — reads existing processed/chunks.json only.
    Sources still come from document metadata, never from the LLM.
    """
    if not docs or not CHUNKS_PATH.is_file():
        return docs

    hit_ids = {
        str(d.metadata.get("chunk_id"))
        for d in docs
        if d.metadata.get("chunk_id") is not None
    }
    # Expand only the top retrieved pages (keeps context bounded)
    hit_pages: list[int] = []
    for doc in docs:
        page = doc.metadata.get("page_number", doc.metadata.get("page"))
        if page is None:
            continue
        page_i = int(page)
        if page_i not in hit_pages:
            hit_pages.append(page_i)
        if len(hit_pages) >= 2:
            break
    hit_page_set = set(hit_pages)

    try:
        raw = json.loads(CHUNKS_PATH.read_text(encoding="utf-8")).get("chunks", [])
    except (OSError, json.JSONDecodeError, TypeError):
        return docs

    expanded = list(docs)
    for chunk in raw:
        page = chunk.get("page_number")
        chunk_id = str(chunk.get("chunk_id", ""))
        text = chunk.get("text") or ""
        if page not in hit_page_set or chunk_id in hit_ids or not str(text).strip():
            continue
        hit_ids.add(chunk_id)
        expanded.append(
            Document(
                page_content=text,
                metadata={
                    "page_number": int(page),
                    "chunk_id": chunk_id,
                    "page": int(page),
                },
            )
        )
    # Prefer original retrieval order, then page/chunk_id for siblings
    expanded.sort(
        key=lambda d: (
            0 if str(d.metadata.get("chunk_id")) in {
                str(x.metadata.get("chunk_id")) for x in docs
            } else 1,
            int(d.metadata.get("page_number", d.metadata.get("page") or 0)),
            str(d.metadata.get("chunk_id") or ""),
        )
    )
    return expanded


def ask(
    question: str,
    collection: str | None = None,
    k: int | None = None,
) -> dict:
    """Retrieve context, prompt Groq, return {answer, sources}.

    DocuMind LCEL pattern:
        docs = retriever(question)
        answer = prompt(context, question) | llm | parser
        sources from FAISS metadata only
    """
    name = collection or COLLECTION
    top_k = TOP_K if k is None else k
    llm = _get_llm()
    retriever = get_retriever(name, k=top_k)

    docs = retriever.invoke(question)
    context_docs = _expand_same_page_context(docs)
    context = _format_docs(context_docs)
    chain = _prompt | llm | StrOutputParser()
    answer = chain.invoke({"context": context, "question": question})
    # Sources from FAISS retrieval metadata only (not LLM-invented pages)
    return {"answer": answer, "sources": _make_sources(docs)}


def _print_result(question: str, result: dict) -> None:
    logger.info("Question:")
    logger.info("%s", question)
    logger.info("")
    logger.info("Answer:")
    logger.info("%s", result["answer"])
    logger.info("")
    logger.info("Sources:")
    if not result["sources"]:
        logger.info("(none)")
        return
    for src in result["sources"]:
        logger.info("Page %s — %s", src.get("page"), src.get("chunk_id"))
        logger.info("%s", src.get("snippet", ""))
        logger.info("")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Ask Balladesh a grounded RAG question (Groq + FAISS)."
    )
    parser.add_argument(
        "--question",
        "-q",
        required=True,
        help="Question in Bangla or English",
    )
    parser.add_argument(
        "--k",
        type=int,
        default=None,
        help=f"Top-k retrieved chunks (default: {TOP_K})",
    )
    parser.add_argument(
        "--collection",
        default=COLLECTION,
        help=f"FAISS collection (default: {COLLECTION})",
    )
    args = parser.parse_args(argv)

    try:
        result = ask(
            question=args.question,
            collection=args.collection,
            k=args.k,
        )
    except (KeyError, ValueError, OSError) as exc:
        logger.error("%s", exc)
        return 1
    except Exception as exc:  # surface Groq/API errors clearly
        logger.error("RAG request failed: %s", exc)
        return 1

    _print_result(args.question, result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
