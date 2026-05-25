import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
full_csv_path = BASE_DIR / "data" / "IST-dataset.csv"
country_code_csv_path = BASE_DIR / "docs" / "COW-country-codes.csv"


def build_target_decod() -> dict:

    df = pd.read_csv(full_csv_path, dtype=str)

    target_values = set(
        token.strip()
        for cell in df["target"].dropna()
        for token in str(cell).split(",")
        if token.strip()
    )

    ref = pd.read_csv(country_code_csv_path, dtype=str).drop_duplicates(subset=["CCode"])

    mapping = (
        ref[ref["CCode"].isin(target_values)]
        .set_index("CCode")["StateNme"]
        .to_dict()
    )
    return mapping


