"""
Resume parser — handles PDF uploads and raw text.
Uses PyMuPDF (fitz) as primary extractor with pdfplumber fallback.
"""

import re
import os


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract clean text from a PDF file."""
    text = ""

    # Try PyMuPDF first (fastest)
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(pdf_path)
        pages = []
        for page in doc:
            pages.append(page.get_text("text"))
        doc.close()
        text = "\n".join(pages)
        if text.strip():
            return clean_text(text)
    except ImportError:
        pass
    except Exception:
        pass

    # Fallback: pdfplumber
    try:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            pages = []
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    pages.append(extracted)
            text = "\n".join(pages)
            if text.strip():
                return clean_text(text)
    except ImportError:
        pass
    except Exception:
        pass

    # Last resort: pypdf
    try:
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        pages = []
        for page in reader.pages:
            pages.append(page.extract_text() or "")
        text = "\n".join(pages)
        return clean_text(text)
    except Exception as e:
        return f"[Could not extract PDF text: {e}. Please paste your resume text instead.]"


def clean_text(text: str) -> str:
    """Normalise extracted PDF text."""
    # Remove excessive whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    # Remove non-printable characters
    text = re.sub(r"[^\x20-\x7E\n]", " ", text)
    return text.strip()


def parse_resume_text(text: str) -> dict:
    """
    Extract structured info from resume text.
    Returns a dict with name, contact, skills, experience sections.
    This is a heuristic parser — the LLM does the heavy lifting.
    """
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    result = {
        "raw_text": text,
        "likely_name": "",
        "sections": {},
    }

    # Try to guess name (usually first non-empty line)
    if lines:
        result["likely_name"] = lines[0]

    # Section detection heuristics
    section_headers = {
        "experience": r"(work\s*experience|professional\s*experience|employment|experience)",
        "education": r"education|academic|qualification",
        "skills": r"skills|technologies|tech\s*stack|competencies",
        "projects": r"projects|portfolio|work\s*samples",
        "summary": r"summary|objective|profile|about",
        "certifications": r"certif|awards|achievements",
    }

    current_section = "general"
    sections = {"general": []}

    for line in lines:
        matched = False
        for section, pattern in section_headers.items():
            if re.search(pattern, line, re.IGNORECASE) and len(line) < 60:
                current_section = section
                if section not in sections:
                    sections[section] = []
                matched = True
                break
        if not matched:
            sections.setdefault(current_section, []).append(line)

    result["sections"] = {k: "\n".join(v) for k, v in sections.items() if v}
    return result
