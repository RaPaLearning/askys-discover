import os
import sys
from qdrant_client import QdrantClient

VDB_DIRNAME = 'gita_fastembed.qdrant'
VDB_COLLECTION_NAME = 'gita_begin_paras'


def is_content(text):
    return len(text) > 0 and not text.startswith('```') and not text.startswith('#')


def get_paragraphs_from_md(folder_path):
    paras = []
    filenames = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith('.md'):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Split paragraphs by double newlines
                paragraphs = [p.strip() for p in content.split('\n\n') if is_content(p.strip())]
                paras.extend(paragraphs)
                filenames.extend([filename] * len(paragraphs))
    return paras, filenames


def to_qdrant(paras, filenames, vdb_path=VDB_DIRNAME):
    client = QdrantClient(path=vdb_path)
    metadata = [{"source": fname} for fname in filenames]
    ids = list(range(len(paras)))
    client.add(
        collection_name="gita_begin_paras",
        documents=paras,
        metadata=metadata,
        ids=ids
    )
    count = client.count(collection_name=VDB_COLLECTION_NAME)
    print(f'done inserting. {VDB_COLLECTION_NAME} has {count} documents now')


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gita_begin_embed.py <folder_path>")
        sys.exit(1)
    folder = sys.argv[1]
    paras, filenames = get_paragraphs_from_md(folder)
    print(f"Found {len(paras)} paragraphs")

    to_qdrant(paras, filenames)
