from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional

# Create Chroma client with new API (persistent to disk)
chroma_client = PersistentClient(path="./chroma_db")


collection = chroma_client.get_or_create_collection(name="pdf_chunks")

# Load embedding model once
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast, 384-dim

def add_chunks_to_vectorstore(chunks: List[Dict]):
    """Embed and store chunks in ChromaDB"""
    texts = [chunk["text"] for chunk in chunks]
    ids = [chunk["id"] for chunk in chunks]
    metadatas = [{"doc_id": chunk["doc_id"], "doc_name": chunk["doc_name"], "chunk_index": chunk["chunk_index"]} for chunk in chunks]
    
    embeddings = embedding_model.encode(texts).tolist()

    collection.add(
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )

def query_vectorstore(query: str, top_k: int = 5, doc_filter: Optional[List[str]] = None) -> List[Dict]:
    """Query ChromaDB for relevant chunks"""
    results = collection.query(
        query_texts=[query],
        n_results=top_k * 3 if doc_filter else top_k,
        where={"doc_id": {"$in": doc_filter}} if doc_filter else None
    )
    
    # Format results
    chunks = []
    for i in range(len(results["documents"][0])):
        chunks.append({
            "id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "doc_id": results["metadatas"][0][i]["doc_id"],
            "doc_name": results["metadatas"][0][i]["doc_name"],
            "chunk_index": results["metadatas"][0][i]["chunk_index"]
        })
        if len(chunks) >= top_k:
            break

    return chunks
