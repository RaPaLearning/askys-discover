# pip install qdrant-client[fastembed]

from qdrant_client import QdrantClient

print('Create embeddings')
# client = QdrantClient(":memory:")
client = QdrantClient(path="embeddings.qdrant")

print('Documents, metadata, and IDs')
docs = ["Qdrant has Langchain integrations", "Qdrant also has Llama Index integrations", "doberman is a dog breed"]
metadata = [
    {"source": "QLangchain-docs"},
    {"source": "QLlama-docs"},
    {"source": "Some Wikipedia"},
]
ids = [42, 2, 3]

print('...adding them')
client.add(
    collection_name="demo_collection",
    documents=docs,
    metadata=metadata,
    ids=ids
)
count = client.count(collection_name="demo_collection")
print(f'done inserting. demo_collection has {count} documents now')
