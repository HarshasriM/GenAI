from dotenv import load_dotenv
from google import genai
from google.genai import types
import chromadb

import os

load_dotenv()


# Path for storing the database persistently
storage_path = "./chroma_db"  # Ensure this directory exists or is created

# Ensure the directory exists
os.makedirs(storage_path, exist_ok=True)

# Initialize ChromaDB client in persistent mode with specified directory
chroma_client = chromadb.PersistentClient(path=storage_path)

print("chromadb client created")


GEMINI_API_KEY = os.getenv("API_KEY")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)

def create_embeddings(documents: list):
    """
    Create embeddings for a list of documents using Gemini's text embedding model.

    Args:
    documents (list): A list of strings for which to create embeddings.

    Returns:
    list: A list of embeddings, where each embedding corresponds to a document in the input list.
    """
    embedding_data = gemini_client.models.embed_content(
        model="text-embedding-004",
        contents=documents,
    )

    # print(embedding_data.embeddings[0].values)
    # Extract the embeddings from the response
    # embeddings = [i for i in embedding_data.embeddings]
    # temp= embedding_data.embeddings[0].values
    # print(type(temp[1]))

    return embedding_data.embeddings[0].values

# Documents to be embedded
documents = [
    "This is a document about apples",
    "This is a document about bananas",
    "This is a document about oranges",
    "This is a document about grapes",
    "This is a document about pineapples"
]

# Corresponding IDs for the documents
ids = ["id4", "id5", "id6", "id7", "id8"]

# Creating embeddings for the documents
embeddings =[]
for i in range(len(documents)):
    embeddings.append(create_embeddings(documents[i]))

# Assuming 'client' is an instance of a database client
embeddings_collection = chroma_client.create_collection(name="embeddings", get_or_create=True)

# Add embeddings and documents to the collection
embeddings_collection.add(
    ids=ids,
    embeddings=embeddings,
    documents=documents
)

#Query text
search_list = ["apples"]

# Create embeddings for the query text
query_embeddings = create_embeddings(search_list)

# Query the collection using the embeddings
results = embeddings_collection.query(
    query_embeddings=query_embeddings,
    n_results=2
)

for i in range(2):
    print()

print('_'*100)

for i in range(2):
    print()

#Print the results
print(results["documents"][0])
