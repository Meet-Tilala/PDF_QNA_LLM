import streamlit as st
from lib.query_engine import answer_query
import os
from lib.pdf_processor import extract_text_from_pdf, extract_texts_from_directory

st.set_page_config(page_title="PDF Q&A System", layout="wide")
st.title("📄 Ask Questions About Your PDF")

# Upload PDF
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

# Make sure upload folder exists
os.makedirs("uploads", exist_ok=True)

if uploaded_file:
    file_path = os.path.join("uploads", uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success(f"Uploaded `{uploaded_file.name}` successfully!")

    with st.spinner("🔍 Processing PDF..."):
        try:
            extract_text_from_pdf(file_path)  # This should embed and store chunks
            st.session_state["doc_name"] = uploaded_file.name
            st.session_state["ready"] = True
            st.success("PDF processed and stored in vector database.")
        except Exception as e:
            st.error(f"Processing failed: {e}")
            st.stop()

# Ask a question
if st.session_state.get("ready", False):
    question = st.text_input("Ask a question:")

    if st.button("Get Answer") and question.strip():
        with st.spinner("💬 Thinking..."):
            try:
                response = answer_query(question)
                st.markdown(f"**Answer:** {response}")
            except Exception as e:
                st.error(f"Error getting answer: {e}")
