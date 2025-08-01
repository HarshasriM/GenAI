import os
from openai import OpenAI
from pydantic import BaseModel
from typing import List
from backend.prompts import basic
from dotenv import load_dotenv

class BooleanResponse(BaseModel):
    response: bool

import os

import json


load_dotenv()

class OpenAIClient():
    def __init__(self) -> None:
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI()

    def get_response(self, model="gpt-3.5-turbo", tokens=500, messages: List[dict] = None):
        prompt = [basic] + messages
        print(prompt)
        response = self.client.chat.completions.create(
            model=model,
            messages=prompt,
            max_tokens=tokens
        )

        return response.choices[0].message.content

    def create_text_embedding(self, text):
        embedding = self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=text,
            encoding_format="float"
        )
        return embedding.data[0].embedding