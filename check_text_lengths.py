
import pandas as pd
from pathlib import Path

# Load our 15 shortlisted judgments
shortlist = pd.read_csv("data/processed/shortlist_15.csv")

results = []

print("Checking judgment text availability...\n")

for index, row in shortlist.iterrows():

    metadata_path = Path(row["metadata_file"])

    try:
        # Read the corresponding metadata file
        data = pd.read_parquet(metadata_path)

        # Find the matching judgment using its PDF filename
        pdf_filename = str(row["pdf_link"]).split("/")[-1]

        matching = data[
            data["pdf_link"].astype(str).str.endswith(pdf_filename)
        ]

        # Fall back to matching by case title
        if matching.empty:
            matching = data[
                data["title"].astype(str).str.contains(
                    str(row["title"])[:35],
                    case=False,
                    na=False
                )
            ]

        if not matching.empty:
            text = str(matching.iloc[0].get("raw_html", ""))
            text_length = len(text)
            status = "TEXT AVAILABLE" if text_length > 0 else "NO TEXT"
        else:
            text_length = 0
            status = "RECORD NOT FOUND"

    except Exception as error:
        text_length = -1
        status = f"ERROR: {error}"

    results.append({
        "court": row["court"],
        "case_title": row["title"],
        "text_characters": text_length,
        "status": status
    })

# Display results
result_df = pd.DataFrame(results)

print(result_df.to_string(index=False))

# Save results for later use
output_path = Path("data/processed/text_availability_report.csv")
result_df.to_csv(output_path, index=False)

print("\n===================================")
print("CHECK COMPLETE")
print("Total judgments:", len(result_df))
print("Text available:", (result_df["text_characters"] > 0).sum())
print("Report saved to:", output_path)
