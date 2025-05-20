import os
import sys
from qdrant_client import QdrantClient

VDB_DIRNAME = 'gita_fastembed.qdrant'
VDB_COLLECTION_NAME = 'gita_begin_paras'


def is_content(text):
    return len(text) > 0 and not text.startswith('```') and not text.startswith('#')


def md_to_qdrant(folder_path, vdb_path=VDB_DIRNAME):
    qdrant_client = QdrantClient(path=vdb_path)
    for filename in os.listdir(folder_path):
        print(f"Processing {filename}...", end='')
        if filename.lower().endswith('.md'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Split paragraphs by double newlines
                paragraphs = [p.strip() for p in content.split('\n\n') if is_content(p.strip())]
                count = paras_to_qdrant(paragraphs, [filename] * len(paragraphs), qdrant_client)
                print(f"{len(paragraphs)} paras added. Total {count} paras.")


def paras_to_qdrant(paras, filenames, client):
    metadata = [{"source": fname} for fname in filenames]
    ids = list(range(len(paras)))
    client.add(
        collection_name=VDB_COLLECTION_NAME,
        documents=paras,
        metadata=metadata,
    )
    return client.count(collection_name=VDB_COLLECTION_NAME)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gita_begin_embed.py <folder_path>")
        sys.exit(1)
    folder = sys.argv[1]
    md_to_qdrant(folder)
