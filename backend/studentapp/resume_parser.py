"""
Extracts plain text from an uploaded resume file (PDF or DOCX).
"""
import io
from pypdf import PdfReader
from docx import Document


class UnsupportedFileType(Exception):
    pass


def extract_text_from_file(django_file) -> str:
    """django_file: an InMemoryUploadedFile or TemporaryUploadedFile from request.FILES"""
    name = django_file.name.lower()
    django_file.seek(0)
    raw_bytes = django_file.read()
    django_file.seek(0)

    if name.endswith(".pdf"):
        return _extract_pdf(raw_bytes)
    elif name.endswith(".docx"):
        return _extract_docx(raw_bytes)
    else:
        raise UnsupportedFileType("Only .pdf and .docx files are supported")


def _extract_pdf(raw_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(raw_bytes))
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        text_parts.append(page_text)
    return "\n".join(text_parts).strip()


def _extract_docx(raw_bytes: bytes) -> str:
    doc = Document(io.BytesIO(raw_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs).strip()
