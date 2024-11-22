from chromadb import Client
from chromadb.config import Settings
from langchain.chat_models import ChatOpenAI 
from langchain.text_splitter import RecursiveCharacterTextSplitter
from loguru import logger
import os

class KnowledgeRetrievalAgent:
    
    def __init__(self):
        try:
           
            self.chroma_client = Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory="data/documents"
            ))
            
           
            openai_api_key = os.getenv('OPENAI_API_KEY')
            if not openai_api_key:
                raise ValueError("OPENAI_API_KEY environment variable is not set.")
            self.llm = ChatOpenAI(api_key=openai_api_key) 

           
            self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500)

            logger.info("KnowledgeRetrievalAgent initialized successfully.")
        except Exception as e:
            logger.exception("Failed to initialize KnowledgeRetrievalAgent.")
            raise e
        
    def store_document(self,doc_title,content):
        try:
            chunks = self.text_splitter.split_text(content)
            collection = self.chroma_client.get_or_create_collection(name="documents")
            
            collection.add(
                documents=chunks,
                metadatas=[{"title": doc_title} for _ in chunks],
                ids=[f"{doc_title}_{i}" for i in range(len(chunks))]
            )
            logger.info(f"Document '{doc_title}' stored with {len(chunks)} chunks.")
        except Exception as e:
            logger.exception("Error in store_document.")
            raise e
    
    def retrieve_relevant_sections(self, query):
        try:
            collection = self.chroma_client.get_collection(name="documents")
            results = collection.query(
                query_texts=[query],
                n_results=3
            )
            relevant_texts = results.get('documents', [])
            logger.info(f"Retrieved {len(relevant_texts)} relevant sections for query '{query}'.")
            return relevant_texts
        except Exception as e:
            logger.exception("Error in retrieve_relevant_sections.")
            raise e

    def generate_summary(self,doc_title):

        try:
            collection = self.chroma_client.get_collection(name="documents")
            results = collection.query(
                query_texts=[doc_title],
                n_results=10
            )
            content_chunks = results.get('documents', [])
            content = ' '.join(content_chunks)
            
            summary = self.llm.predict(f"Summarize the following: {content}")
            logger.info(f"Summary generated for document '{doc_title}'.")
            return summary
        except Exception as e:
            logger.exception("Error in generate_summary.")
            raise e


         