import unittest
import os
import shutil
from agents.knowledge_retrieval_agent import KnowledgeRetrievalAgent

class TestKnowledgeRetrievalAgent(unittest.TestCase):
    
    def setUp(self):
        self.agent=KnowledgeRetrievalAgent()
        self.test_data_dir="data/documents"
        if os.path.exists(self.test_data_dir):
            shutil.rmtree(self.test_data_dir)
        os.makedirs(self.test_data_dir,exist_ok=True)


    def tearDown(self):
        if os.path.exists(self.test_data_dir):
            shutil.rmtree(self.test_data_dir)

    def test_store_document(self):
   
        doc_title = "Test Document"
        content = "This is a test document. It contains multiple sentences for testing purposes."
        try:
            self.agent.store_document(doc_title, content)
       
            collection = self.agent.chroma_client.get_collection(name="documents")
            results = collection.query(query_texts=["test"], n_results=1)
            self.assertGreater(len(results.get("documents", [])), 0, "Document storage failed.")
        except Exception as e:
            self.fail(f"store_document raised an exception {e}")


    def test_retrieve_relevant_sections(self):
    
        doc_title = "Test Document"
        content = "This is a test document. It contains important content related to testing."
        self.agent.store_document(doc_title, content)
        query = "testing"
        try:
            results = self.agent.retrieve_relevant_sections(query)
            self.assertGreater(len(results), 0, "No relevant sections retrieved.")
        except Exception as e:
            self.fail(f"retrieve_relevant_sections raised an exception {e}")


    def test_generation_summary(self):

        doc_title="Test Document"
        content="This document explain various topics about testing strategic and practices"
        self.agent.store_document(doc_title,content)
        try:
           
            summary = self.agent.generate_summary(doc_title)
            self.assertIsInstance(summary, str, "Summary is not a string.")
            self.assertGreater(len(summary), 0, "Generated summary is empty.")
        except Exception as e:
            self.fail(f"generate_summary raised an exception {e}")


if __name__ == "__main__":
    unittest.main()
