import os
import json
import uuid

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.llm import OpenAIClient

app = FastAPI()
openai_client = OpenAIClient()

class QueryRequest(BaseModel):
    conversational_id: Optional[str] = None
    query: str

class QueryResponse(BaseModel):
    conversational_id: str
    response: str

def save_history(conversational_id, query, response):
    history_file = f"history_{conversational_id}.json"
    history_entry = [
        {"role": "user", "content": query},
        {"role": "system", "content": response}
    ]

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


@app.post("/query", response_model=QueryResponse)
async def get_query_response(request: QueryRequest):
    try:
        if request.conversational_id:
            conversational_id = request.conversational_id
        else:
            conversational_id = str(uuid.uuid4())
        
        user_history = get_user_history(conversational_id=conversational_id)
        user_query_message = {"role": "user", "content": request.query}
        user_history.append(user_query_message)

        response = openai_client.get_response(messages=user_history)
        save_history(conversational_id, request.query, response)

        return QueryResponse(conversational_id=conversational_id, response=response)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))
