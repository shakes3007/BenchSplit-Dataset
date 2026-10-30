
import pdfplumber
from pathlib import Path

pdf_path = Path(
    "data/raw_pdfs/BRHC010547492024_1_2025-02-25.pdf"
)

output_dir = Path("data/extracted_text")
output_dir.mkdir(parents=True, exist_ok=True)

output_path = output_dir / f"{pdf_path.stem}.txt"

all_pages = []

with pdfplumber.open(pdf_path) as pdf:
    print("Total pages:", len(pdf.pages))

    for page_number, page in enumerate(pdf.pages, start=1):
        text = page.extract_text() or ""

        print(
            f"Page {page_number}: "
            f"{len(text)} characters extracted"
        )

        all_pages.append(
            f"\n--- PAGE {page_number} ---\n{text}"
        )

full_text = "\n".join(all_pages)

output_path.write_text(
    full_text,
    encoding="utf-8"
)

print("\nExtraction completed.")
print("Total characters:", len(full_text))
print("Output:", output_path)
print("\nPreview:")
print(full_text[:1500])
