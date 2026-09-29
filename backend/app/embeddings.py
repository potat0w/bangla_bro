"""Local sentence-transformers embeddings — no API key needed.

Same pattern as DocuMind's ``embeddings.py``, but the model name comes from
config (multilingual MiniLM for Bangla).
"""
from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings

from .config import EMBEDDING_MODEL


@lru_cache(maxsize=1)
def get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
