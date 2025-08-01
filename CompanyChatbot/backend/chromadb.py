import chromadb

from backend.text_processing import get_processed_data

from backend.llm import OpenAIClient

class ChromaDBClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChromaDBClient, cls).__new__(cls)
            cls._instance.client = chromadb.PersistentClient(path="./chroma_db")
            cls._instance.llm_client = OpenAIClient()
            cls._instance.collection = cls._instance.client.create_collection(name="company_data", get_or_create=True)
        return cls._instance

    async def create_database(self, conversational_id, pdf_file_path):
        processed_pdf_data = get_processed_data(pdf_file_path=pdf_file_path)
        metadata= {"conversational_id": conversational_id}
        self.collection.add(
            ids=processed_pdf_data["ids"],
            embeddings=processed_pdf_data["embeddings"],
            documents=processed_pdf_data["documents"],
            metadatas= [metadata] * len(processed_pdf_data['ids'])
        )
        return "done"
    
    async def query_database(self, conversational_id, query):
        results = self.collection.query(
            query_embeddings=[self.llm_client.create_text_embedding(query)],
            n_results=5
        )

        print(results)
        return results['documents'][0]


