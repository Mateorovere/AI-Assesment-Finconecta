# AI Engineer Assessment – FinConecta

This repository contains a **rapid prototype** demonstrating:
1. An **AI-powered Semantic Search** application using OpenAI embeddings and a vector database.
2. A **Retrieval-Augmented Generation (RAG)** pipeline for question answering.
3. A **Web Scraper** that collects product data from an e-commerce site (Mercado Libre).

The code showcases:
- How to generate embeddings and store/query them using ChromaDB (and a FAISS example).
- How to build a Q&A system with retrieval-augmented generation in Python.
- How to scrape product data (name, price, description) from Mercado Libre using `requests` + `BeautifulSoup`.


---

## Setup & Installation

1. **Clone or download** this repository.

2. **Create and activate** a Python virtual environment (recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # or venv\Scripts\activate on Windows
    ```

3. **Install dependencies** for each section:
   - **RAG Pipeline**:
     ```bash
     cd rag_pipeline
     pip install -r requirements.txt
     ```
   - **Semantic Search**:
     ```bash
     cd semantic_search
     pip install -r requirements.txt
     ```
   - **Web Scraper**:
     ```bash
     cd web_scraper
     pip install -r requirements.txt
     ```

4. **Set up environment variables**:
   - Copy each `.env.sample` into a `.env` file (in `rag_pipeline/` and `semantic_search/`) and add your [OpenAI API key](https://platform.openai.com/account/api-keys):
     ```
     OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>
     ```
   - Make sure the `.env` file is placed in the same directory where the scripts will run so the code can pick up these variables using `python-dotenv`.

---

## Semantic Search (FastAPI) Usage

Inside the `semantic_search/` folder:

1. **Install dependencies** (if not done yet):
   ```bash
   uvicorn main:app --reload
   ```

Check the interactive API docs:

Navigate to: http://127.0.0.1:8000/docs

---

## RAG Pipeline Usage

**Inside the `rag_pipeline/` folder**:

1. **Install dependencies** (if not done yet):
   ```bash
   pip install -r requirements.txt
   python rag_pipeline.py
   ```

---

## Web Scraper Usage

**Inside the `web_scraper/` folder**:

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   python mercado_scraper.py
   ```

Scheduling:
You can schedule mercado_scraper.py to run periodically using Cron jobs or on a serverless platform like AWS Lambda.
Example Cron job entry (once a day at midnight):

```bash
0 0 * * * /path/to/venv/bin/python /path/to/web_scraper/mercado_scraper.py
```

