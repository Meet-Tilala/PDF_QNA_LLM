# PDF_QNA_LLM

## PDF-QA: Question Answering System for PDFs

A Streamlit-based application that allows you to upload PDF documents and ask natural language questions about their content. Built using embedding-based retrieval (via ChromaDB) and OpenAI's LLMs.

---

## Features

-  Upload and process any PDF file or a directory
- Automatic text extraction, chunking, and vector embedding
- Semantic search with OpenAI models
- Accurate, traceable answers based on document content
- Persistent local vector store using ChromaDB

---

## Folder Structure

pdf-qa/
├── uploads/ ← User PDFs (ignored in Git)
├── lib/
│ ├── pdf_processor.py # End-to-end processing logic
│ ├── chunking.py # PDF text chunking logic
│ ├── vector_store.py # Embedding + vector DB logic (ChromaDB)
│ ├── query_engine.py # LANGCHAIN pipeline
├── main.py # Backend script (test CLI)
├── frontend.py # Streamlit app
├── config.py # Configuration variables
├── .env # API keys and secrets
├── .gitignore
├── requirements.txt
└── venv/ # Virtual environment (ignored)


---

##  Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/pdf-qa.git
cd pdf-qa
```

### 2. Set Up a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate     # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API Key
Create a .env file in the root directory:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Run the Streamlit App

```bash
streamlit run frontend.py
```

