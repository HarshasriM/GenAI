import os
import json
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List,Optional



app = FastAPI()

import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))  # Adds the 'backend' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Adds the root directory
HISTORY_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'history_files'))
# Ensure the folder exists
os.makedirs(HISTORY_FOLDER, exist_ok=True)
from backend.LLM import GeminiAIClient
from backend.chroma_db import ChromaDBClient
gemini_client = GeminiAIClient()


# pydantic models

class CompanyInfoRequest(BaseModel):
    conversational_id: Optional[str] = None
    filename: str

class CompanyInfoQueryRequest(BaseModel):
    conversational_id: Optional[str] = None
    query: str

class CompanyInfoResponse(BaseModel):
    conversational_id: str
    response: str


# Helper functions
def save_history(conversational_id: str, query: str, response: str):
    history_file = os.path.join(HISTORY_FOLDER, f"history_{conversational_id}.json")
    history_entry = [
        {"role": "user", "content": query},
        {"role": "system", "content": response},
    ]
    
    # Load existing history if available
    if os.path.exists(history_file):
        with open(history_file, "r") as file:
            history = json.load(file)
    else:
        history = []

    history.extend(history_entry)  # Append correctly
    with open(history_file, "w") as file:
        json.dump(history, file, indent=4)

def get_user_history(conversational_id: str) -> List[dict]:
    history_file =os.path.join(HISTORY_FOLDER, f"history_{conversational_id}.json")
    if os.path.exists(history_file):
        with open(history_file, "r") as file:
            return json.load(file)
    return []  # Return empty list if no history exists

@app.post("/create/vector/database",response_model = CompanyInfoResponse)
async def create_vector_database(request: CompanyInfoRequest):
    try:
        if request.conversational_id:
            conversational_id = request.conversational_id
        else:
            conversational_id = str(uuid.uuid4())
        chroma_db_client = ChromaDBClient()
        await chroma_db_client.adding_documents(conversational_id=conversational_id,file_path=request.filename)
        return CompanyInfoResponse(conversational_id=conversational_id,response="done")
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500,detail=str(e))

@app.post("/query/vector/database")
async def query_vector_database(request: CompanyInfoQueryRequest):
    try:
        if request.conversational_id:
            conversational_id = request.conversational_id
        else:
            conversational_id = str(uuid.uuid4())
        chroma_db_client = ChromaDBClient()
        response = await chroma_db_client.query_database(query=request.query)
        return CompanyInfoResponse(conversational_id=conversational_id,response=response)
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    
@app.post("/query", response_model=CompanyInfoResponse)
async def get_query_response(request: CompanyInfoQueryRequest):
    try:
        chroma_client = ChromaDBClient()
        if request.conversational_id:
            conversational_id = request.conversational_id
        else:
            conversational_id = str(uuid.uuid4())
        rag_response = await chroma_client.query_database(conversational_id=conversational_id, query=request.query)
        user_history = get_user_history(conversational_id=conversational_id)
        info_to_system = {"role": "system", "content" : f"Answer using the this information -- {' '.join(rag_response)}"}
        user_query_message = {"role": "user", "content": request.query}
        user_history.append(info_to_system)
        user_history.append(user_query_message)

        response = gemini_client.get_response(messages=user_history)
        save_history(conversational_id, request.query, response)

        return CompanyInfoResponse(conversational_id=conversational_id, response=response)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))