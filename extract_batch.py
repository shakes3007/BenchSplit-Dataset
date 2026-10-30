
import pdfplumber
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

PDF_DIR = BASE_DIR / "data" / "raw_pdfs"
OUTPUT_DIR = BASE_DIR / "data" / "extracted_text"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

pdf_files = list(PDF_DIR.glob("*.pdf"))

print(f"Found {len(pdf_files)} PDF files.")

successful = 0
failed = 0
skipped = 0

for pdf_file in pdf_files:

    output_file = OUTPUT_DIR / f"{pdf_file.stem}.txt"

    if output_file.exists():
        print(f"Already extracted: {pdf_file.name}")
        skipped += 1
        continue

    try:
        all_pages = []

        with pdfplumber.open(pdf_file) as pdf:

            for page_number, page in enumerate(pdf.pages, start=1):

                text = page.extract_text() or ""

                all_pages.append(
                    f"\n--- PAGE {page_number} ---\n{text}"
                )

        full_text = "\n".join(all_pages)

        output_file.write_text(
            full_text,
            encoding="utf-8"
        )

        print(f"Extracted: {pdf_file.name}")
        successful += 1

    except Exception as error:
        print(f"Failed: {pdf_file.name}: {error}")
        failed += 1

print("\nBATCH EXTRACTION COMPLETE")
print("Successful:", successful)
print("Skipped:", skipped)
print("Failed:", failed)
