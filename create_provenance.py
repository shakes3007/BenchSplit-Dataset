import hashlib
from pathlib import Path
import pandas as pd

folder = Path("data/supreme_court_pdfs")
metadata = pd.concat([
    pd.read_parquet("sc_metadata_2023.parquet"),
    pd.read_parquet("sc_metadata_2024.parquet")
], ignore_index=True)

files = list(folder.glob("*.pdf"))
records = []

for pdf in files:
    if pdf.name == "Bijay_Agarwal_2024.pdf":
        stem = "2024_10_1890_1901"
        year = 2024
    else:
        parts = pdf.stem.split("_", 2)
        year = int(parts[1])
        stem = parts[2]

    matches = metadata[
        (metadata["year"].astype(int) == year) &
        (metadata["path"].astype(str).str.contains(stem, regex=False))
    ]

    row = matches.iloc[0] if not matches.empty else {}

    digest = hashlib.sha256(pdf.read_bytes()).hexdigest()
    records.append({
        "title": row.get("title", "Bijay Agarwal" if pdf.name == "Bijay_Agarwal_2024.pdf" else "Metadata not matched"),
        "citation": row.get("citation", ""),
        "decision_date": row.get("decision_date", ""),
        "local_filename": pdf.name,
        "source_url": f"https://indian-supreme-court-judgments.s3.ap-south-1.amazonaws.com/data/pdf/year={year}/english/{stem}_EN.pdf",
        "sha256": digest,
        "file_size_bytes": pdf.stat().st_size
    })

output = pd.DataFrame(records)
output.to_csv("data/supreme_court_provenance.csv", index=False)
print("Records created:", len(output))
print("Output: data/supreme_court_provenance.csv")
print(output[["local_filename", "sha256"]].to_string(index=False))
