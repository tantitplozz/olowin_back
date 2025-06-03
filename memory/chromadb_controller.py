# memory/chromadb_controller.py

import os
import chromadb
from chromadb.config import Settings
from chromadb.api.models.Collection import Collection
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
import requests
from typing import Optional, List # Removed Dict, Any as they are not used

load_dotenv()

CHROMA_HOST_ENV = os.getenv("CHROMA_HOST", "http://chromadb:8000")
COLLECTION_NAME = "omnicard_memory"

parsed_host = "chromadb"
parsed_port = 8000
if CHROMA_HOST_ENV:
    if CHROMA_HOST_ENV.startswith("http://") or CHROMA_HOST_ENV.startswith("https://"):
        stripped_url = CHROMA_HOST_ENV.split("://")[1]
        host_port_parts = stripped_url.split(":")
        parsed_host = host_port_parts[0]
        if len(host_port_parts) > 1 and host_port_parts[1].isdigit():
            parsed_port = int(host_port_parts[1])
    else:
        host_port_parts = CHROMA_HOST_ENV.split(":")
        parsed_host = host_port_parts[0]
        if len(host_port_parts) > 1 and host_port_parts[1].isdigit():
            parsed_port = int(host_port_parts[1])

print(f"[ChromaDB Controller] Target ChromaDB host: '{parsed_host}', port: {parsed_port}")

# To avoid using global for _collection_instance, we can wrap it in a class or pass it around.
# For simplicity and given its module-level singleton nature here, global was used.
# A refactor could be: 
class ChromaDBManager:
    def __init__(self):
        self.collection: Optional[Collection] = None
        self._initialize_collection_with_retry()

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(3), retry=retry_if_exception_type((requests.exceptions.ConnectionError, Exception)))
    def _initialize_collection(self):
        print(f"[ChromaDB Manager] Attempting to connect to ChromaDB at host: '{parsed_host}', port: {parsed_port}...")
        client = chromadb.HttpClient(host=parsed_host,
                                     port=parsed_port,
                                     settings=Settings(anonymized_telemetry=False))
        self.collection = client.get_or_create_collection(name=COLLECTION_NAME)
        print(f"[ChromaDB Manager] Successfully connected and got collection '{COLLECTION_NAME}'.")

    def _initialize_collection_with_retry(self):
        try:
            self._initialize_collection()
        except Exception as e:
            print(f"[ChromaDB Manager] CRITICAL: Failed to connect to ChromaDB after multiple retries: {e}")
            self.collection = None

    def add_to_memory(self, user_input: str, agent_response: str):
        if self.collection is None:
            print("[ChromaDB Error] Collection not available. Cannot add to memory.")
            return
        if not user_input or not agent_response:
            print("[ChromaDB] Warning: Attempted to add empty user_input or agent_response to memory.")
            return
        try:
            doc_id = f"id_{hash(user_input)}" 
            self.collection.add(
                documents=[agent_response],
                metadatas=[{"source": "agent", "user_input": user_input[:256]}],
                ids=[doc_id]
            )
            print(f"[ChromaDB] Added to memory: ID '{doc_id}', Response: '{agent_response[:50]}...'")
        except Exception as e:
            print(f"[ChromaDB] Error adding to memory: {e}")

    def query_memory(self, query: str, top_k: int = 3) -> List[str]:
        if self.collection is None:
            print("[ChromaDB Error] Collection not available. Cannot query memory.")
            return []
        if not query:
            print("[ChromaDB] Warning: Attempted to query with empty text.")
            return []
        try:
            results = self.collection.query(query_texts=[query], n_results=top_k, include=["documents"])
            documents_list_of_lists = results.get("documents")
            if isinstance(documents_list_of_lists, list) and documents_list_of_lists:
                retrieved_docs: List[str] = documents_list_of_lists[0]
                print(f"[ChromaDB] Query: '{query[:50]}...', Found: {len(retrieved_docs)} results")
                return retrieved_docs
            # Removed unnecessary else after return
            print(f"[ChromaDB] Query: '{query[:50]}...', No documents found or unexpected format in results.")
            return []
        except Exception as e:
            print(f"[ChromaDB] Error querying memory: {e}")
            return []

# Instantiate the manager making its methods available for import
db_manager = ChromaDBManager()

# Expose only the public interface methods
add_to_memory = db_manager.add_to_memory
query_memory = db_manager.query_memory

# Your simplified versions (from user prompt - will use the ones above that are more complete)
# def add_to_memory(prompt: str):
#     collection.add(documents=[prompt], ids=[prompt])

# def query_memory(prompt: str, n=2):
#     results = collection.query(query_texts=[prompt], n_results=n)
#     return results.get("documents", [[]])[0] 