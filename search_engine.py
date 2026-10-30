
import json
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Load saved data
print("Loading BenchSplit search engine...")

with open(DATA_DIR / "judgment_chunks.json", "r", encoding="utf-8") as file:
    chunks = json.load(file)

embeddings = np.load(DATA_DIR / "judgment_embeddings.npy")

# Load the same model used for embeddings
model = SentenceTransformer(MODEL_NAME)

print("Search engine ready!")




def search_judgments(query, top_k=5):

    query_lower = query.lower()

    # Identify requested bail category
    required_bail_type = None

    if "anticipatory bail" in query_lower:
        required_bail_type = "ANTICIPATORY BAIL"

    elif "regular bail" in query_lower:
        required_bail_type = "REGULAR BAIL"

    # Identify requested judgment outcome
    required_outcome = None

    if any(word in query_lower for word in ["granted", "allowed"]):
        required_outcome = "BAIL GRANTED"

    elif any(word in query_lower for word in ["rejected", "refused", "denied"]):
        required_outcome = "BAIL REJECTED"

    # Generate query embedding
    query_embedding = model.encode(
        [query],
        normalize_embeddings=True
    )

    # Calculate similarity scores
    scores = np.dot(embeddings, query_embedding[0])

    ranked_indices = np.argsort(scores)[::-1]

    unique_results = {}

    for index in ranked_indices:

        result = chunks[index]

        bail_type = str(result.get("bail_type", "")).upper()
        outcome = str(result.get("disposal_nature", "")).upper()

        # Apply bail category filter
        if required_bail_type and bail_type != required_bail_type:
            continue

        # Apply outcome filter
        if required_outcome and required_outcome not in outcome:
            continue

        case_number = result.get("case_number", "")

        if not case_number:
            case_number = result.get("document_id", f"chunk_{index}")

        if case_number not in unique_results:
            unique_results[case_number] = (
                index,
                scores[index]
            )

    # Display results
    print("\n" + "=" * 65)
    print("BENCHSPLIT HYBRID SEARCH RESULTS")
    print("=" * 65)

    results = list(unique_results.values())[:top_k]

    if not results:
        print("No judgments matched the requested legal filters.")
        return

    for rank, (index, score) in enumerate(results, start=1):

        result = chunks[index]

        print(f"\nRank: {rank}")
        print(f"Similarity Score: {score:.4f}")
        print(f"Case Number: {result.get('case_number', 'N/A')}")
        print(f"Decision Date: {result.get('decision_date', 'N/A')}")
        print(f"Bail Type: {result.get('bail_type', 'N/A')}")
        print(f"Outcome: {result.get('disposal_nature', 'N/A')}")
        print(f"Relevant Text: {result.get('text', '')[:500]}")

        print("-" * 65)



if __name__ == "__main__":

    print("\nEnter your legal search query.")
    query = input("\nSearch: ")

    search_judgments(query)
