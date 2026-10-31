
import pandas as pd
import requests
from pathlib import Path
import pdfplumber

# Load Delhi High Court metadata
metadata_path = Path(
    "data/metadata/multi_court/year=2025/court=7_26/bench=dhcdb/metadata.parquet"
)

if not metadata_path.exists():
    raise FileNotFoundError(f"Metadata file not found: {metadata_path}")

df = pd.read_parquet(metadata_path)

# Check required columns
required_columns = ["title", "description", "cnr", "pdf_link"]
missing = [col for col in required_columns if col not in df.columns]

if missing:
    raise ValueError(f"Missing metadata columns: {missing}")

# Find arbitration related judgments
search_text = (
    df["title"].fillna("").astype(str)
    + " "
    + df["description"].fillna("").astype(str)
)

pattern = (
    r"arbitrator|arbitration|section 12|section 11|"
    r"appointment of arbitrator|unilateral appointment"
)

mask = search_text.str.contains(
    pattern,
    case=False,
    regex=True,
    na=False
)

candidates = (
    df.loc[mask]
    .drop_duplicates(subset=["cnr"])
    .head(15)
)

print(f"Candidates found: {len(candidates)}")

# Output folders
raw_folder = Path("data/raw_pdfs/conflict_research")
text_folder = Path("data/extracted_text/conflict_research")

raw_folder.mkdir(parents=True, exist_ok=True)
text_folder.mkdir(parents=True, exist_ok=True)

base_url = (
    "https://indian-high-court-judgments.s3.ap-south-1.amazonaws.com/"
    "data/pdf/year=2025/court=7_26/bench=dhcdb/"
)

session = requests.Session()

success = 0
skipped = 0
failed = 0

# Download and extract judgments
for index, row in candidates.iterrows():

    name = str(row["pdf_link"]).split("/")[-1]

    if not name or name.lower() == "nan":
        print("SKIPPED: Missing PDF filename")
        skipped += 1
        continue

    pdf_path = raw_folder / name
    text_path = text_folder / (pdf_path.stem + ".txt")

    # Avoid downloading files that already exist
    if pdf_path.exists() and text_path.exists():
        print("ALREADY PROCESSED:", name)
        skipped += 1
        continue

    url = base_url + name

    try:
        print(f"\nProcessing: {row['title']}")

        # Download PDF if needed
        if not pdf_path.exists():
            response = session.get(url, timeout=60)
            response.raise_for_status()

            if not response.content.startswith(b"%PDF"):
                raise ValueError("Downloaded file is not a valid PDF")

            pdf_path.write_bytes(response.content)

        # Extract text
        with pdfplumber.open(pdf_path) as document:
            extracted_text = "\n".join(
                page.extract_text() or ""
                for page in document.pages
            )

        if not extracted_text.strip():
            raise ValueError("No text could be extracted from this PDF")

        text_path.write_text(
            extracted_text,
            encoding="utf-8"
        )

        success += 1

        print("SUCCESS:", row["title"])
        print("Characters extracted:", len(extracted_text))
        print("Saved text:", text_path)

    except Exception as error:
        failed += 1
        print("FAILED:", name, "|", str(error))

print("\n========== DOWNLOAD SUMMARY ==========")
print("Total candidates:", len(candidates))
print("Successfully processed:", success)
print("Already processed or skipped:", skipped)
print("Failed:", failed)
print("PDF folder:", raw_folder)
print("Text folder:", text_folder)