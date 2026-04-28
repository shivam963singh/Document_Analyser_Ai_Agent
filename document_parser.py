import os
import pandas as pd
from pypdf import PdfReader
import docx
import nbformat

def extract_text(file_path: str) -> str:
    """Extracts text from a given file based on its extension."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext == ".pdf":
        return _parse_pdf(file_path)
    elif ext == ".docx":
        return _parse_docx(file_path)
    elif ext == ".xlsx" or ext == ".xls":
        return _parse_excel(file_path)
    elif ext == ".ipynb":
        return _parse_notebook(file_path)
    elif ext in [".txt", ".md", ".csv", ".py", ".json"]:
        # Fallback for simple text files
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        raise ValueError(f"Unsupported file format: {ext}")

def _parse_pdf(file_path: str) -> str:
    text = ""
    try:
        reader = PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        print(f"Error parsing PDF: {e}")
    return text

def _parse_docx(file_path: str) -> str:
    text = ""
    try:
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error parsing DOCX: {e}")
    return text

def _parse_excel(file_path: str) -> str:
    text = ""
    try:
        # Read all sheets into a dictionary of DataFrames
        excel_data = pd.read_excel(file_path, sheet_name=None)
        for sheet_name, df in excel_data.items():
            text += f"--- Sheet: {sheet_name} ---\n"
            text += df.to_string(index=False) + "\n\n"
    except Exception as e:
        print(f"Error parsing Excel: {e}")
    return text

def _parse_notebook(file_path: str) -> str:
    text = ""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            nb = nbformat.read(f, as_version=4)
        for cell in nb.cells:
            if cell.cell_type == "markdown":
                text += f"[Markdown Cell]\n{cell.source}\n\n"
            elif cell.cell_type == "code":
                text += f"[Code Cell]\n{cell.source}\n\n"
    except Exception as e:
        print(f"Error parsing Notebook: {e}")
    return text
