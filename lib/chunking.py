import re
from typing import List, Dict

CHUNK_SIZE = 1000                                                     # characters (tweak based on LLM context limit)
CHUNK_OVERLAP = 200                                                   # characters of overlap for context retention

def intelligent_chunking(text: str, doc_id: str, doc_name: str) -> List[Dict]:
    """
    Split text into chunks using multiple strategies:
    1. Paragraph-based chunking when possible
    2. Fallback to fixed-size chunking with overlap
    """
    chunks = []

    # Strategy 1: Paragraph-based chunking
    paragraphs = re.split(r'\n\s*\n', text)
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If adding this paragraph exceeds chunk size
        if len(current_chunk) + len(para) > CHUNK_SIZE:
            if current_chunk:
                chunk_id = f"{doc_id}_{len(chunks)}"
                chunks.append({
                    'id': chunk_id,
                    'text': current_chunk.strip(),
                    'doc_id': doc_id,
                    'doc_name': doc_name,
                    'chunk_index': len(chunks)
                })

                # Add overlap
                last_words = " ".join(current_chunk.split()[-20:]) if len(current_chunk.split()) > 20 else ""
                current_chunk = last_words + " " + para
            else:
                current_chunk = para
        else:
            current_chunk += " " + para if current_chunk else para

    # Add the final chunk
    if current_chunk:
        chunk_id = f"{doc_id}_{len(chunks)}"
        chunks.append({
            'id': chunk_id,
            'text': current_chunk.strip(),
            'doc_id': doc_id,
            'doc_name': doc_name,
            'chunk_index': len(chunks)
        })

    # Strategy 2: Fallback to fixed-size chunking if paragraph-based failed
    if len(chunks) <= 1 and len(text) > CHUNK_SIZE:
        chunks = []
        for i in range(0, len(text), CHUNK_SIZE - CHUNK_OVERLAP):
            chunk_text = text[i:i + CHUNK_SIZE]
            if chunk_text.strip():
                chunk_id = f"{doc_id}_{len(chunks)}"
                chunks.append({
                    'id': chunk_id,
                    'text': chunk_text.strip(),
                    'doc_id': doc_id,
                    'doc_name': doc_name,
                    'chunk_index': len(chunks)
                })

    return chunks
