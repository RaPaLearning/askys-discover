from qdrant_client import QdrantClient

print('Initializing...')
client = QdrantClient(path="embeddings.qdrant")

print('Searching:')
search_result = client.query(
    collection_name="demo_collection",
    query_text="animal",
)
for i in range(3):
    print(f'{search_result[i].score}: {search_result[i].metadata["source"]}: {search_result[i].document}')
