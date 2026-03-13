"""
file_handler.py
---------------
Handles all file upload and text extraction logic.

Supports:
  - PDF files  (via pdfplumber)
  - DOCX files (via python-docx)
  - TXT files  (plain read)

Usage:
  from file_handler import extract_text_from_file
  text = extract_text_from_file(uploaded_file)
"""

import io
import pdfplumber
from docx import Document


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract all text from a PDF file.

    Args:
        file_bytes: Raw bytes of the uploaded PDF.

    Returns:
        A single string containing all extracted text, pages joined by newlines.
    """
    text_pages = []

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:                       # some pages may be image-only
                text_pages.append(page_text)

    return "\n\n".join(text_pages)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    Extract all text from a DOCX (Word) file.

    Args:
        file_bytes: Raw bytes of the uploaded DOCX.

    Returns:
        A single string with each paragraph separated by a newline.
    """
    doc = Document(io.BytesIO(file_bytes))
    paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
    return "\n".join(paragraphs)


def extract_text_from_txt(file_bytes: bytes) -> str:
    """
    Decode a plain-text file.

    Args:
        file_bytes: Raw bytes of the uploaded TXT file.

    Returns:
        Decoded string (UTF-8 with fallback to latin-1).
    """
    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        return file_bytes.decode("latin-1")


def extract_text_from_file(uploaded_file) -> str:
    """
    Dispatch to the correct extractor based on file extension.

    Args:
        uploaded_file: Streamlit UploadedFile object.

    Returns:
        Extracted plain text string.

    Raises:
        ValueError: If the file type is not supported.
    """
    file_bytes = uploaded_file.read()
    filename   = uploaded_file.name.lower()

    if filename.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif filename.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    elif filename.endswith(".txt"):
        return extract_text_from_txt(file_bytes)
    else:
        raise ValueError(
            f"Unsupported file type: '{uploaded_file.name}'. "
            "Please upload a PDF, DOCX, or TXT file."
        )
