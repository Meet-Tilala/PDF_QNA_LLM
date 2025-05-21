# PDF_QNA_LLM

## PDF-QA: Question Answering System for PDFs

A Streamlit-based application that allows you to upload PDF documents and ask natural language questions about their content. Built using embedding-based retrieval (via ChromaDB) and OpenAI's LLMs. For a working demo of this project, check out <a href="https://github.com/Meet-Tilala/PDF_QNA_LLM/blob/main/Demo%20Video.mp4">Demo Video</a>

Powered by a combination of:

- **Text extraction** and **chunking** from PDFs
- **Semantic embedding** using `sentence-transformers`
- **Vector-based retrieval** with ChromaDB
- **Natural language responses** using OpenAI's GPT models

All through a **Streamlit** interface designed for ease of use.
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


##  Contact

Made by Meet Tilala.

For questions, suggestions, or collaboration:
- GitHub: [@thatswhatmeetcoded](https://github.com/thatswhatmeetcoded)
- Email: meettilala2005@gmail.com

Feel free to open an issue or submit a PR if you’d like to contribute!

---

##  Acknowledgements

- [Streamlit](https://streamlit.io/) – for rapid UI development
- [ChromaDB](https://www.trychroma.com/) – for fast vector search
- [SentenceTransformers](https://www.sbert.net/) – for semantic embeddings
- [OpenAI](https://platform.openai.com/) – for powerful LLMs
