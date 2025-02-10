from openai import OpenAI
import os
from dotenv import load_dotenv
from functions import tokenize_text, build_index, retrieve_chunks, generate_answer

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
 raise ValueError("The OPENAI_API_KEY environment variable is not set. Please set it before running the application.")
client = OpenAI(api_key=openai_api_key)

EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-3.5-turbo"

def main():
    # Example documents
    documents = [
        "Argentina is a country in South America, bordered by the Andes mountains to the west and the Atlantic Ocean to the east. Its capital is Buenos Aires.",
        "The tango, a passionate dance and music genre, originated in the working-class neighborhoods of Buenos Aires and Montevideo in the late 19th century.",
        "Argentina's economy is heavily reliant on agriculture, with exports including soybeans, beef, and wine, particularly from the Mendoza region.",
        "The May Revolution of 1810 marked the beginning of Argentina's independence movement from Spanish rule, culminating in formal independence in 1816.",
        "Patagonia, a region spanning southern Argentina and Chile, is known for its dramatic landscapes, glaciers, and wildlife like penguins and guanacos.",
        "The Argentine peso is the national currency, though the country has faced recurring economic crises and high inflation rates in recent decades.",
        "Asado, a traditional Argentine barbecue, is a central part of the country's culinary culture, often featuring cuts of beef cooked over an open flame.",
        "Lionel Messi, widely regarded as one of the greatest footballers of all time, was born in Rosario, Argentina, and played for the national team for over 15 years.",
        "The Perito Moreno Glacier in Los Glaciares National Park is one of the few glaciers in the world that is still advancing.",
        "The Falklands War in 1982 was a brief but intense conflict between Argentina and the United Kingdom over the disputed Falkland Islands (Islas Malvinas)."
    ]
    
    all_text = "\n\n".join(documents)
    
    # Tokenize and chunk the text
    chunks = tokenize_text(all_text, max_tokens=150)
    print("Text Chunks:")
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i+1}: {chunk[:100]}...")
    
    # Build the vector index using Faiss
    index, valid_chunks = build_index(chunks, client, EMBEDDING_MODEL)
    print(f"\nBuilt Faiss index with {len(valid_chunks)} chunks.")
    
    user_query = "What are the main cultural, historical, and economic aspects of Argentina?"
    print(f"\nUser Query: {user_query}")
    
    # Retrieve the most relevant chunks
    retrieved_chunks = retrieve_chunks(client, EMBEDDING_MODEL, user_query, index, valid_chunks, top_k=3)
    print("\nRetrieved Context Chunks:")
    for chunk in retrieved_chunks:
        print(f"- {chunk}")
    
    # Generate the final answer using the retrieved context
    final_answer = generate_answer(user_query, retrieved_chunks, client, CHAT_MODEL)
    print("\nFinal Answer:")
    print(final_answer)

if __name__ == "__main__":
    main()
