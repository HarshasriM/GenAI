import chromadb
import os
from backend.text_processing import get_processed_data
from backend.LLM import GeminiAIClient

class ChromaDBClient:
    # used singleton Pattern which instantiate the object only once
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChromaDBClient, cls).__new__(cls)
            cls._instance.client = chromadb.Client(settings=chromadb.config.Settings(persist_directory="./chroma_db"))
            cls._instance.llm_client = GeminiAIClient()
            cls._instance.collection = cls._instance.client.create_collection(name="company_data", get_or_create=True)
        return cls._instance
    
    async def adding_documents(self,conversational_id,file_path):
        processed_pdf_data= get_processed_data(file_path)
        metadata= {"conversational_id": conversational_id}
        self.collection.add(
            ids=processed_pdf_data["ids"],
            embeddings=processed_pdf_data["embeddings"],
            documents=processed_pdf_data["documents"],
            metadatas= [metadata] * len(processed_pdf_data['ids'])
        )
        return "done"
    
    async def query_database(self,query):
        results = self.collection.query(
            query_embeddings=[self.llm_client.create_text_embedding(query)],
            n_results=5
        )

        print(results)
        return results['documents'][0]