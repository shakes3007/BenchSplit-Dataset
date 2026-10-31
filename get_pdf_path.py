import pandas as pd
import re
from pathlib import Path

file = Path(
    "data/metadata/multi_court/year=2025/"
    "court=7_26/bench=dhcdb/metadata.parquet"
)

df = pd.read_parquet(file)

matches = df[
    df["raw_html"].astype(str).str.contains(
        "MDD MEDICAL SYSTEMS",
        case=False,
        na=False
    )
]

if matches.empty:
    print("Judgment not found")
else:
    row = matches.iloc[0]

    print("\nCASE TITLE:")
    print(row["title"])

    print("\nPDF LINK FIELD:")
    print(row["pdf_link"])

    print("\nPDF PATH FROM ORIGINAL HTML:")

    html = str(row["raw_html"])
    paths = re.findall(r"open_pdf\((.*?)\)", html)

    for path in paths:
        print(path)