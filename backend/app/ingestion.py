"""OCR page ingestion: load page JSON -> split -> persist chunks.

Mirrors DocuMind's ``ingestion.py`` flow (load -> RecursiveCharacterTextSplitter)
but reads cached OCR pages instead of PyPDFLoader, and stops before embed/FAISS.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import CHUNK_OVERLAP, CHUNK_SIZE, CHUNKS_PATH, OCR_OUTPUT_DIR

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger(__name__)

_PAGE_FILE_RE = re.compile(r"^page_(\d+)\.json$")


def load_ocr_pages(ocr_dir: Path | None = None) -> list[dict]:
    """Load all ``page_XXX.json`` files, sorted by page number."""
    ocr_dir = Path(ocr_dir) if ocr_dir else OCR_OUTPUT_DIR
    if not ocr_dir.is_dir():
        raise FileNotFoundError(
            f"OCR output directory not found: {ocr_dir}\n"
            "Run OCR first: python -m backend.app.ocr --start 1 --end 121"
        )

    pages: list[dict] = []
    for path in sorted(ocr_dir.iterdir()):
        if not path.is_file():
            continue
        match = _PAGE_FILE_RE.match(path.name)
        if not match:
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        page_num = int(data.get("page", match.group(1)))
        text = data.get("text", "")
        if not isinstance(text, str):
            text = "" if text is None else str(text)
        pages.append({"page": page_num, "text": text, "path": path})

    pages.sort(key=lambda item: item["page"])
    if not pages:
        raise FileNotFoundError(
            f"No page_XXX.json files found under {ocr_dir}. "
            "Run OCR before chunking."
        )
    return pages


def _chunk_page_text(
    text: str,
    page_number: int,
    splitter: RecursiveCharacterTextSplitter,
) -> list[dict]:
    """Split one page only — never merge text across pages."""
    # DocuMind: Document per page, then RecursiveCharacterTextSplitter
    doc = Document(
        page_content=text,
        metadata={
            "page": page_number,  # DocuMind rag_chain uses metadata["page"]
            "page_number": page_number,
        },
    )
    split_docs = splitter.split_documents([doc])
    chunks: list[dict] = []
    for index, split_doc in enumerate(split_docs, start=1):
        chunk_text = split_doc.page_content
        if not chunk_text.strip():
            continue
        chunk_id = f"page_{page_number:03d}_chunk_{index:03d}"
        chunks.append(
            {
                "page_number": page_number,
                "chunk_id": chunk_id,
                "text": chunk_text,
            }
        )
    return chunks


def build_chunks(
    ocr_dir: Path | None = None,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> dict:
    """
    Convert all OCR pages into RAG-ready chunks (no embeddings / FAISS).

    Returns a result dict with chunks + statistics (DocuMind-style summary).
    """
    pages = load_ocr_pages(ocr_dir)
    size = chunk_size if chunk_size is not None else CHUNK_SIZE
    overlap = chunk_overlap if chunk_overlap is not None else CHUNK_OVERLAP

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=overlap,
    )

    all_chunks: list[dict] = []
    per_page_counts: dict[int, int] = {}
    skipped_empty: list[int] = []
    pages_processed = 0

    logger.info("OCR pages found: %s", len(pages))
    logger.info("Chunk size=%s, overlap=%s", size, overlap)

    for page in pages:
        page_number = page["page"]
        text = page["text"]
        if not text.strip():
            skipped_empty.append(page_number)
            per_page_counts[page_number] = 0
            logger.info(
                "Skipping page %s — empty OCR text.",
                page_number,
            )
            continue

        page_chunks = _chunk_page_text(text, page_number, splitter)
        pages_processed += 1
        per_page_counts[page_number] = len(page_chunks)
        all_chunks.extend(page_chunks)
        logger.info(
            "Page %s → %s chunk(s)",
            page_number,
            len(page_chunks),
        )

    stats = {
        "ocr_pages_found": len(pages),
        "pages_processed": pages_processed,
        "skipped_empty_pages": skipped_empty,
        "skipped_empty_count": len(skipped_empty),
        "chunks_per_page": {
            str(page): count for page, count in sorted(per_page_counts.items())
        },
        "total_chunks": len(all_chunks),
        "chunk_size": size,
        "chunk_overlap": overlap,
    }
    return {"chunks": all_chunks, "stats": stats}


def save_chunks(result: dict, output_path: Path | None = None) -> Path:
    """Persist chunks JSON under vectorstore/ (pre-FAISS staging)."""
    path = Path(output_path) if output_path else CHUNKS_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def ingest_ocr_chunks(
    ocr_dir: Path | None = None,
    output_path: Path | None = None,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> dict:
    """Build chunks from OCR and write them to disk. Returns stats (+ path)."""
    result = build_chunks(
        ocr_dir=ocr_dir,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    path = save_chunks(result, output_path=output_path)
    stats = dict(result["stats"])
    stats["chunks_path"] = str(path)
    return stats


def _print_summary(stats: dict) -> None:
    logger.info("")
    logger.info("=== Chunking summary ===")
    logger.info("OCR pages found:      %s", stats["ocr_pages_found"])
    logger.info("Pages processed:      %s", stats["pages_processed"])
    logger.info(
        "Skipped/empty pages:  %s (%s)",
        stats["skipped_empty_count"],
        stats["skipped_empty_pages"] or "none",
    )
    logger.info("Total chunks:         %s", stats["total_chunks"])
    logger.info("Saved to:             %s", stats.get("chunks_path", CHUNKS_PATH))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Chunk Balladesh OCR pages for RAG (no embeddings yet)."
    )
    parser.add_argument(
        "--ocr-dir",
        type=Path,
        default=OCR_OUTPUT_DIR,
        help=f"Directory of page_XXX.json files (default: {OCR_OUTPUT_DIR})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=CHUNKS_PATH,
        help=f"Output JSON path (default: {CHUNKS_PATH})",
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=CHUNK_SIZE,
        help=f"Chunk size in characters (default: {CHUNK_SIZE})",
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=CHUNK_OVERLAP,
        help=f"Chunk overlap in characters (default: {CHUNK_OVERLAP})",
    )
    args = parser.parse_args(argv)

    try:
        stats = ingest_ocr_chunks(
            ocr_dir=args.ocr_dir,
            output_path=args.output,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
        )
    except (FileNotFoundError, ValueError, OSError) as exc:
        logger.error("%s", exc)
        return 1

    _print_summary(stats)
    return 0


if __name__ == "__main__":
    sys.exit(main())
