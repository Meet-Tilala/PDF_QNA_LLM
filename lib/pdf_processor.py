from PyPDF2 import PdfReader
import os

def extract_text_from_pdf(file_path):
    text = ""
    reader = PdfReader(file_path)
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_texts_from_directory(directory_path):
    """
    Reads all PDFs in a directory and returns a dict {filename: extracted_text}
    """
    texts = {}
    for filename in os.listdir(directory_path):
        if filename.lower().endswith(".pdf"):
            path = os.path.join(directory_path, filename)
            texts[filename] = extract_text_from_pdf(path)
    return texts
