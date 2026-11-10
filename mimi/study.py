from pypdf import PdfReader

def extract_pdf_text(file_path: str) -> str:
    reader = PdfReader(file_path)
    pages = []
    for page in reader.pages:
        pages.append(page.extract_text() or "")
    text = "\n".join(pages).strip()
    if not text:
        raise ValueError(
            "No selectable text was found. This may be a scanned PDF; "
            "OCR can be added in a later version."
        )
    return text[:50000]
