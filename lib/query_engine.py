from typing import List, Dict
import openai
from lib.vector_store import query_vectorstore
import os

# Set your OpenAI key via .env or elsewhere before using this
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_answer(query: str, relevant_chunks: List[Dict]) -> Dict:
    """
    Generate answer using LLM based on retrieved document chunks
    """
    if not relevant_chunks:
        return {
            "answer": "I couldn't find any relevant information in the uploaded documents.",
            "sources": []
        }

    # Build the context from retrieved chunks
    context = "\n\n".join([f"[From: {chunk['doc_name']}]\n{chunk['text']}" for chunk in relevant_chunks])

                                                                                           # here is also a usp for the project
    prompt = f""" 
You are an AI assistant that answers questions based on the provided document snippets.
    Please answer the following question using ONLY the information in the document snippets below.
    If you cannot find the answer in the provided snippets, say "I couldn't find the answer in the provided documents." 
    Always cite the document sources in your answer.

Document snippets:
{context}

Question: {query}
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that only uses provided context."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=800
    )

    answer_text = response['choices'][0]['message']['content']

    # Include sources used in answer
    sources = list({(chunk['doc_id'], chunk['doc_name']) for chunk in relevant_chunks})

    return {
        "answer": answer_text,
        "sources": [{"doc_id": doc_id, "doc_name": doc_name} for doc_id, doc_name in sources]
    }


def answer_query(query: str, top_k: int = 5, doc_filter: List[str] = None) -> Dict:
    """
    Handle a full query-response pipeline
    """
    chunks = query_vectorstore(query, top_k=top_k, doc_filter=doc_filter)
    return generate_answer(query, chunks)
