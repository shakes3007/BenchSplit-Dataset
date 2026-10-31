import pandas as pd
from pathlib import Path

files = list(Path("data/metadata/multi_court").rglob("metadata.parquet"))

total_records = 0
total_pdfs = 0
court_stats = {}

for i, file in enumerate(files, 1):
    df = pd.read_parquet(file, columns=["court", "pdf_exists"])

    total_records += len(df)
    total_pdfs += int(df["pdf_exists"].sum())

    for court, group in df.groupby("court"):
        stats = court_stats.setdefault(court, [0, 0])
        stats[0] += len(group)
        stats[1] += int(group["pdf_exists"].sum())

    del df
    print(f"Processed {i}/{len(files)} files", flush=True)

print("\nTOTAL JUDGMENTS:", total_records)
print("TOTAL AVAILABLE PDFS:", total_pdfs)
print("\nCOURT-WISE SUMMARY:")

for court, stats in sorted(court_stats.items()):
    print(f"{court}: {stats[0]} judgments, {stats[1]} PDFs")

