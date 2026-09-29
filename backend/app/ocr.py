"""OCR helpers for scanned Bengali PDFs (Tesseract + pdf2image)."""

from __future__ import annotations

import argparse
import json
import logging
import re
import shutil
import sys
from pathlib import Path

import pytesseract
from pdf2image import convert_from_path
from pdf2image.exceptions import PDFInfoNotInstalledError, PDFPageCountError
from pytesseract import TesseractError, TesseractNotFoundError

from .config import OCR_DPI, OCR_OUTPUT_DIR, PDF_PATH, TESSERACT_LANG

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger(__name__)


def clean_text(text: str) -> str:
    """Light cleanup: collapse whitespace and blank lines; keep Bangla intact."""
    if not text:
        return ""

    # Normalize Windows/Mac newlines
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Strip trailing spaces on each line
    lines = [line.rstrip() for line in text.split("\n")]
    # Collapse runs of spaces/tabs inside a line (keep single spaces)
    lines = [re.sub(r"[ \t]+", " ", line) for line in lines]
    # Drop leading/trailing empty lines and collapse 3+ blank lines to 1
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def page_json_path(page: int, output_dir: Path | None = None) -> Path:
    out = output_dir or OCR_OUTPUT_DIR
    return out / f"page_{page:03d}.json"


def check_pdf_exists(pdf_path: Path) -> None:
    if not pdf_path.is_file():
        raise FileNotFoundError(
            f"PDF not found: {pdf_path}\n"
            f"Place Balladesh.pdf at data/Balladesh.pdf and try again."
        )


def check_tesseract(lang: str) -> None:
    if shutil.which("tesseract") is None:
        raise RuntimeError(
            "Tesseract is not installed or not on PATH.\n"
            "On Ubuntu: sudo apt-get install -y tesseract-ocr tesseract-ocr-ben"
        )

    try:
        available = set(pytesseract.get_languages(config=""))
    except TesseractNotFoundError as exc:
        raise RuntimeError(
            "Tesseract is not installed or not on PATH.\n"
            "On Ubuntu: sudo apt-get install -y tesseract-ocr tesseract-ocr-ben"
        ) from exc

    needed = [part for part in lang.split("+") if part]
    missing = [code for code in needed if code not in available]
    if missing:
        pkgs = " ".join(
            f"tesseract-ocr-{code}" if code != "eng" else "tesseract-ocr"
            for code in missing
        )
        raise RuntimeError(
            f"Tesseract language data missing: {', '.join(missing)}\n"
            f"Installed languages: {', '.join(sorted(available)) or '(none)'}\n"
            f"On Ubuntu: sudo apt-get install -y {pkgs}"
        )


def check_poppler() -> None:
    if shutil.which("pdftoppm") is None or shutil.which("pdfinfo") is None:
        raise RuntimeError(
            "PDF rendering tools (poppler-utils) are missing.\n"
            "On Ubuntu: sudo apt-get install -y poppler-utils"
        )


def save_page_json(page: int, text: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = page_json_path(page, output_dir)
    payload = {"page": page, "text": text}
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def ocr_image(image, lang: str) -> str:
    try:
        raw = pytesseract.image_to_string(image, lang=lang)
    except TesseractNotFoundError as exc:
        raise RuntimeError(
            "Tesseract is not installed or not on PATH.\n"
            "On Ubuntu: sudo apt-get install -y tesseract-ocr tesseract-ocr-ben"
        ) from exc
    except TesseractError as exc:
        raise RuntimeError(
            f"Tesseract failed while reading text (lang={lang}): {exc}"
        ) from exc
    return clean_text(raw)


def process_pages(
    pdf_path: Path | None = None,
    start_page: int = 1,
    end_page: int = 5,
    output_dir: Path | None = None,
    lang: str | None = None,
    dpi: int | None = None,
) -> list[Path]:
    """
    OCR pages [start_page, end_page] (1-based, inclusive).

    Skips pages that already have a JSON file under ocr_output/.
    """
    pdf_path = Path(pdf_path) if pdf_path else PDF_PATH
    output_dir = Path(output_dir) if output_dir else OCR_OUTPUT_DIR
    lang = lang or TESSERACT_LANG
    dpi = dpi or OCR_DPI

    if start_page < 1 or end_page < start_page:
        raise ValueError(
            f"Invalid page range: start_page={start_page}, end_page={end_page}"
        )

    check_pdf_exists(pdf_path)
    check_poppler()
    check_tesseract(lang)

    output_dir.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []
    total = end_page - start_page + 1

    for page in range(start_page, end_page + 1):
        out_path = page_json_path(page, output_dir)
        relative = page - start_page + 1

        if out_path.is_file():
            logger.info(
                "Skipping page %s — cached OCR found.",
                page,
            )
            saved.append(out_path)
            continue

        logger.info("Processing page %s/%s...", relative, total)

        try:
            images = convert_from_path(
                str(pdf_path),
                dpi=dpi,
                first_page=page,
                last_page=page,
            )
        except PDFInfoNotInstalledError as exc:
            raise RuntimeError(
                "PDF rendering tools (poppler-utils) are missing.\n"
                "On Ubuntu: sudo apt-get install -y poppler-utils"
            ) from exc
        except PDFPageCountError as exc:
            raise RuntimeError(
                f"Could not read PDF page count from {pdf_path}: {exc}"
            ) from exc
        except Exception as exc:  # noqa: BLE001 — surface render failures clearly
            raise RuntimeError(
                f"Failed to render PDF page {page} from {pdf_path}: {exc}"
            ) from exc

        if not images:
            raise RuntimeError(
                f"No image rendered for page {page}. "
                "Check that the page exists in the PDF."
            )

        text = ocr_image(images[0], lang=lang)
        path = save_page_json(page, text, output_dir)
        logger.info("Saved %s", path.name)
        saved.append(path)

    return saved


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="OCR Balladesh PDF pages with Tesseract (Bengali)."
    )
    parser.add_argument(
        "--pdf",
        type=Path,
        default=PDF_PATH,
        help=f"Path to PDF (default: {PDF_PATH})",
    )
    parser.add_argument(
        "--start",
        type=int,
        default=1,
        help="First page (1-based, inclusive)",
    )
    parser.add_argument(
        "--end",
        type=int,
        default=5,
        help="Last page (1-based, inclusive)",
    )
    parser.add_argument(
        "--lang",
        default=TESSERACT_LANG,
        help=f"Tesseract language(s), e.g. ben or ben+eng (default: {TESSERACT_LANG})",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=OCR_DPI,
        help=f"Render DPI (default: {OCR_DPI})",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OCR_OUTPUT_DIR,
        help=f"Directory for page_XXX.json files (default: {OCR_OUTPUT_DIR})",
    )
    args = parser.parse_args(argv)

    try:
        paths = process_pages(
            pdf_path=args.pdf,
            start_page=args.start,
            end_page=args.end,
            output_dir=args.output_dir,
            lang=args.lang,
            dpi=args.dpi,
        )
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        logger.error("%s", exc)
        return 1

    logger.info("Done. %s page file(s) ready under %s", len(paths), args.output_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
