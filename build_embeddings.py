
import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

# Project paths
BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "data" / "processed" / "benchsplit_dataset.jsonl"
OUTPUT_DIR = BASE_DIR / "data" / "processed"

# Embedding model
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Chunk settings
CHUNK_SIZE = 120
OVERLAP = 30


def split_into_chunks(text):
    words = text.split()
    chunks = []

    if not words:
        return chunks

    step = CHUNK_SIZE - OVERLAP

    for start in range(0, len(words), step):
        chunk = words[start:start + CHUNK_SIZE]

        if chunk:
            chunks.append(" ".join(chunk))

        if start + CHUNK_SIZE >= len(words):
            break

    return chunks


def main():
    print("Loading judgment dataset...")

    records = []

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        for line in file:
            if line.strip():
                records.append(json.loads(line))

    print(f"Loaded {len(records)} judgments.")

    print("Preparing judgment chunks...")

    all_chunks = []

    for record in records:
        judgment_text = record.get("judgment_text", "")

        metadata = (
            f"Case: {record.get('case_number', '')}. "
            f"Court: {record.get('court', '')}. "
            f"Judges: {', '.join(record.get('judges', []))}. "
            f"Bail type: {record.get('bail_type', '')}. "
            f"Outcome: {record.get('disposal_nature', '')}. "
            f"Decision evidence: {record.get('decision_evidence', '')}."
        )

        chunks = split_into_chunks(judgment_text)

        for index, chunk in enumerate(chunks):
            all_chunks.append({
                "document_id": record.get("document_id", ""),
                "case_number": record.get("case_number", ""),
                "decision_date": record.get("decision_date", ""),
                "bail_type": record.get("bail_type", ""),
                "disposal_nature": record.get("disposal_nature", ""),
                "chunk_index": index,
                "text": metadata + " " + chunk
            })

    print(f"Created {len(all_chunks)} text chunks.")

    print("Loading Sentence Transformer model...")

    model = SentenceTransformer(MODEL_NAME)

    texts = [chunk["text"] for chunk in all_chunks]

    print("Generating embeddings...")

    embeddings = model.encode(
        texts,
        batch_size=16,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    np.save(
        OUTPUT_DIR / "judgment_embeddings.npy",
        embeddings
    )

    with open(
        OUTPUT_DIR / "judgment_chunks.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(all_chunks, file, ensure_ascii=False, indent=2)

    print("\nEMBEDDING GENERATION COMPLETE")
    print(f"Judgments processed: {len(records)}")
    print(f"Chunks generated: {len(all_chunks)}")
    print(f"Embedding dimensions: {embeddings.shape[1]}")
    print("Saved judgment_embeddings.npy")
    print("Saved judgment_chunks.json")


if __name__ == "__main__":
    main()
