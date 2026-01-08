import gzip
import pickle
from pathlib import Path


def normalize(text: str) -> str:
    return " ".join(
        text.lower()
            .replace("\r", " ")
            .replace("\n", " ")
            .split()
    )


def read_md_files(folder: Path) -> list[dict[str, str]]:
    docs: list[dict[str, str]] = []

    for md_path in sorted(folder.glob("*.md")):
        with md_path.open("r", encoding="utf-8") as f:
            raw_text = f.read()

        doc = {
            "id": md_path.stem,          # e.g. "04_34"
            "filename": md_path.name,
            "raw_text": raw_text,
            "norm_text": normalize(raw_text),
        }

        docs.append(doc)

    return docs


def save_gzipped_pickle(doc_contents: list[dict[str,str]], output_path: Path):
    with gzip.open(output_path, "wb") as f:
        pickle.dump(
            doc_contents,
            f,
            protocol=pickle.HIGHEST_PROTOCOL
        )


def main():
    input_folder = Path("gita-begin/gita")
    output_file = Path("normalized_docs.pkl.gz")

    if not input_folder.exists():
        raise FileNotFoundError(f"Folder not found: {input_folder}")

    docs = read_md_files(input_folder)

    save_gzipped_pickle(docs, output_file)

    print(f"Processed {len(docs)} files")
    print(f"Saved to {output_file.resolve()}")


if __name__ == "__main__":
    main()
