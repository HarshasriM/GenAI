import os
import PyPDF2
import re
import tiktoken
from backend.LLM import GeminiAIClient

gemini_client = GeminiAIClient()

#Function to read pdfs
def read_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in range(reader.numPages):
            text += reader.getPage(page).extract_text()
        return text
    
#cleaning the by removing spaces
def clean_text(text):
    #remove leading and trailing spaces
    text = text.strip()
    #replace multiple newlines with single space
    text = re.sub(r"\n+"," ",text)
    #replace multiple spaces with single space
    text = re.sub(r"\s+"," ",text)
    return text
def extract_paragraphs(text):
    #split the text into paragraphs
    paragraphs = text.split("\n")
    #remove empty paragraphs
    paragraphs = [para for para in paragraphs if para]
    return paragraphs

def extract_sentences(text):
    sentences = re.split(r'[.!?]\s*',text)
    return sentences

def count_tokens(text):
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokens = tokenizer.encode(text)
    return len(tokens)

def semantic_chunking(sentences:list,token_size=100,overlap=20):
    chunks = []
    chunk = []
    token_count = 0
    # sentence_token_map = {sentence : count_tokens(sentence) for sentence in sentences}
    for sentence in sentences:
        # sentence_token_count = sentence_token_map[sentence]
        # if token_count + sentence_token_count <= token_size:
        #     chunk .append(sentence)
        if token_count + count_tokens(sentence) <= token_size:
            chunk .append(sentence)
        else:
            chunks.append(" ".join(chunk))
            chunk = chunk[:-overlap]
            chunk.append(sentence)
            token_count = count_tokens(sentence)
    if chunk:
        chunks.append(" ".join(chunk))
    return chunks

def get_processed_data(file_path,chunking_type="semantic",overlap=1,token_limit=100):
    text=read_pdf(file_path)
    cleaned_text= clean_text(text)
    if chunking_type == "semantic":
        sentences = extract_sentences(cleaned_text)
        chunks = semantic_chunking(sentences,token_size=token_limit,overlap=overlap)
        embeddings = gemini_client.create_text_embeddings(documents=chunks)
    elif chunking_type == "fixed":
        chunks = extract_paragraphs(cleaned_text)
        embeddings = gemini_client.create_text_embeddings(documents=chunks)
    elif chunking_type == "sentence":
        chunks = extract_sentences(cleaned_text)
        embeddings = gemini_client.create_text_embeddings(documents=chunks)
    response = {
        "ids":[f"id{i}" for i in range(1,len(chunks)+1)],
        "embeddings":embeddings,
        "documents":chunks
    }
    return response