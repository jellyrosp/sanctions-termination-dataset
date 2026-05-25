# IST Sanctions Dataset

## Data Processing Pipeline Stages

This pipeline ingests the raw IST (International Sanctions Terminations) dataset in CSV format,
normalises its structure, and loads it into a relational SQLite database for downstream analysis.

---

### Source Data

- **File:** `data/IST-dataset.csv`
- **Format:** CSV, one row per sanction case
- **Origin:** IST dataset, combining and extending EUSANCT, TIES, and HSE datasets

Each row represents a sanction regime, identified by a `caseid` of the form `{SENDER}_{TARGET}_{YEAR}`
(e.g. `USA_CUB_58`). Several columns encode multiple values in a single cell using different
delimiters (commas, semicolons, slashes, or em-dashes), requiring normalisation before storage.

---


### 1. Loading and Basic Cleaning (`csv2sqlite.py`)

The raw CSV is loaded with all columns read as strings to avoid silent type coercions.
Column names are stripped of whitespace. The `outcome` column receives additional stripping
to remove trailing spaces found in the source data.

### 2. Type Normalisation

**Dates** — Three date columns (`startdate`, `terdate`, `defactoter`) are parsed from
`DD.MM.YYYY` format and stored as `YYYY-MM-DD` strings, with unparseable values stored as NULL.

**Booleans** — Eight columns encoding binary flags (`ongoing`, `gradual`, `expiry`, `review`,
`negotiations`, `instinvestment`, `sendersalience`, `targetsalience`) are cast to nullable
integers (0/1), with blank values stored as NULL.

### 3. Multi-valued Column Normalisation

Six columns contain multiple values per cell, each using a different delimiter:

| Column | Delimiter | Example |
|---|---|---|
| `sender` | comma | `1653, 1830` |
| `measures` | comma | `TE, CE, AE` |
| `goals` | comma | `DM, HR` |
| `outcome` | comma | `Negotiated settlement, Target complete acquiescence` |
| `multilateralism` | em-dash (` – `) | `EU – UN – USA – RO` |
| `datasets` | slash | `EUSANCT/TIES/HSE` |

Each column is split into individual tokens, which are used to populate dedicated lookup
tables and junction tables following a standard many-to-many pattern.

### 4. Decode Mapping

Abbreviated codes in `measures` and `goals` are expanded into human-readable labels
via static dictionaries (e.g. `"AE"` → `"arms embargo"`). Target country codes are
resolved to full country names using the Correlates of War (COW) state system reference
file (`COW-country-codes.csv`). Sender organisation codes are resolved via a manually
maintained dictionary, referencing the respective authoritative document (`IGO-Codebook_v3_short-copy.pdf`).

### 5. Database Schema

The SQLite database (`data/IST-dataset.db`) implements a fully normalised relational schema: