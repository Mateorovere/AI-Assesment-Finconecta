import numpy as np
import faiss
import tiktoken
from openai import OpenAI

#######################################
# 1. Tokenization and Chunking Function
#######################################
def tokenize_text(text: str, max_tokens: int = 512) -> list[str]:
    """
    Tokenizes the given text and splits it into chunks not exceeding max_tokens.
    """
    # Get the tokenizer encoding
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)
    
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        # Slice tokens and decode back into text
        chunk_tokens = tokens[i:i + max_tokens]
        chunk_text = tokenizer.decode(chunk_tokens)
        chunks.append(chunk_text)
        
    #[TODO] ADD SLIDING WINDOW TO CAPTURE BETTER UNDERSTANDING OF THE WHOLE TEXT
    return chunks

##################################
# 2. Embedding Generation Function
##################################
def get_embedding(text: str, client: OpenAI, EMBEDDING_MODEL: str) -> list[float] | None:
    """
    Generates an embedding for the given text using OpenAI's text-embedding-ada-002.
    Returns a 1536-dimensional vector.
    """
    if not text or not isinstance(text, str):
        return None
    try:
        response = client.embeddings.create(input=[text], model=EMBEDDING_MODEL)
        embedding = response.data[0].embedding
        return embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

###############################################
# 3. Building a Faiss Index for Retrieval
###############################################
def build_index(chunks: list[str], client: OpenAI, EMBEDDING_MODEL: str) -> tuple[faiss.IndexFlatIP, list[str]]:
    """
    For each text chunk, generates its embedding and builds a Faiss index using inner product (cosine similarity).
    Returns the Faiss index and a list of valid chunks corresponding to the embeddings.
    """
    embeddings = []
    valid_chunks = []
    for chunk in chunks:
        emb = get_embedding(chunk, client, EMBEDDING_MODEL)
        if emb is not None:
            embeddings.append(emb)
            valid_chunks.append(chunk)
    if not embeddings:
        raise ValueError("No embeddings generated; check your input texts and API key.")
    embedding_matrix = np.array(embeddings).astype('float32')
    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(embedding_matrix)
    # Create a Faiss index 
    index = faiss.IndexFlatIP(embedding_matrix.shape[1])
    index.add(embedding_matrix)
    return index, valid_chunks

#######################
# 4. Retrieval Function
#######################
def retrieve_chunks(client: OpenAI, EMBEDDING_MODEL: str, query: str, index: faiss.IndexFlatIP, chunks: list[str], top_k: int = 5) -> list[str]:
    """
    Embeds the query, normalizes it, and searches the Faiss index for the top_k most similar chunks.
    Returns a list of the retrieved text chunks.
    """
    query_embedding = get_embedding(query, client, EMBEDDING_MODEL)
    if query_embedding is None:
        return []
    query_vector = np.array(query_embedding).astype('float32').reshape(1, -1)
    faiss.normalize_L2(query_vector)
    distances, indices = index.search(query_vector, top_k)
    retrieved = [chunks[i] for i in indices[0] if i < len(chunks)]
    return retrieved

################
# 5. Generation
################
def generate_answer(query: str, context_chunks: list[str], client: OpenAI, CHAT_MODEL: str) -> str:
    """
    Constructs a prompt by combining the retrieved context with the user query,
    then calls the ChatCompletion API (e.g., GPT-3.5-turbo) to generate an answer.
    """
    context = "\n\n".join(context_chunks)
    prompt = (
        "You are an expert on Argentina's history, culture, and economy. "
        "Based solely on the context provided below, answer the user's query succinctly and accurately. "
        "If the context does not contain enough information, indicate any gaps in the data.\n\n"
        f"Context:\n{context}\n\n"
        f"User Query: {query}\n\n"
        "Answer:"
    )

    try:
        response = client.chat.completions.create(
            model=CHAT_MODEL,
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are a knowledgeable assistant with deep expertise in all things related to Argentina. "
                        "Ensure that your answers are directly supported by the context provided, and refrain from including "
                        "information not present in the context."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=300
        )
        answer = response.choices[0].message.content
        return answer
    except Exception as e:
        print(f"Error generating answer: {e}")
        return "Sorry, I encountered an error generating an answer."