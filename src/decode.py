import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
full_csv_path = BASE_DIR / "data" / "IST-dataset.csv"
country_code_csv_path = BASE_DIR / "docs" / "COW-country-codes.csv"




SENDER_ABBREV = {
    "united states of america"                                    : "USA",
    "european economic community - european community"            : "EEC",
    "european union"                                              : "EU",
    "pan american union"                                          : "OAS",
    "united nations"                                              : "UN",
    "commonwealth secretariat"                                    : "CommSec",
    "economic community of west african states"                   : "ECOWAS",
    "league of arab states"                                       : "LAS",
    "organization for african unity"                              : "OAU",
    "secretariat of the commission for east african cooperation"  : "EAC",
    "southern african development community"                      : "SADC",
    "union of the mediterranean"                                  : "UM",
}



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






