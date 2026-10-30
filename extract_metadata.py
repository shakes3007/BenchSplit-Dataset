
import re
import json
from pathlib import Path

# Project directories
BASE_DIR = Path(__file__).resolve().parent

INPUT_DIR = BASE_DIR / "data" / "extracted_text"
OUTPUT_DIR = BASE_DIR / "data" / "metadata"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def extract_metadata(text):

    metadata = {}

    # Normalize text
    text = text.replace("\x0c", "\n")
    upper_text = text.upper()

    # Court name
    court = re.search(
        r"IN THE HIGH COURT OF JUDICATURE AT ([A-Z ]+)",
        text,
        re.IGNORECASE
    )

    metadata["court"] = (
        court.group(0).strip() if court else None
    )

    # Case number
    case = re.search(
        r"(CRIMINAL\s+MISCELLANEOUS|CR\.\s*MISC\.|CRIMINAL\s+APPEAL|"
        r"CIVIL\s+REVIEW|C\.\s*REV\.|CWJC|CRIMINAL\s+WRIT)"
        r"[^\n]{0,100}",
        text[:5000],
        re.IGNORECASE
    )

    metadata["case_number"] = (
        re.sub(r"\s+", " ", case.group(0)).strip()
        if case else None
    )

    # Decision date
    date = re.search(
        r"(?:DT\.?|DATED\s*:?)\s*(\d{2}-\d{2}-\d{4})",
        text[:5000],
        re.IGNORECASE
    )

    if not date:
        date = re.search(
            r"\b(\d{2}-\d{2}-\d{4})\b",
            text[:1500]
        )

    metadata["decision_date"] = (
        date.group(1) if date else None
    )

    # Judge names
    judges = re.findall(
        r"(?:HONOURABLE\s+)?(?:MR\.?\s+|MRS\.?\s+)?"
        r"JUSTICE\s+([A-Z][A-Z .'-]+)",
        upper_text,
        re.IGNORECASE
    )

    metadata["judges"] = list(dict.fromkeys(
        re.sub(r"\s+", " ", judge).strip()
        for judge in judges
    ))

    # Identify bail type
    if re.search(r"ANTICIPATORY\s+BAIL", upper_text):
        metadata["bail_type"] = "ANTICIPATORY BAIL"
    elif re.search(r"REGULAR\s+BAIL", upper_text):
        metadata["bail_type"] = "REGULAR BAIL"
    elif re.search(r"\bBAIL\b", upper_text):
        metadata["bail_type"] = "BAIL"
    else:
        metadata["bail_type"] = None

    # Examine only the final portion of the judgment.
    # This reduces interference from earlier orders and arguments.
    final_text = upper_text[-6000:]
    final_text = re.sub(r"\s+", " ", final_text)

    # Decision classification
    patterns = [
        (
            "BAIL GRANTED",
            r"(?:ENLARGED|RELEASED)\s+(?:THE\s+)?(?:PETITIONER\s+)?ON\s+BAIL|"
            r"GRANT(?:ED)?\s+OF\s+(?:REGULAR\s+|ANTICIPATORY\s+)?BAIL"
            r".{0,100}(?:ALLOW|GRANT)|"
            r"(?:BAIL|ANTICIPATORY\s+BAIL)\s+APPLICATION\s+"
            r"(?:IS\s+)?(?:HEREBY\s+)?ALLOWED"
        ),
        (
            "BAIL REJECTED",
            r"(?:PRAYER|APPLICATION|PETITION|PLEA)"
            r"\s+FOR\s+(?:REGULAR\s+|ANTICIPATORY\s+)?BAIL"
            r".{0,150}(?:REJECTED|DISMISSED)|"
            r"(?:BAIL|ANTICIPATORY\s+BAIL)\s+"
            r"(?:APPLICATION|PRAYER|PETITION|PLEA)"
            r".{0,100}(?:REJECTED|DISMISSED)|"
            r"(?:REJECTED|DISMISSED).{0,100}"
            r"(?:BAIL|ANTICIPATORY\s+BAIL)"
        ),
        (
            "PARTLY ALLOWED",
            r"(?:PARTLY|PARTIALLY)\s+ALLOWED"
        ),
        (
            "DISMISSED AS WITHDRAWN",
            r"DISMISSED\s+AS\s+WITHDRAWN|"
            r"DISMISSED\s+AS\s+WITHDRAWN\s+"
            r"(?:WITH\s+LIBERTY|TO)"
        ),
        (
            "WITHDRAWN",
            r"(?:APPLICATION|PETITION|APPEAL)\s+"
            r"(?:IS\s+)?(?:HEREBY\s+)?WITHDRAWN|"
            r"STANDS\s+WITHDRAWN"
        ),
        (
            "DISMISSED",
            r"(?:APPLICATION|PETITION|APPEAL|WRIT\s+PETITION)"
            r"\s+(?:IS\s+)?(?:HEREBY\s+)?DISMISSED|"
            r"STANDS\s+DISMISSED"
        ),
        (
            "REJECTED",
            r"(?:APPLICATION|PETITION|APPEAL|PRAYER)"
            r"\s+(?:IS\s+)?(?:HEREBY\s+)?REJECTED|"
            r"STANDS\s+REJECTED"
        ),
        (
            "ALLOWED",
            r"(?:APPLICATION|PETITION|APPEAL|WRIT\s+PETITION)"
            r"\s+(?:IS\s+)?(?:HEREBY\s+)?ALLOWED|"
            r"STANDS\s+ALLOWED"
        ),
        (
            "DISPOSED",
            r"(?:APPLICATION|PETITION|APPEAL|REVIEW\s+PETITIONS?)"
            r"\s+(?:IS|ARE)?\s*(?:HEREBY\s+)?"
            r"(?:STANDS\s+)?DISPOSED"
        )
    ]

    metadata["disposal_nature"] = ["UNCLASSIFIED"]
    metadata["decision_evidence"] = None

    for decision, pattern in patterns:

        matches = list(re.finditer(pattern, final_text, re.IGNORECASE))

        if matches:
            match = matches[-1]

            metadata["disposal_nature"] = [decision]

            start = max(0, match.start() - 180)
            end = min(len(final_text), match.end() + 180)

            metadata["decision_evidence"] = (
                final_text[start:end].strip()
            )

            break

    return metadata


def main():

    files = sorted(INPUT_DIR.glob("*.txt"))

    if not files:
        print("No extracted text files found.")
        return

    successful = 0

    for file in files:

        try:
            text = file.read_text(encoding="utf-8")

            metadata = extract_metadata(text)

            output_file = OUTPUT_DIR / f"{file.stem}.json"

            output_file.write_text(
                json.dumps(metadata, indent=4),
                encoding="utf-8"
            )

            print(f"Processed: {file.name}")
            print(f"Decision: {metadata['disposal_nature']}")
            print(f"Metadata saved: {output_file}")

            successful += 1

        except Exception as error:
            print(f"Failed: {file.name}")
            print(f"Error: {error}")

    print("\nMETADATA EXTRACTION COMPLETE")
    print(f"Successful: {successful}")
    print(f"Failed: {len(files) - successful}")


if __name__ == "__main__":
    main()
