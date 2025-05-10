import os
from dotenv import load_dotenv
from lib.pdf_processor import extract_text_from_pdf
from lib.chunking import intelligent_chunking
from lib.vector_store import add_chunks_to_vectorstore
from lib.query_engine import answer_query

load_dotenv()

def test_pipeline(file_path: str):
    file_name = os.path.basename(file_path)
    
    # Step 1: Extract text
    with open(file_path, "rb") as f:
        text = extract_text_from_pdf(f)
    
    # Step 2: Chunk
    doc_id = "doc1"
    chunks = intelligent_chunking(text, doc_id, file_name)

    # Step 3: Add to vectorstore
    add_chunks_to_vectorstore(chunks)

    # Step 4: Query
    while True:
        query = input("\nAsk a question (or type 'exit'): ")
        if query.lower() == 'exit':
            break
        response = answer_query(query)
        print("\nAnswer:")
        print(response["answer"])
        print("\nSources:")
        for source in response["sources"]:
            print(f"- {source['doc_name']}")

if __name__ == "__main__":
    test_pipeline("uploads/sample.pdf")  # Make sure a test PDF is in /uploads
