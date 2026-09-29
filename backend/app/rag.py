"""Build the LCEL RAG chain: retriever -> prompt -> Groq -> parser.

Same small structure as DocuMind's ``rag_chain.py``.
"""
from functools import lru_cache

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from .config import COLLECTION, TOP_K, get_settings
from .db import get_retriever

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
    """Sources from FAISS metadata only — never from the LLM."""
    sources = []
    for doc in docs:
        meta = doc.metadata or {}
        snippet = (doc.page_content or "").replace("\n", " ").strip()
        if len(snippet) > 200:
            snippet = snippet[:197] + "..."
        sources.append(
            {
                "page": meta.get("page_number", meta.get("page")),
                "chunk_id": meta.get("chunk_id"),
                "snippet": snippet,
            }
        )
    return sources


def ask(
    question: str,
    collection: str | None = None,
    k: int | None = None,
) -> dict:
    """Retrieve context, prompt Groq, return {answer, sources}."""
    llm = _get_llm()
    retriever = get_retriever(collection or COLLECTION, k=k or TOP_K)

    docs = retriever.invoke(question)
    context = _format_docs(docs)
    answer = (_prompt | llm | StrOutputParser()).invoke(
        {"context": context, "question": question}
    )
    return {"answer": answer, "sources": _make_sources(docs)}
