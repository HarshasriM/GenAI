import json
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))  # Adds the 'backend' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  # Adds the root directory
HISTORY_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'history_files'))
# Ensure the folder exists
os.makedirs(HISTORY_FOLDER, exist_ok=True)

from backend.LLM import GeminiAIClient

# Initialization
app = FastAPI()
gemini_client = GeminiAIClient()

# Pydantic models

class QueryRequest(BaseModel):
    conversational_id: Optional[str] = None
    query: str

class QueryResponse(BaseModel):
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

# Route to handle user queries
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

        response = gemini_client.get_response(messages=user_history)
        save_history(conversational_id, request.query, response)

        return QueryResponse(conversational_id=conversational_id, response=response)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))
    # except Exception as e:
    #     print(str(e))
    #     raise HTTPException(status_code=500, detail=str(e))