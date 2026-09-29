import os
from pypdf import PdfReader

DEFAULT_PDF_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "resume.pdf")


def extract_resume_text(pdf_path: str = DEFAULT_PDF_PATH) -> str:
    """Reads a local PDF file and extracts all text content."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(
            f"Resume PDF not found at {pdf_path}. Please place your 'resume.pdf' in the 'data/' directory."
        )

    reader = PdfReader(pdf_path)
    extracted_chunks = []

    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            extracted_chunks.append(text)

    full_text = "\n".join(extracted_chunks).strip()
    return full_text


def get_resume_keywords(text: str) -> list[str]:
    """Basic keyword parser to cross-reference skills against job requirements."""
    common_skills = [
        "python", "java", "c++", "javascript", "react", "node", "sql", "git",
        "product management", "machine learning", "ai", "gis", "data analysis"
    ]
    text_lower = text.lower()
    return [skill for skill in common_skills if skill in text_lower]