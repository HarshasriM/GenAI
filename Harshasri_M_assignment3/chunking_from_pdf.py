import chromadb
import os
import sys
import re
from dotenv import load_dotenv
from google import genai
import contextlib
import PyPDF2  
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("API_KEY")

gemini_client = genai.Client(api_key=GEMINI_API_KEY)



# Initialize ChromaDB client
storage_path = "./chroma_db"
os.makedirs(storage_path, exist_ok=True)
client = chromadb.PersistentClient(path=storage_path)
embeddings_collection = client.create_collection(name="embeddings", get_or_create=True)
print("chromadb client created")

# Extract text from PDF
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = [page.extract_text() for page in reader.pages if page.extract_text()]
        return ' '.join(text)

# Clean text
def clean_text(text):
    """Remove extra whitespace and unnecessary line breaks"""
    text = re.sub(r'\s+', ' ', text, flags=re.MULTILINE)
    return text.strip()

# Chunk text by sentences
def chunk_text_by_sentences(text, chunk_size=100):
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    return [' '.join(sentences[i:i + chunk_size]) for i in range(0, len(sentences), chunk_size)]

# Token size sentences
def token_size_sentences(sentences, token_size):
    chunks = []
    chunk = []
    token_count = 0
    for sentence in sentences:
        token_count += len(sentence.split(" "))
        if token_count <= token_size:
            chunk.append(sentence)
        else:
         chunks.append(' '.join(chunk))
         chunk = [sentence]
         token_count = len(sentence.split())
    if chunk:
     chunks.append(' '.join(chunk))
    return chunks





# Create embeddings for a list of documents using Gemini's text embedding model
def create_embeddings(document):
    if(not document):
        print("No documents to embed")
        return []
    embedding_data = gemini_client.models.embed_content(
        model="text-embedding-004",
        contents=document,
    )

    # print(embedding_data.embeddings[0].values)
    # Extract the embeddings from the response
    # embeddings = [i for i in embedding_data.embeddings]
    # temp= embedding_data.embeddings[0].values
    # print(type(temp[1]))
    return embedding_data.embeddings[0].values

# @contextlib.contextmanager
# def suppress_output():
#     with open(os.devnull, 'w') as devnull:
#         old_stdout = sys.stdout
#         old_stderr = sys.stderr
#         sys.stdout = devnull
#         sys.stderr = devnull
#         try:
#             yield
#         finally:
#             sys.stdout = old_stdout
#             sys.stderr = old_stderr


# Add embeddings and documents to the collection
def add_documents_to_collection(documents):
    embeddings =[]
    for i in range(len(documents)):
        embeddings.append(create_embeddings(documents[i]))
    ids = [f"id_{i}" for i in range(len(documents))]
    embeddings_collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents
        )
    print("success")

# Query the collection
def query_collection(query, n_results):
    query_embeddings = create_embeddings([query])
    results = embeddings_collection.query(
            query_embeddings=query_embeddings,
            n_results=n_results
        )
    return results.get('documents', [])

# Print the response

def print_response(response_docs):
    for doc in response_docs[0]:
        print(doc)
        print()



# Chunking by chunk size
def chunking_by_sentences(cleaned_text, search_query):
    chunk_size=100
    documents = chunk_text_by_sentences(cleaned_text, chunk_size)
    add_documents_to_collection(documents)
    no_of_responses=2
    response_docs = query_collection(search_query, no_of_responses)
    print('_'*50+'chunk by sentences'+'_'*50)
    print_response(response_docs)

# Chunking by token size
def token_by_sentences(cleaned_text, search_query):
    chunk_size=100
    sentences = chunk_text_by_sentences(cleaned_text, chunk_size)
    documents = token_size_sentences(sentences, 100)
    documents.pop(0)
    add_documents_to_collection(documents)
    no_of_responses=2
    response_docs = query_collection(search_query, no_of_responses)
    print('_'*50+'chunk by sentences'+'_'*50)
    print_response(response_docs)

def main():
    # PDF file path
    pdf_path = r'C:\Users\HarshaSri\Documents\Genai\Harshasri_M_assignment3\genai.pdf'
    # Extract and clean text from PDF
    raw_text = extract_text_from_pdf(pdf_path)
    if not raw_text.strip():
        raise ValueError("Extracted text is empty. Check the PDF file.")
    
    cleaned_text = clean_text(raw_text)

    # Semantic chunking by sentences
    search_query = "what is genai"
    #chunking_by_sentences(cleaned_text, search_query)
    token_by_sentences(cleaned_text, search_query)

if __name__ == "__main__":
    main()