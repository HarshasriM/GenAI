import os
import json
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.llm import OpenAIClient
from backend.chromadb import ChromaDBClient

app = FastAPI()
openai_client = OpenAIClient()

class CompanyInfoRequest(BaseModel):
    conversational_id: Optional[str] = None
    filename: str

class CompanyInfoQueryRequest(BaseModel):
    conversational_id: Optional[str] = None
    query: str

class CompanyInfoResponse(BaseModel):
    conversational_id: str
    response: str

class QueryRequest(BaseModel):
    conversational_id: Optional[str] = None
    query: str

class QueryResponse(BaseModel):
    conversational_id: str
    response: str

def save_history(conversational_id, query, response):
    history_file = f"history_{conversational_id}.json"
    history_entry = [{"role": "user", "content": query}, {"role": "system", "content": response}]

    if os.path.exists(history_file):
        with open(history_file, "r") as file:
            history = json.load(file)
    else:
        history = []

    history = history + history_entry

    with open(history_file, "w") as file:
        json.dump(history, file, indent=4)

def get_user_history(conversational_id):
    history_file = f"history_{conversational_id}.json"
    if os.path.exists(history_file):
        with open(history_file, "r") as file:
            history = json.load(file)
        return history
    else:
        return []

@app.post("/create/vector/database", response_model= CompanyInfoResponse)
async def extract_company_data(request:CompanyInfoRequest):
    chroma_client = ChromaDBClient()
    if request.conversational_id:
        conversational_id = request.conversational_id
    else:
        conversational_id = str(uuid.uuid4())
    resp = await chroma_client.create_database(conversational_id= conversational_id, pdf_file_path=request.filename)
    return {"conversational_id": conversational_id, "response": "success"}

@app.post("/query/vector/database")
async def query_company_data(request:CompanyInfoQueryRequest):
    chroma_client = ChromaDBClient()
    if request.conversational_id:
        conversational_id = request.conversational_id
    else:
        conversational_id = str(uuid.uuid4())
    resp = await chroma_client.query_database(conversational_id= conversational_id, query=request.query)
    return {"conversational_id": conversational_id, "response": resp}

@app.post("/query", response_model=QueryResponse)
async def get_query_response(request: QueryRequest):
    try:
        chroma_client = ChromaDBClient()
        if request.conversational_id:
            conversational_id = request.conversational_id
        else:
            conversational_id = str(uuid.uuid4())
        rag_resp = await chroma_client.query_database(conversational_id= conversational_id, query=request.query)
        user_history = get_user_history(conversational_id=conversational_id)
        info_to_system = {"role": "system", "content" : f"Answer using the this information -- {' '.join(rag_resp)}"}
        user_query_message = {"role": "user", "content": request.query}
        user_history.append(info_to_system)
        user_history.append(user_query_message)

        response = openai_client.get_response(messages=user_history)
        save_history(conversational_id, request.query, response)

        return QueryResponse(conversational_id=conversational_id, response=response)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))
