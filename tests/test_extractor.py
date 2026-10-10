from pathlib import Path

import fitz

from app.services.ingestion.extractor import extract_pdf_pages


def test_extract_pdf_pages(tmp_path):
    pdf_path = tmp_path / "sample.pdf"

    document = fitz.open()

    page1 = document.new_page()
    page1.insert_text((50, 50), "This is page one.")

    page2 = document.new_page()
    page2.insert_text((50, 50), "This is page two.")

    document.save(pdf_path)
    document.close()

    pages = extract_pdf_pages(Path(pdf_path))

    assert len(pages) == 2

    assert pages[0]["page_number"] == 1
    assert "This is page one." in pages[0]["text"]

    assert pages[1]["page_number"] == 2
    assert "This is page two." in pages[1]["text"]