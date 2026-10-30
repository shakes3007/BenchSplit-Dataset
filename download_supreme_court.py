import re
import subprocess
from pathlib import Path
import pandas as pd

print("Reading Supreme Court metadata...")

df = pd.concat([
    pd.read_parquet("sc_metadata_2023.parquet"),
    pd.read_parquet("sc_metadata_2024.parquet")
], ignore_index=True)

text = df[["title", "description"]].fillna("").astype(str).agg(" ".join, axis=1)

patterns = [
    r"negotiable instruments act|section\s*138|cheque dishonou?r",
    r"arbitration and conciliation act|arbitration agreement|arbitrator",
    r"section\s*482|482\s*crpc|inherent powers of the high court"
]

mask = pd.Series(False, index=df.index)

for pattern in patterns:
    mask |= text.str.contains(pattern, case=False, regex=True)

selected = df[mask].drop_duplicates(subset=["year", "path"])

output = Path("data/supreme_court_pdfs")
output.mkdir(parents=True, exist_ok=True)

downloaded = 0
skipped = 0
failed = 0

print(f"Found {len(selected)} matching judgments.")

for row in selected.itertuples(index=False):
    year = int(row.year)
    stem = str(row.path).strip().strip("/")

    if stem == "2024_10_1890_1901":
        print("Already downloaded: Bijay Agarwal")
        skipped += 1
        continue

    if stem.lower().endswith(".pdf"):
        filenames = [stem]
    else:
        filenames = [stem + "_EN.pdf", stem + ".pdf"]

    target = output / f"SC_{year}_{Path(stem).name}.pdf"

    if target.exists():
        print(f"Already exists: {target.name}")
        skipped += 1
        continue

    success = False

    for filename in filenames:
        source = (
            f"s3://indian-supreme-court-judgments/"
            f"data/pdf/year={year}/english/{filename}"
        )

        result = subprocess.run(
            [
                "aws", "s3", "cp", source, str(target),
                "--no-sign-request", "--region", "ap-south-1"
            ],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"DOWNLOADED: {target.name}")
            downloaded += 1
            success = True
            break

    if not success:
        print(f"FAILED: {stem}")
        failed += 1

print("\n========== DOWNLOAD SUMMARY ==========")
print("Downloaded:", downloaded)
print("Skipped:", skipped)
print("Failed:", failed)
print("Folder:", output.resolve())
