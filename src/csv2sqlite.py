"""
csv2sqlite.py
-----------
Reads the raw IST-dataset CSV, normalises every multi-valued / coded column,
and writes a fully-relational SQLite database that matches the ERD.

Tables created
--------------
  Core entity   : Case
  Lookup tables : Outcome, Sender, Target, Measure, Goal,
                  Multilateralism, Dataset
  Junction tbls : Case_Outcome, Case_Sender, Case_Target,
                  Case_Measure, Case_Goal, Case_Multilateralism,
                  Case_Dataset
"""

import re
import sqlite3
from pathlib import Path
import decode
import pandas as pd

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
file_path = BASE_DIR / "data" / "IST-dataset.csv"
db_path   = BASE_DIR / "data" / "IST-dataset.db"

# ---------------------------------------------------------------------------
# 1. Load & basic cleaning
# ---------------------------------------------------------------------------
df = pd.read_csv(file_path, dtype=str).fillna("")




# Normalise column names: strip whitespace
df.columns = df.columns.str.strip()

# Strip trailing/leading whitespace from all string columns
df = df.apply(lambda col: col.str.strip() if col.dtype == object else col)

# ---------------------------------------------------------------------------
# 2. Date normalisation  DD.MM.YYYY → YYYY-MM-DD
# ---------------------------------------------------------------------------
date_cols = ["startdate", "terdate", "defactoter"]
for col in date_cols:
    df[col] = (
        pd.to_datetime(df[col], format="%d.%m.%Y", errors="coerce")
        .dt.strftime("%Y-%m-%d")
    )

# ---------------------------------------------------------------------------
# 3. Boolean columns  ("0"/"1" → 0/1 int, blank → NULL)
# ---------------------------------------------------------------------------
bool_cols = [
    "ongoing", "gradual", "expiry", "review",
    "negotiations", "instinvestment",
    "targetsalience", "sendersalience",
]
for col in bool_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

# ---------------------------------------------------------------------------
# 4. Helper: split a delimited cell into a clean list of tokens
# ---------------------------------------------------------------------------
def split_cell(value) -> list[str]:
    """Split on commas or semicolons, strip whitespace and quotes."""
    if pd.isna(value):
        return []
    tokens = re.split(r"[;,]", str(value))
    return [t.strip().strip('"').strip("'") for t in tokens if t.strip()]


# Multilateralism handling of multi-valued column
def split_multilat(value: str) -> list[str]:
    tokens = re.split(r"\s*–\s*", value)
    return [t.strip() for t in tokens if t.strip()]


multilat_records = []
for _, row in df.iterrows():
    for token in split_multilat(row["multilateralism"]):
        if token:
            multilat_records.append({
                "case_id"           : row["caseid"],
                "multilateralism_id": token,
            })

case_multilat = pd.DataFrame(multilat_records).drop_duplicates()

multilat_lookup = pd.DataFrame(
    {"multilateralism_id": sorted(case_multilat["multilateralism_id"].unique())}
)    


# Datasets handling of multi-valued column
def split_dataset(value: str) -> list[str]:
    tokens = value.split("/")
    return [t.strip() for t in tokens if t.strip()]


dataset_records = []
for _, row in df.iterrows():
    for token in split_dataset(row["datasets"]):
        if token:
            dataset_records.append({
                "case_id"   : row["caseid"],
                "dataset_id": token,
            })

case_dataset = pd.DataFrame(dataset_records).drop_duplicates()

dataset_lookup = pd.DataFrame(
    {"dataset_id": sorted(case_dataset["dataset_id"].unique())}
)



# ---------------------------------------------------------------------------
# 5. Build lookup + junction dataframes for every multi-valued column
# ---------------------------------------------------------------------------

def build_lookup_and_junction(
    df: pd.DataFrame,
    case_col: str,
    csv_col: str,
    id_col: str,
    decod_map: dict | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Parse a column where cells may contain comma-separated codes.
    Returns (lookup_df, junction_df).
    lookup_df  columns: [id_col] or [id_col, "decod"] if decod_map provided
    junction_df columns: ["case_id", id_col]
    """
    records = []
    for _, row in df.iterrows():
        case_id = row[case_col]
        for token in split_cell(row[csv_col]):
            if token:
                records.append({"case_id": case_id, id_col: token})

    junction = pd.DataFrame(records).drop_duplicates()
    all_ids  = junction[id_col].unique()

    lookup_rows = []
    for uid in sorted(all_ids):
        if decod_map is not None:
            decod = decod_map.get(uid, uid)
            lookup_rows.append({id_col: uid, "decod": decod})
        else:
            lookup_rows.append({id_col: uid})

    lookup = pd.DataFrame(lookup_rows)
    return lookup, junction


# ── Sender ─────────────────────────────────────────────────────────────────
SENDER_DECOD = {
    "2"    : "united states of america",
    "1653" : "european economic community - european community",
    "1830" : "european union",
    "3900" : "pan american union",
    "4400" : "united nations",
    "1240": "commonwealth secretariat",
    "1520": "economic community of west african states",
    "3450": "league of arab states",
    "3760": "organization for african unity",
    "4120": "secretariat of the commission for east african cooperation",
    "4250": "southern african development community",
    "4375": "union of the mediterranean",
}    

sender_lookup, case_sender = build_lookup_and_junction(
    df, "caseid", "sender", "sender_id", SENDER_DECOD
)


# ── Target ─────────────────────────────────────────────────────────────────
TARGET_DECOD = decode.build_target_decod()

target_lookup, case_target = build_lookup_and_junction(
    df, "caseid", "target", "target_id", TARGET_DECOD
)


# ── Outcome ──────────────────────────────────────────────────────────────────
# Normalize "Blank" to NULL in the outcome column
df["outcome"] = df["outcome"].str.strip()
df["outcome"] = df["outcome"].replace("Blank", pd.NA)

outcome_lookup, case_outcome = build_lookup_and_junction(
    df, "caseid", "outcome", "outcome_type"
)


# ── Measure ─────────────────────────────────────────────────────────────────
MEASURE_DECOD = {
    "DS": "diplomatic sanctions",
    "TE": "comprehensive trade embargo",
    "CE": "commodity embargo",
    "AE": "arms embargo",
    "AS": "Aid sanctions",
    "FS": "financial sanctions",
    "AF": "asset freeze",
    "TB": "travel ban",
    "IM": "interruption of military cooperation",
    "OE": "oil embargo",
    "FB": "flight ban",
}

measure_lookup, case_measure = build_lookup_and_junction(
    df, "caseid", "measures", "measure_id", MEASURE_DECOD
)

# ── Goal ─────────────────────────────────────────────────────────────────────
GOAL_DECOD = {
    "DM": "democracy support",
    "HR": "support human rights",
    "AC": "address armed conflict",
    "NP": "nuclear non-proliferation",
    "WM": "stop proliferation or usage of weapons of mass destructio",
    "CT": "counter-terrorism",
    "DT": "stop drug trafficking",
    "CB": "address convention breach",
    "other": "other"
    
}

# Normalize "Other" to "other" in the goals column
goal_records = []
for _, row in df.iterrows():
    adapt = int(row["adaptgoal"]) if row["adaptgoal"] in ("0", "1") else None
    for token in split_cell(row["goals"]):
        if token:
            # Normalize all variations of "Other" to "other"
            normalized_token = "other" if token.strip().lower() == "other" else token
            goal_records.append({
                "case_id": row["caseid"],
                "goal_id": normalized_token,
                "adapt_goal": adapt,
            })

case_goal = pd.DataFrame(goal_records).drop_duplicates(subset=["case_id", "goal_id"])

goal_lookup = pd.DataFrame([
    {"goal_id": gid, "decod": GOAL_DECOD.get(gid, gid)}
    for gid in sorted(case_goal["goal_id"].unique())
])



# ---------------------------------------------------------------------------
# 6. Build the main Case table (scalar columns only)
# ---------------------------------------------------------------------------
case_df = df[[
    "caseid", "startdate", "terdate", "defactoter",
    "ongoing", "gradual", "expiry", "review",
    "requirementter", "negotiations", "comment",
    "sourceimp", "sourceter",
    "sendersalience", "costsender", "instinvestment",
    "targetsalience", "costtarget",
]].copy()

# Strip whitespace from requirementter to normalize "Clear " to "Clear" and "missing" to NULL
case_df["requirementter"] = case_df["requirementter"].str.strip()
case_df["requirementter"] = case_df["requirementter"].replace("missing", pd.NA)

# Normalize "Blank" to NULL in the cost_sender column
case_df["costsender"] = case_df["costsender"].str.strip()
case_df["costsender"] = case_df["costsender"].replace("Blank", pd.NA)

# Normalize all empty sourceimp cells with NULL
case_df["sourceter"] = case_df["sourceter"].str.strip()
case_df["sourceter"] = case_df["sourceter"].replace(r"^\s*$", pd.NA, regex=True)

# Normalize all empty comment cells with NULL
case_df["comment"] = case_df["comment"].str.strip()
case_df["comment"] = case_df["comment"].replace(r"^\s*$", pd.NA, regex=True)

case_df = case_df.rename(columns={
    "caseid"        : "case_id",
    "startdate"     : "start_date",
    "terdate"       : "ter_date",
    "defactoter"    : "de_facto_ter",
    "requirementter": "requirement_termination",
    "sourceimp": "source_imp",
    "sourceter": "source_ter",
    "sendersalience": "sender_salience",
    "costsender"    : "cost_sender",
    "instinvestment": "inst_investment",
    "targetsalience": "target_salience",
    "costtarget"    : "cost_target",
})

# ---------------------------------------------------------------------------
# 7. Write to SQLite
# ---------------------------------------------------------------------------
db_path.parent.mkdir(parents=True, exist_ok=True)
con = sqlite3.connect(db_path)
cur = con.cursor()

cur.executescript("""
PRAGMA foreign_keys = ON;

-- Lookup tables -------------------------------------------------------
CREATE TABLE IF NOT EXISTS Outcome (
    outcome_type TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS Sender (
    sender_id TEXT PRIMARY KEY,
    decod     TEXT
);

CREATE TABLE IF NOT EXISTS Target (
    target_id TEXT PRIMARY KEY,
    decod     TEXT
);

CREATE TABLE IF NOT EXISTS Measure (
    measure_id TEXT PRIMARY KEY,
    decod      TEXT
);

CREATE TABLE IF NOT EXISTS Goal (
    goal_id TEXT PRIMARY KEY,
    decod   TEXT
);

CREATE TABLE IF NOT EXISTS Multilateralism (
    multilateralism_id TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS Dataset (
    dataset_id TEXT PRIMARY KEY
);

-- Core case table -----------------------------------------------------
CREATE TABLE IF NOT EXISTS RegimeCase (
    case_id                 TEXT PRIMARY KEY,
    start_date              TEXT,
    ter_date                TEXT,
    de_facto_ter            TEXT,
    ongoing                 INTEGER,
    gradual                 INTEGER,
    expiry                  INTEGER,
    review                  INTEGER,
    requirement_termination TEXT,
    negotiations            INTEGER,
    comment                 TEXT,
    source_imp              TEXT,
    source_ter              TEXT,
    sender_salience         INTEGER,
    cost_sender             TEXT,
    inst_investment         INTEGER,
    target_salience         INTEGER,
    cost_target             TEXT
);

-- Junction tables -----------------------------------------------------
CREATE TABLE IF NOT EXISTS Case_Outcome (
    case_id      TEXT REFERENCES RegimeCase(case_id),
    outcome_type TEXT REFERENCES Outcome(outcome_type),
    PRIMARY KEY (case_id, outcome_type)
);

CREATE TABLE IF NOT EXISTS Case_Sender (
    case_id   TEXT REFERENCES RegimeCase(case_id),
    sender_id TEXT REFERENCES Sender(sender_id),
    PRIMARY KEY (case_id, sender_id)
);

CREATE TABLE IF NOT EXISTS Case_Target (
    case_id   TEXT REFERENCES RegimeCase(case_id),
    target_id TEXT REFERENCES Target(target_id),
    PRIMARY KEY (case_id, target_id)
);

CREATE TABLE IF NOT EXISTS Case_Measure (
    case_id    TEXT REFERENCES RegimeCase(case_id),
    measure_id TEXT REFERENCES Measure(measure_id),
    PRIMARY KEY (case_id, measure_id)
);

CREATE TABLE IF NOT EXISTS Case_Goal (
    case_id     TEXT REFERENCES RegimeCase(case_id),
    goal_id     TEXT REFERENCES Goal(goal_id),
    adapt_goal  INTEGER,
    PRIMARY KEY (case_id, goal_id)
);

CREATE TABLE IF NOT EXISTS Case_Multilateralism (
    case_id            TEXT REFERENCES RegimeCase(case_id),
    multilateralism_id TEXT REFERENCES Multilateralism(multilateralism_id),
    PRIMARY KEY (case_id, multilateralism_id)
);

CREATE TABLE IF NOT EXISTS Case_Dataset (
    case_id    TEXT REFERENCES RegimeCase(case_id),
    dataset_id TEXT REFERENCES Dataset(dataset_id),
    PRIMARY KEY (case_id, dataset_id)
);
""")
con.commit()

# ---------------------------------------------------------------------------
# 8. Insert data
# ---------------------------------------------------------------------------
def insert(df: pd.DataFrame, table: str, con: sqlite3.Connection):
    if df.empty:
        return
    # Convert pandas NA/NaT to None for SQLite compatibility
    df = df.astype(object).where(pd.notna(df), None)
    placeholders = ", ".join("?" * len(df.columns))
    cols = ", ".join(df.columns)
    sql = f"INSERT OR IGNORE INTO {table} ({cols}) VALUES ({placeholders})"
    con.executemany(sql, df.itertuples(index=False, name=None))
    con.commit()

# Lookups first (referenced by FKs)
insert(outcome_lookup,  "Outcome",          con)
insert(sender_lookup,   "Sender",           con)
insert(target_lookup,   "Target",           con)
insert(measure_lookup,  "Measure",          con)
insert(goal_lookup,     "Goal",             con)
insert(multilat_lookup, "Multilateralism",  con)
insert(dataset_lookup,  "Dataset",          con)

# Core case table
insert(case_df, "RegimeCase", con)

# Junction tables
insert(case_outcome, "Case_Outcome",         con)
insert(case_sender,  "Case_Sender",          con)
insert(case_target,  "Case_Target",          con)
insert(case_measure, "Case_Measure",         con)
insert(case_goal,    "Case_Goal",            con)
insert(case_multilat,"Case_Multilateralism", con)
insert(case_dataset, "Case_Dataset",         con)

con.close()

# ---------------------------------------------------------------------------
# 9. Quick verification
# ---------------------------------------------------------------------------
con = sqlite3.connect(db_path)
tables = [
    "RegimeCase", "Outcome", "Sender", "Target", "Measure",
    "Goal", "Multilateralism", "Dataset",
    "Case_Outcome", "Case_Sender", "Case_Target",
    "Case_Measure", "Case_Goal", "Case_Multilateralism", "Case_Dataset",
]
print(f"\nDatabase written to: {db_path}\n")
print(f"{'Table':<25} {'Rows':>6}")
print("-" * 33)
for t in tables:
    n = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"{t:<25} {n:>6}")
con.close()
print("\nDone.")