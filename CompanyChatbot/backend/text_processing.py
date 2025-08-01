import os
import PyPDF2
import re
import tiktoken

from backend.llm import OpenAIClient

openai_client = OpenAIClient()

# Function to read PDFs from a specified directory
def read_pdfs_from_directory(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    return text

def clean_text(text):
    # Remove leading and trailing whitespace
    text = text.strip()
    # Replace multiple new lines with a single space
    text = re.sub(r'\n+', ' ', text)
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    return text

def extract_paragraphs(text):
    paragraphs = text.split('\n')
    return paragraphs

def extract_sentences(text):
    sentences = re.split(r'[.!?]\s*', text)
    return sentences

def count_tokens(text):
    tokenizer =  tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)
    return len(tokens)

def semantic_chunking(sentences, token_size, overlap):
    chunks = []
    chunk = []
    token_count = 0
    sentence_token_map = {sentence: count_tokens(sentence) for sentence in sentences}

    for sentence in sentences:
        sentence_token_count = sentence_token_map[sentence]
        if token_count + sentence_token_count <= token_size:
            chunk.append(sentence)
            token_count += sentence_token_count
        else:
            chunks.append(' '.join(chunk))
            print(chunk)
            chunk = chunk[:-overlap]
            print(chunk)
            token_count = sentence_token_count
    if chunk:
        chunks.append(' '.join(chunk))
    return chunks

def get_processed_data(pdf_file_path, chunking_type = "semantic", overlap = 1, token_limit = 100):
    text = read_pdfs_from_directory(pdf_file_path)
    cleaned_text = clean_text(text)
    if chunking_type == "semantic":
        sentences = extract_sentences(cleaned_text)
        chunks = semantic_chunking(sentences=sentences, token_size=token_limit, overlap=overlap)
        embeddings = openai_client.create_text_embeddings(documents=chunks)
    elif chunking_type == "sentence":
        chunks = extract_sentences(cleaned_text)
        embeddings = openai_client.create_text_embeddings(documents=chunks)
    
    resp =  {
        "ids": [f"id{i}" for i in range(1, len(chunks) + 1)],
        "embeddings": embeddings,
        "documents": chunks
    }

    return resp
