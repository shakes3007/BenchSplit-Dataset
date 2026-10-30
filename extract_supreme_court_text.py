from pathlib import Path
import pdfplumber
import pandas as pd

source = Path("data/supreme_court_pdfs")
output = Path("data/extracted_text/supreme_court")
output.mkdir(parents=True, exist_ok=True)

results = []

for pdf in sorted(source.glob("*.pdf")):
    print(f"Extracting: {pdf.name}")

    pages_text = []
    page_count = 0

    try:
        with pdfplumber.open(pdf) as document:
            page_count = len(document.pages)

            for page in document.pages:
                text = page.extract_text() or ""
                pages_text.append(text)

        full_text = "\n\n".join(pages_text).strip()
        text_file = output / f"{pdf.stem}.txt"
        text_file.write_text(full_text, encoding="utf-8")

        results.append({
            "filename": pdf.name,
            "pages": page_count,
            "characters": len(full_text),
            "status": "SUCCESS" if len(full_text) > 100 else "CHECK"
        })

        print(f"  Pages: {page_count}, Characters: {len(full_text)}")

    except Exception as error:
        results.append({
            "filename": pdf.name,
            "pages": page_count,
            "characters": 0,
            "status": f"FAILED: {error}"
        })
        print(f"  FAILED: {error}")

report = pd.DataFrame(results)
report.to_csv(output / "extraction_report.csv", index=False)

print("\n========== EXTRACTION SUMMARY ==========")
print("PDFs processed:", len(results))
print("Successful:", (report["status"] == "SUCCESS").sum())
print("Needs checking:", (report["status"] == "CHECK").sum())
print("Failed:", report["status"].str.startswith("FAILED").sum())
print("Output folder:", output.resolve())
