from pathlib import Path

import fitz


def extract_pdf_pages(pdf_path: Path) -> list[dict]:
    pages = []

    with fitz.open(pdf_path) as document:
        for page_number, page in enumerate(document, start=1):
            text = page.get_text("text")

            pages.append(
                {
                    "page_number": page_number,
                    "text": text,
                }
            )

    return pages