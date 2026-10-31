
import pandas as pd

path = (
    "data/metadata/multi_court/year=2025/"
    "court=7_26/bench=dhcdb/metadata.parquet"
)

data = pd.read_parquet(path)

row = data[
    data["title"].astype(str).str.contains(
        "MDD MEDICAL SYSTEMS",
        case=False,
        na=False
    )
].iloc[0]

print("\nAVAILABLE FIELDS:")
for column in data.columns:
    value = str(row[column])
    print(f"\n{column}:")
    print(value[:1000])
