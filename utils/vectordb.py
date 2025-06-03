from chromadb import Client

client = Client()
collection = client.get_or_create_collection("fraud_signals")


def add_fraud_signal(task_id: str, vector: list, metadata: dict):
    collection.add(
        documents=[str(task_id)],
        embeddings=[vector],
        metadatas=[metadata],
        ids=[task_id],
    )


def query_similar(vector: list, k=3):
    return collection.query(query_embeddings=[vector], n_results=k)
