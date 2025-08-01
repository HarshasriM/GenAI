import os
import json
from dotenv import load_dotenv
from typing import List
from google import genai
from backend.prompts import basic
load_dotenv()

class GeminiAIClient:
    def __init__(self):
        GEMINI_API_KEY = os.getenv("API_KEY")
        self.gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    def get_response(self,model = "gemini-1.5-flash",tokens = 500 , messages : List[dict] = None):
        prompt = [basic]+messages
        sys_instruct = "<<SYS>>You are a chatbot. Your name is Reto.<</SYS>>"

        # Extract content from messages and format them properly
        user_messages = "\n".join([msg["content"] for msg in prompt]) if messages else ""
        
        full_prompt = f"{sys_instruct}\n\n{user_messages}"

        response = self.gemini_client.models.generate_content(
            model=model,
            contents=[full_prompt],  # Should be a list
           
        )
        # print(response.text)
        return response.text
    def create_text_embeddings(self,text):
        embedding_data = self.gemini_client.models.embed_content(
            model="text-embedding-004",
            contents=text,
        )
        return embedding_data.embeddings[0].values

