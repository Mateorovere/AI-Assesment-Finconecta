"""
Semantic Search Application
===========================

This FastAPI application implements an AI-powered semantic search system. It provides two endpoints:

1. `/upload_document`: Accepts a document (with content and an optional title), generates its embedding via OpenAI's API,
   and stores it in ChromaDB.

2. `/search`: Accepts a query string, generates its embedding, and retrieves the most similar stored documents.

Usage:
------
1. Run the application with Uvicorn:

uvicorn main:app --reload

2. Access the interactive API docs at: http://127.0.0.1:8000/docs

"""

import os
import uuid
from typing import List
from fastapi import FastAPI, HTTPException
from openai import OpenAI
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
from models import DocumentResponse, DocumentUpload, QueryRequest, QueryResponse
load_dotenv()

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
 raise ValueError("The OPENAI_API_KEY environment variable is not set. Please set it before running the application.")
openai_client = OpenAI(api_key=openai_api_key)

# ------------------------------------------------------------------------------
# Initialize FastAPI Application
# ------------------------------------------------------------------------------

app = FastAPI(
 title="AI-powered Semantic Search API",
 description="Upload documents and search for similar ones using semantic embeddings.",
 version="1.0.0",
)

# ------------------------------------------------------------------------------
# Initialize ChromaDB Client and Collection
# ------------------------------------------------------------------------------

# Create a ChromaDB client with DuckDB for fast queries
client = chromadb.Client(
    settings=Settings(chroma_db_impl="duckdb", persist_directory="./chroma_db")
)


COLLECTION_NAME = "documents"

existing_collections = [col.name for col in client.list_collections()]
if COLLECTION_NAME in existing_collections:
 collection = client.get_collection(name=COLLECTION_NAME)
else:
 collection = client.create_collection(name=COLLECTION_NAME, embedding_function=None)


# ------------------------------------------------------------------------------
# Utility Function: Generate Embedding
# ------------------------------------------------------------------------------

def get_embedding(text: str) -> List[float]:
 """
 Generate an embedding for the provided text using OpenAI's API.

 Args:
     text (str): The text for which to generate the embedding.

 Returns:
     List[float]: The embedding vector.

 Raises:
     HTTPException: If the OpenAI API call fails.
 """
 try:
     text = text.replace("\n", " ")
     embedding = openai_client.embeddings.create(input=[text], model="text-embedding-3-small").data[0].embedding
     return embedding
 except Exception as e:
     raise HTTPException(status_code=500, detail=f"Error generating embedding: {str(e)}")


# ------------------------------------------------------------------------------
# API Endpoints
# ------------------------------------------------------------------------------

@app.post("/upload_document", response_model=DocumentResponse, summary="Upload a Document")
def upload_document(doc: DocumentUpload):
 """
 Upload a document to the semantic search system.

 This endpoint accepts a document's content and optional title, generates an embedding
 using OpenAI, and stores the document (with its metadata) in ChromaDB.

 Args:
     doc (DocumentUpload): The document data containing the content and an optional title.

 Returns:
     DocumentResponse: The stored document details, including a unique ID.
 """
 
 doc_id = str(uuid.uuid4())

 embedding = get_embedding(doc.content)

 metadata = {"title": doc.title, "content": doc.content}

 # Store the document in the ChromaDB collection.
 try:
     collection.add(
         ids=[doc_id],
         embeddings=[embedding],
         metadatas=[metadata]
     )
 except Exception as e:
     raise HTTPException(status_code=500, detail=f"Error storing document: {str(e)}")

 return DocumentResponse(id=doc_id, content=doc.content, title=doc.title)


@app.post("/search", response_model=QueryResponse, summary="Search for Similar Documents")
def search_documents(query_request: QueryRequest):
 """
 Search for documents that are semantically similar to the provided query.

 The endpoint generates an embedding for the query and performs a vector search in ChromaDB,
 returning the top-N most similar documents.

 Args:
     query_request (QueryRequest): The search query and the number of results desired.

 Returns:
     QueryResponse: A list of documents that are similar to the query.
 """
 
 query_embedding = get_embedding(query_request.query)

 # Query the ChromaDB collection for similar documents.
 try:
     results = collection.query(
         query_embeddings=[query_embedding],
         n_results=query_request.n_results,
         include=["metadatas"]
     )
 except Exception as e:
     raise HTTPException(status_code=500, detail=f"Error querying documents: {str(e)}")

 documents = []
 for doc_id, metadata in zip(results["ids"][0], results["metadatas"][0]):
     document = DocumentResponse(
         id=doc_id,
         content=metadata.get("content", ""),
         title=metadata.get("title")
     )
     documents.append(document)

 return QueryResponse(results=documents)


if __name__ == "__main__":
 import uvicorn

 uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)