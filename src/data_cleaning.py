from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
file_path = BASE_DIR / "data" / "raw" / "IST-dataset.csv"

df = pd.read_csv(file_path)

# Columns to normalize
date_cols = ["startdate", "terdate", "defactoter"]

# Convert DD.MM.YYYY -> YYYY-MM
for col in date_cols:
    df[col] = (
        pd.to_datetime(
            df[col],
            format="%d.%m.%Y",
            errors="coerce"
        )
        .dt.strftime("%Y-%m")
    )


print(df[['startdate', 'terdate', 'defactoter']])


