
import json
import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

TEXT_DIR = BASE_DIR / "data" / "extracted_text"
METADATA_DIR = BASE_DIR / "data" / "metadata"

OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

records = []

for metadata_file in sorted(METADATA_DIR.glob("*.json")):

    text_file = TEXT_DIR / f"{metadata_file.stem}.txt"

    if not text_file.exists():
        print(f"Missing text: {metadata_file.stem}")
        continue

    with open(metadata_file, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    judgment_text = text_file.read_text(
        encoding="utf-8"
    )

    record = {
        "document_id": metadata_file.stem,
        "court": metadata.get("court"),
        "case_number": metadata.get("case_number"),
        "decision_date": metadata.get("decision_date"),
        "judges": metadata.get("judges", []),
        "bail_type": metadata.get("bail_type"),
        "disposal_nature": metadata.get("disposal_nature", []),
        "decision_evidence": metadata.get("decision_evidence"),
        "judgment_text": judgment_text
    }

    records.append(record)

# Save complete JSONL dataset
jsonl_file = OUTPUT_DIR / "benchsplit_dataset.jsonl"

with open(jsonl_file, "w", encoding="utf-8") as f:
    for record in records:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

# Save metadata CSV without full judgment text
csv_file = OUTPUT_DIR / "benchsplit_dataset.csv"

csv_fields = [
    "document_id",
    "court",
    "case_number",
    "decision_date",
    "judges",
    "bail_type",
    "disposal_nature",
    "decision_evidence"
]

with open(csv_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=csv_fields)
    writer.writeheader()

    for record in records:
        row = record.copy()
        row["judges"] = ", ".join(row["judges"])
        row["disposal_nature"] = ", ".join(
            row["disposal_nature"]
        )
        writer.writerow({
            key: row.get(key) for key in csv_fields
        })

print("\nBENCHSPLIT DATASET CREATED")
print(f"Total judgments: {len(records)}")
print(f"JSONL: {jsonl_file}")
print(f"CSV: {csv_file}")
