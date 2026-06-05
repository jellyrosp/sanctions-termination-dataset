import sqlite3
from pathlib import Path
import sys

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Project root: 3 levels up from this file
BASE_DIR = Path(__file__).resolve().parent.parent.parent
src_dir = BASE_DIR / "src"

# Add src to sys.path so `import decode` works
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import decode

# Connect to the database using the same BASE_DIR
con = sqlite3.connect(BASE_DIR / "data" / "IST-dataset.db")




def query(sql: str, con: sqlite3.Connection) -> pd.DataFrame:
    """Execute SQL and return results as a DataFrame."""
    return pd.read_sql_query(sql, con)    


def get_termination_by_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Contingency table of sanction regimes by sender and termination type.

    Multi-sender cases are collapsed at the case level in pandas:
    - (EEC, EU) is treated as 'EEC & EU'

    Then contingency table is built on cleaned sender categories.
    """

    sql = """
        SELECT
            rc.case_id,
            s.decod AS sender,

            rc.ter_date,
            rc.de_facto_ter,
            rc.ongoing

        FROM RegimeCase rc
        JOIN Case_Sender cs ON rc.case_id = cs.case_id
        JOIN Sender s       ON cs.sender_id = s.sender_id

        WHERE rc.ter_date IS NOT NULL
           OR rc.de_facto_ter IS NOT NULL
           OR rc.ongoing = 1
    """

    df = query(sql, con)

    # --- collapse multi-sender at CASE level ---
    sender_per_case = (
        df.groupby("case_id")["sender"]
          .apply(lambda x: "EEC & EU" if set(x) == {
              "european economic community - european community",
              "european union"
          } else x.iloc[0])
    )

    df = df.drop_duplicates("case_id").copy()
    df["sender"] = df["case_id"].map(sender_per_case)

    # --- termination classification ---
    def classify(row):
        if pd.notnull(row["ter_date"]) and pd.notnull(row["de_facto_ter"]):
            return "De iure & de facto"
        elif pd.notnull(row["ter_date"]):
            return "De iure"
        elif pd.notnull(row["de_facto_ter"]):
            return "De facto"
        else:
            return "Ongoing"

    df["termination"] = df.apply(classify, axis=1)

    # --- map sender labels (as in your duration function) ---
    df["sender"] = df["sender"].map(
        lambda x: decode.SENDER_ABBREV.get(x, x)
    )

    # --- contingency table ---
    ct = (
        df.groupby(["sender", "termination"])
          .size()
          .unstack(fill_value=0)
    )

    count_cols = [
        "De iure & de facto",
        "De iure",
        "De facto",
        "Ongoing",
    ]

    ct = ct.reindex(columns=count_cols, fill_value=0)
    ct["Total"] = ct.sum(axis=1)

    # --- TOTAL row ---
    total = ct.sum()
    ct = pd.concat([ct, total.to_frame().T])
    ct = ct.rename(index={0: "TOTAL"})
    ct.index.name = "Sender"

    # --- relative frequencies ---
    rel = ct[count_cols].div(ct["Total"], axis=0).mul(100).round(1)

    # --- multi-index output ---
    result = pd.DataFrame(index=ct.index)

    for c in count_cols:
        result[(c, "Abs.")] = ct[c]
        result[(c, "Rel(%)")] = rel[c]

    result[("Total", "")] = ct["Total"]

    result.columns = pd.MultiIndex.from_tuples(result.columns)

    return result
#print(get_termination_by_sender(con))


def get_duration_by_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Contingency table of sanction regimes by sender and duration interval.

    Multi-sender cases are collapsed at case level:
    - (EEC, EU) → "EEC & EU"

    Duration is computed from start_date to ter_date,
    or to 2018-12-31 for ongoing cases.
    """

    sql = """
    SELECT
        rc.case_id,
        rc.start_date,

        CASE
            WHEN rc.ongoing = 1 THEN '2018-12-31'
            ELSE rc.ter_date
        END AS end_date,

        cs.sender_id,
        s.decod AS sender

    FROM RegimeCase rc
    JOIN Case_Sender cs ON rc.case_id = cs.case_id
    JOIN Sender s       ON cs.sender_id = s.sender_id

    WHERE rc.start_date IS NOT NULL
      AND (rc.ter_date IS NOT NULL OR rc.ongoing = 1)
    """

    df = query(sql, con)

    # --- collapse sender at CASE level ---
    sender_per_case = (
        df.groupby("case_id")["sender"]
          .apply(lambda x: "EEC & EU" if set(x) == {
              "european economic community - european community",
              "european union"
          } else x.iloc[0])
    )

    df = df.drop_duplicates("case_id").copy()
    df["sender"] = df["case_id"].map(sender_per_case)

    # --- compute duration ---
    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
    df["end_date"]   = pd.to_datetime(df["end_date"], errors="coerce")

    df["months"] = (
        (df["end_date"].dt.year - df["start_date"].dt.year) * 12 +
        (df["end_date"].dt.month - df["start_date"].dt.month)
    )

    # --- intervals ---
    bins = [0, 6, 12, 24, 60, 120, 240, float("inf")]
    labels = ["0–6m", "6m–1y", "1–2y", "2–5y", "5–10y", "10–20y", "20+y"]

    df["interval"] = pd.cut(df["months"], bins=bins, labels=labels, right=False)

    # --- map sender labels ---
    df["sender"] = df["sender"].map(
        lambda x: decode.SENDER_ABBREV.get(x, x)
    )

    # --- contingency table ---
    ct = (
        df.groupby(["sender", "interval"])
          .size()
          .unstack(fill_value=0)
    )

    ct = ct.reindex(columns=labels, fill_value=0)

    ct["Total"] = ct.sum(axis=1)

    total = ct.sum()
    ct = pd.concat([ct, total.to_frame().T])
    ct = ct.rename(index={0: "TOTAL"})
    ct.index.name = "Sender"

    # --- relative frequencies ---
    rel = ct[labels].div(ct["Total"], axis=0).mul(100).round(1)

    # --- output format ---
    result = pd.DataFrame(index=ct.index)

    for c in labels:
        result[(c, "Abs.")] = ct[c]
        result[(c, "Rel(%)")] = rel[c]

    result[("Total", "")] = ct["Total"]

    result.columns = pd.MultiIndex.from_tuples(result.columns)

    return result
#print(get_duration_by_sender(con))


def get_gradual_by_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Contingency table of sanction regimes by sender and termination modality.

    Sender is collapsed at case level:
    - (EEC, EU) → "EEC & EU"

    Termination modality:
    - gradual (1)
    - not gradual (0)
    - missing (NULL)
    """

    sql = """
    SELECT
        rc.case_id,
        rc.gradual,
        s.decod AS sender
    FROM RegimeCase rc
    JOIN Case_Sender cs ON rc.case_id = cs.case_id
    JOIN Sender s       ON cs.sender_id = s.sender_id
    WHERE rc.gradual IS NOT NULL OR rc.gradual IS NULL
    """

    df = query(sql, con)

    # --- collapse sender at case level ---
    sender_per_case = (
        df.groupby("case_id")["sender"]
          .apply(
              lambda x: "EEC & EU"
              if set(x) == {
                  "european economic community - european community",
                  "european union"
              }
              else x.iloc[0]
          )
    )

    df = df.drop_duplicates("case_id").copy()
    df["sender"] = df["case_id"].map(sender_per_case)

    # --- map sender labels ---
    df["sender"] = df["sender"].map(
        lambda x: decode.SENDER_ABBREV.get(x, x)
    )

    # --- classify gradual with missing category ---
    def classify(x):
        if x == 1:
            return "Gradual"
        elif x == 0:
            return "Not Gradual"
        else:
            return "Missing"

    df["modality"] = df["gradual"].apply(classify)

    # --- contingency table ---
    ct = (
        df.groupby(["sender", "modality"])
          .size()
          .unstack(fill_value=0)
    )

    # enforce stable column order
    cols = ["Gradual", "Not Gradual", "Missing"]
    ct = ct.reindex(columns=cols, fill_value=0)

    ct["Total"] = ct.sum(axis=1)

    # --- TOTAL row ---
    total = ct.sum()
    ct = pd.concat([ct, total.to_frame().T])
    ct = ct.rename(index={0: "TOTAL"})
    ct.index.name = "Sender"

    # --- relative frequencies ---
    rel = ct[cols].div(ct["Total"], axis=0).mul(100).round(1)

    # --- MultiIndex output ---
    result = pd.DataFrame(index=ct.index)

    for c in cols:
        result[(c, "Abs.")] = ct[c]
        result[(c, "Rel(%)")] = rel[c]

    result[("Total", "")] = ct["Total"]

    result.columns = pd.MultiIndex.from_tuples(result.columns)

    return result
#print(get_gradual_by_sender(con))    


def get_expiry_by_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Contingency table of sanction regimes by sender and expiry condition.

    Sender is collapsed at case level:
    - (EEC, EU) → "EEC & EU"

    Expiry categories:
    - stipulated (1)
    - not stipulated (0)
    - missing (NULL)
    """

    sql = """
    SELECT
        rc.case_id,
        rc.expiry,
        s.decod AS sender
    FROM RegimeCase rc
    JOIN Case_Sender cs ON rc.case_id = cs.case_id
    JOIN Sender s       ON cs.sender_id = s.sender_id
    WHERE rc.expiry IS NOT NULL OR rc.expiry IS NULL
    """

    df = query(sql, con)

    # --- collapse sender at case level ---
    sender_per_case = (
        df.groupby("case_id")["sender"]
          .apply(
              lambda x: "EEC & EU"
              if set(x) == {
                  "european economic community - european community",
                  "european union"
              }
              else x.iloc[0]
          )
    )

    df = df.drop_duplicates("case_id").copy()
    df["sender"] = df["case_id"].map(sender_per_case)

    # --- map sender labels ---
    df["sender"] = df["sender"].map(
        lambda x: decode.SENDER_ABBREV.get(x, x)
    )

    # --- classify expiry ---
    def classify(x):
        if x == 1:
            return "Stipulated expiry date"
        elif x == 0:
            return "Not stipulated expiry date"
        else:
            return "Missing"

    df["expiry_cat"] = df["expiry"].apply(classify)

    # --- contingency table ---
    ct = (
        df.groupby(["sender", "expiry_cat"])
          .size()
          .unstack(fill_value=0)
    )

    cols = [
        "Stipulated expiry date",
        "Not stipulated expiry date",
        "Missing"
    ]

    ct = ct.reindex(columns=cols, fill_value=0)

    ct["Total"] = ct.sum(axis=1)

    # --- TOTAL row ---
    total = ct.sum()
    ct = pd.concat([ct, total.to_frame().T])
    ct = ct.rename(index={0: "TOTAL"})
    ct.index.name = "Sender"

    # --- relative frequencies ---
    rel = ct[cols].div(ct["Total"], axis=0).mul(100).round(1)

    # --- MultiIndex output ---
    result = pd.DataFrame(index=ct.index)

    for c in cols:
        result[(c, "Abs.")] = ct[c]
        result[(c, "Rel(%)")] = rel[c]

    result[("Total", "")] = ct["Total"]

    result.columns = pd.MultiIndex.from_tuples(result.columns)

    return result
#print(get_expiry_by_sender(con))    


def get_review_by_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Contingency table of sanction regimes by sender and review regulation.

    Sender is collapsed at case level:
    - (EEC, EU) → "EEC & EU"

    Review categories:
    - has review regulation (1)
    - lacks review regulation (0)
    - missing (NULL)
    """

    sql = """
    SELECT
        rc.case_id,
        rc.review,
        s.decod AS sender
    FROM RegimeCase rc
    JOIN Case_Sender cs ON rc.case_id = cs.case_id
    JOIN Sender s       ON cs.sender_id = s.sender_id
    WHERE rc.review IS NOT NULL OR rc.review IS NULL
    """

    df = query(sql, con)

    # --- collapse sender at case level ---
    sender_per_case = (
        df.groupby("case_id")["sender"]
          .apply(
              lambda x: "EEC & EU"
              if set(x) == {
                  "european economic community - european community",
                  "european union"
              }
              else x.iloc[0]
          )
    )

    df = df.drop_duplicates("case_id").copy()
    df["sender"] = df["case_id"].map(sender_per_case)

    # --- map sender labels ---
    df["sender"] = df["sender"].map(
        lambda x: decode.SENDER_ABBREV.get(x, x)
    )

    # --- classify review ---
    def classify(x):
        if x == 1:
            return "Has review regulation"
        elif x == 0:
            return "Lacks review regulation"
        else:
            return "Missing"

    df["review_cat"] = df["review"].apply(classify)

    # --- contingency table ---
    ct = (
        df.groupby(["sender", "review_cat"])
          .size()
          .unstack(fill_value=0)
    )

    cols = [
        "Has review regulation",
        "Lacks review regulation",
        "Missing"
    ]

    ct = ct.reindex(columns=cols, fill_value=0)

    ct["Total"] = ct.sum(axis=1)

    # --- TOTAL row ---
    total = ct.sum()
    ct = pd.concat([ct, total.to_frame().T])
    ct = ct.rename(index={0: "TOTAL"})
    ct.index.name = "Sender"

    # --- relative frequencies ---
    rel = ct[cols].div(ct["Total"], axis=0).mul(100).round(1)

    # --- MultiIndex output ---
    result = pd.DataFrame(index=ct.index)

    for c in cols:
        result[(c, "Abs.")] = ct[c]
        result[(c, "Rel(%)")] = rel[c]

    result[("Total", "")] = ct["Total"]

    result.columns = pd.MultiIndex.from_tuples(result.columns)

    return result
#print(get_review_by_sender(con))    


def get_measure_distribution(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Frequency distribution of sanction regimes by applied measure.
    Relative frequency is computed over the total number of RegimeCase rows.
    """
    sql = """
        SELECT
            m.measure_id AS measure,
            COUNT(DISTINCT cm.case_id) AS n_cases
        FROM Case_Measure cm
        JOIN Measure m ON cm.measure_id = m.measure_id
        GROUP BY m.measure_id
        ORDER BY n_cases DESC
    """
    df = query(sql, con)
    df.columns = ["Measure", "Case Frq"]
    df = df.set_index("Measure")

    return df
#print(get_measure_frequency(con))    


def get_measure_by_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Contingency table of sanction regimes by sender and measure combinations.

    Both sender and measure are collapsed at case level:
    - sender: (EEC, EU) → "EEC & EU"
    - measure: sorted unique set per case
    - absolute frequency >= 7

    Ensures one observation per regime case.
    """

    sender_sql = """
    SELECT cs.case_id, s.decod AS sender
    FROM Case_Sender cs
    JOIN Sender s ON cs.sender_id = s.sender_id
    """

    measure_sql = """
    SELECT cm.case_id, m.measure_id AS measure
    FROM Case_Measure cm
    JOIN Measure m ON cm.measure_id = m.measure_id
    """

    sender_df = query(sender_sql, con)
    measure_df = query(measure_sql, con)

    # --- collapse sender at case level ---
    sender_grouped = (
        sender_df.groupby("case_id")["sender"]
        .apply(lambda x: "EEC & EU" if set(x) == {
            "european economic community - european community",
            "european union"
        } else x.iloc[0])
        .reset_index(name="sender_combo")
    )

    sender_grouped["sender_combo"] = sender_grouped["sender_combo"].map(
        lambda x: decode.SENDER_ABBREV.get(x, x)
    )

    # --- collapse measure at case level (IMPORTANT FIX) ---
    measure_grouped = (
        measure_df.groupby("case_id")["measure"]
        .apply(lambda x: " & ".join(sorted(set(x))))
        .reset_index(name="measure_combo")
    )

    # --- merge CASE-level tables (now safe) ---
    df = sender_grouped.merge(measure_grouped, on="case_id")

    # --- contingency table ---
    ct = (
        df.groupby(["sender_combo", "measure_combo"])
        .size()
        .unstack(fill_value=0)
    )

    ct.index.name = "Sender"

    ct["Total"] = ct.sum(axis=1)

    # --- filter rare measure combos ---
    measure_cols = [c for c in ct.columns if c != "Total"]
    keep_cols = [c for c in measure_cols if ct[c].sum() >= 7]

    ct = ct[keep_cols + ["Total"]]

    # --- total row ---
    total = ct.sum()
    ct = pd.concat([ct, total.to_frame().T])
    ct = ct.rename(index={0: "TOTAL"})

    # --- relative frequencies ---
    rel = ct[keep_cols].div(ct["Total"], axis=0).mul(100).round(1)

    # --- MultiIndex output ---
    result = pd.DataFrame(index=ct.index)

    for c in keep_cols:
        result[(c, "Abs.")] = ct[c]
        result[(c, "Rel(%)")] = rel[c]

    result[("Total", "")] = ct["Total"]

    result.columns = pd.MultiIndex.from_tuples(result.columns)

    return result
#print(get_measure_by_sender(con))    


def get_measure_count_by_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Frequency distribution of sanction regimes by sender and number of measures.

    Measures are NOT treated as categories but as cardinality per case:
    - x ≤ 2
    - 2 < x ≤ 5
    - 5 < x ≤ 8
    - 8 < x ≤ 11
    """

    sender_sql = """
    SELECT cs.case_id, s.decod AS sender
    FROM Case_Sender cs
    JOIN Sender s ON cs.sender_id = s.sender_id
    """

    measure_sql = """
    SELECT cm.case_id, cm.measure_id
    FROM Case_Measure cm
    """

    sender_df = query(sender_sql, con)
    measure_df = query(measure_sql, con)

    # --- sender collapse (case-level) ---
    sender_grouped = (
        sender_df.groupby("case_id")["sender"]
        .apply(lambda x: "EEC & EU" if set(x) == {
            "european economic community - european community",
            "european union"
        } else x.iloc[0])
        .reset_index(name="sender_combo")
    )

    sender_grouped["sender_combo"] = sender_grouped["sender_combo"].map(
        lambda x: decode.SENDER_ABBREV.get(x, x)
    )

    # --- measure count per case ---
    measure_counts = (
        measure_df.groupby("case_id")
        .size()
        .reset_index(name="n_measures")
    )

    # --- merge case-level data ---
    df = sender_grouped.merge(measure_counts, on="case_id", how="left")

    # cases with no measures → 0
    df["n_measures"] = df["n_measures"].fillna(0).astype(int)

    # --- binning ---
    bins = [-float("inf"), 2, 5, 8, 11]
    labels = ["≤2", "3–5", "6–8", "9–11"]

    df["measure_bin"] = pd.cut(
        df["n_measures"],
        bins=bins,
        labels=labels,
        right=True,
        include_lowest=True
    )

    # --- contingency table ---
    ct = (
        df.groupby(["sender_combo", "measure_bin"])
        .size()
        .unstack(fill_value=0)
    )

    ct = ct.reindex(columns=labels, fill_value=0)

    ct["Total"] = ct.sum(axis=1)

    # --- total row ---
    total = ct.sum()
    ct = pd.concat([ct, total.to_frame().T])
    ct = ct.rename(index={0: "TOTAL"})
    ct.index.name = "Sender"

    # --- relative frequencies ---
    rel = ct[labels].div(ct["Total"], axis=0).mul(100).round(1)

    # --- MultiIndex output ---
    result = pd.DataFrame(index=ct.index)

    for c in labels:
        result[(c, "Abs.")] = ct[c]
        result[(c, "Rel(%)")] = rel[c]

    result[("Total", "")] = ct["Total"]

    result.columns = pd.MultiIndex.from_tuples(result.columns)

    return result
#print(get_measure_count_by_sender(con))    


def get_goal_distribution(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Frequency distribution of sanction regimes by exact number of goals per case.

    Categories:
    =1, =2, =3, =4, =5, =6
    Includes correct TOTAL row.
    """

    goal_sql = """
    SELECT case_id, goal_id
    FROM Case_Goal
    """

    df = query(goal_sql, con)

    goal_counts = (
        df.groupby("case_id")
        .size()
        .reset_index(name="n_goals")
    )

    cases_sql = """
    SELECT case_id FROM RegimeCase
    """

    cases = query(cases_sql, con)

    df_cases = cases.merge(goal_counts, on="case_id", how="left")
    df_cases["n_goals"] = df_cases["n_goals"].fillna(0).astype(int)

    grand_total = len(df_cases)

    df_vis = df_cases[df_cases["n_goals"].between(1, 6)]

    ct = (
        df_vis.groupby("n_goals")
        .size()
        .reindex(range(1, 7), fill_value=0)
    )

    rel = (ct / grand_total * 100).round(1)

    # --- build result with correct alignment ---
    index = [str(i) for i in range(1, 7)]

    result = pd.DataFrame(index=index)

    result[("Goals", "Abs.")] = ct.reindex(range(1, 7)).values
    result[("Goals", "Rel(%)")] = rel.reindex(range(1, 7)).values

    total_row = pd.DataFrame(
        {
            ("Goals", "Abs."): [ct.sum()],
            ("Goals", "Rel(%)"): [100.0],
        },
        index=["TOTAL"]
    )

    result = pd.concat([result, total_row])

    result.columns = pd.MultiIndex.from_tuples(result.columns)

    return result
#print(get_goal_distribution(con))    


def get_goal_count_by_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Frequency distribution of sanction regimes by sender and number of goals.

    Goals are NOT treated as categories but as cardinality per case:
    - x = 1
    - x = 2
    - x = 3
    - x = 4
    - x = 5
    - x = 6
    """

    sender_sql = """
    SELECT cs.case_id, s.decod AS sender
    FROM Case_Sender cs
    JOIN Sender s ON cs.sender_id = s.sender_id
    """

    goal_sql = """
    SELECT cg.case_id, cg.goal_id
    FROM Case_Goal cg
    """

    sender_df = query(sender_sql, con)
    goal_df = query(goal_sql, con)

    # --- sender collapse (case-level) ---
    sender_grouped = (
        sender_df.groupby("case_id")["sender"]
        .apply(lambda x: "EEC & EU" if set(x) == {
            "european economic community - european community",
            "european union"
        } else x.iloc[0])
        .reset_index(name="sender_combo")
    )

    sender_grouped["sender_combo"] = sender_grouped["sender_combo"].map(
        lambda x: decode.SENDER_ABBREV.get(x, x)
    )

    # --- goal count per case ---
    goal_counts = (
        goal_df.groupby("case_id")
        .size()
        .reset_index(name="n_goals")
    )

    # --- merge case-level data ---
    df = sender_grouped.merge(goal_counts, on="case_id", how="left")

    # cases with no goals → 0
    df["n_goals"] = df["n_goals"].fillna(0).astype(int)

    # --- binning ---
    # Define bins for exact goal counts (2, 3, 4, 5, 6, 7)
    bins = [1, 2, 3, 4, 5, 6, 7]  # 7 edges → 6 bins
    labels = ["1", "2", "3", "4", "5", "6"]  # 6 labels

    df["goal_bin"] = pd.cut(
        df["n_goals"],
        bins=bins,
        labels=labels,
        right=False,  # Left-inclusive bins (e.g., [2, 3) includes 2)
    )

    # Filter out cases with n_goals < 1 or n_goals > 7
    df = df[df["n_goals"].between(1, 6)]

    # --- contingency table ---
    ct = (
        df.groupby(["sender_combo", "goal_bin"])
        .size()
        .unstack(fill_value=0)
    )

    ct = ct.reindex(columns=labels, fill_value=0)

    ct["Total"] = ct.sum(axis=1)

    # --- total row ---
    total = ct.sum()
    ct = pd.concat([ct, total.to_frame().T])
    ct = ct.rename(index={0: "TOTAL"})
    ct.index.name = "Sender"

    # --- relative frequencies ---
    rel = ct[labels].div(ct["Total"], axis=0).mul(100).round(1)

    # --- MultiIndex output ---
    result = pd.DataFrame(index=ct.index)

    for c in labels:
        result[(c, "Abs.")] = ct[c]
        result[(c, "Rel(%)")] = rel[c]

    result[("Total", "")] = ct["Total"]

    result.columns = pd.MultiIndex.from_tuples(result.columns)

    return result
#print(get_goal_count_by_sender(con))



def get_goal_adaptation_by_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Frequency distribution of sanction regimes by sender and review adaptation of goal.

    Sender is collapsed at case level:
    - (EEC, EU) → "EEC & EU"

    Adaptation of goal categories:
    - Adapted (1)
    - Not adapted (0)
    - Missing (NULL)
    """

    sql = """
    SELECT
        rc.case_id,
        cg.adapt_goal,
        s.decod AS sender
    FROM RegimeCase rc
    JOIN Case_Sender cs ON rc.case_id = cs.case_id
    JOIN Sender s       ON cs.sender_id = s.sender_id
    JOIN Case_Goal cg   ON rc.case_id = cg.case_id
    """

    df = query(sql, con)

    # --- collapse sender at case level ---
    sender_per_case = (
        df.groupby("case_id")["sender"]
          .apply(
              lambda x: "EEC & EU"
              if set(x) == {
                  "european economic community - european community",
                  "european union"
              }
              else x.iloc[0]
          )
    )

    # Drop duplicates to get one row per case
    df = df.drop_duplicates("case_id").copy()
    df["sender"] = df["case_id"].map(sender_per_case)

    # --- map sender labels ---
    df["sender"] = df["sender"].map(
        lambda x: decode.SENDER_ABBREV.get(x, x)
    )

    # --- classify adapt_goal ---
    def classify(x):
        if x == 1:
            return "Adapted"
        elif x == 0:
            return "Not adapted"
        else:
            return "Missing"

    df["adapt_goal_cat"] = df["adapt_goal"].apply(classify)

    # --- contingency table ---
    ct = (
        df.groupby(["sender", "adapt_goal_cat"])
          .size()
          .unstack(fill_value=0)
    )

    cols = [
        "Adapted",
        "Not adapted",
        "Missing"
    ]

    ct = ct.reindex(columns=cols, fill_value=0)

    ct["Total"] = ct.sum(axis=1)

    # --- TOTAL row ---
    total = ct.sum()
    ct = pd.concat([ct, total.to_frame().T])
    ct = ct.rename(index={0: "TOTAL"})
    ct.index.name = "Sender"

    # --- relative frequencies ---
    rel = ct[cols].div(ct["Total"], axis=0).mul(100).round(1)

    # --- MultiIndex output ---
    result = pd.DataFrame(index=ct.index)

    for c in cols:
        result[(c, "Abs.")] = ct[c]
        result[(c, "Rel(%)")] = rel[c]

    result[("Total", "")] = ct["Total"]

    result.columns = pd.MultiIndex.from_tuples(result.columns)

    return result
#print(get_goal_adaptation_by_sender(con))    


def get_target_salience_by_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Frequency distribution of sanction regimes by sender and target salience.

    Sender is collapsed at case level:
    - (EEC, EU) → "EEC & EU"

    Target salience categories:
    - Has target salience (1)
    - Lacks target salience (0)
    """

    sql = """
    SELECT
        rc.case_id,
        rc.target_salience,
        s.decod AS sender
    FROM RegimeCase rc
    JOIN Case_Sender cs ON rc.case_id = cs.case_id
    JOIN Sender s       ON cs.sender_id = s.sender_id
    """

    df = query(sql, con)

    # --- collapse sender at case level ---
    sender_per_case = (
        df.groupby("case_id")["sender"]
          .apply(
              lambda x: "EEC & EU"
              if set(x) == {
                  "european economic community - european community",
                  "european union"
              }
              else x.iloc[0]
          )
    )

    # Drop duplicates to get one row per case
    df = df.drop_duplicates("case_id").copy()
    df["sender"] = df["case_id"].map(sender_per_case)

    # --- map sender labels ---
    df["sender"] = df["sender"].map(
        lambda x: decode.SENDER_ABBREV.get(x, x)
    )

    # --- classify target_salience ---
    def classify(x):
        if x == 1:
            return "Has target salience"
        else:
            return "Lacks target salience"

    df["target_salience_cat"] = df["target_salience"].apply(classify)

    # --- contingency table ---
    ct = (
        df.groupby(["sender", "target_salience_cat"])
          .size()
          .unstack(fill_value=0)
    )

    cols = [
        "Has target salience",
        "Lacks target salience"
    ]

    ct = ct.reindex(columns=cols, fill_value=0)

    ct["Total"] = ct.sum(axis=1)

    # --- TOTAL row ---
    total = ct.sum()
    ct = pd.concat([ct, total.to_frame().T])
    ct = ct.rename(index={0: "TOTAL"})
    ct.index.name = "Sender"

    # --- relative frequencies ---
    rel = ct[cols].div(ct["Total"], axis=0).mul(100).round(1)

    # --- MultiIndex output ---
    result = pd.DataFrame(index=ct.index)

    for c in cols:
        result[(c, "Abs.")] = ct[c]
        result[(c, "Rel(%)")] = rel[c]

    result[("Total", "")] = ct["Total"]

    result.columns = pd.MultiIndex.from_tuples(result.columns)

    return result
#print(get_target_salience_by_sender(con))


def get_sender_salience_by_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Frequency distribution of sanction regimes by sender and sender salience.

    Sender is collapsed at case level:
    - (EEC, EU) → "EEC & EU"

    Sender salience categories:
    - Has sender salience (1)
    - Lacks sender salience (0)
    """

    sql = """
    SELECT
        rc.case_id,
        rc.sender_salience,
        s.decod AS sender
    FROM RegimeCase rc
    JOIN Case_Sender cs ON rc.case_id = cs.case_id
    JOIN Sender s       ON cs.sender_id = s.sender_id
    """

    df = query(sql, con)

    # --- collapse sender at case level ---
    sender_per_case = (
        df.groupby("case_id")["sender"]
          .apply(
              lambda x: "EEC & EU"
              if set(x) == {
                  "european economic community - european community",
                  "european union"
              }
              else x.iloc[0]
          )
    )

    # Drop duplicates to get one row per case
    df = df.drop_duplicates("case_id").copy()
    df["sender"] = df["case_id"].map(sender_per_case)

    # --- map sender labels ---
    df["sender"] = df["sender"].map(
        lambda x: decode.SENDER_ABBREV.get(x, x)
    )

    # --- classify sender_salience ---
    def classify(x):
        if x == 1:
            return "Has sender salience"
        else:
            return "Lacks sender salience"

    df["sender_salience_cat"] = df["sender_salience"].apply(classify)

    # --- contingency table ---
    ct = (
        df.groupby(["sender", "sender_salience_cat"])
          .size()
          .unstack(fill_value=0)
    )

    cols = [
        "Has sender salience",
        "Lacks sender salience"
    ]

    ct = ct.reindex(columns=cols, fill_value=0)

    ct["Total"] = ct.sum(axis=1)

    # --- TOTAL row ---
    total = ct.sum()
    ct = pd.concat([ct, total.to_frame().T])
    ct = ct.rename(index={0: "TOTAL"})
    ct.index.name = "Sender"

    # --- relative frequencies ---
    rel = ct[cols].div(ct["Total"], axis=0).mul(100).round(1)

    # --- MultiIndex output ---
    result = pd.DataFrame(index=ct.index)

    for c in cols:
        result[(c, "Abs.")] = ct[c]
        result[(c, "Rel(%)")] = rel[c]

    result[("Total", "")] = ct["Total"]

    result.columns = pd.MultiIndex.from_tuples(result.columns)

    return result
#print(get_sender_salience_by_sender(con))    


def get_requirement_termination_by_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Frequency distribution of sanction regimes by sender and requirement termination.

    Sender is collapsed at case level:
    - (EEC, EU) → "EEC & EU"

    Requirement termination categories:
    - Ambiguous
    - Clear
    - missing
    """

    sql = """
    SELECT
        rc.case_id,
        rc.requirement_termination,
        s.decod AS sender
    FROM RegimeCase rc
    JOIN Case_Sender cs ON rc.case_id = cs.case_id
    JOIN Sender s       ON cs.sender_id = s.sender_id
    """

    df = query(sql, con)

    # --- collapse sender at case level ---
    sender_per_case = (
        df.groupby("case_id")["sender"]
          .apply(
              lambda x: "EEC & EU"
              if set(x) == {
                  "european economic community - european community",
                  "european union"
              }
              else x.iloc[0]
          )
    )

    # Drop duplicates to get one row per case
    df = df.drop_duplicates("case_id").copy()
    df["sender"] = df["case_id"].map(sender_per_case)

    # --- map sender labels ---
    df["sender"] = df["sender"].map(
        lambda x: decode.SENDER_ABBREV.get(x, x)
    )

    # Use requirement_termination directly (no classification needed)
    df["requirement_termination_cat"] = df["requirement_termination"]

    # --- contingency table ---
    ct = (
        df.groupby(["sender", "requirement_termination_cat"])
          .size()
          .unstack(fill_value=0)
    )

    cols = [
        "Ambiguous",
        "Clear",
        "missing"
    ]

    ct = ct.reindex(columns=cols, fill_value=0)

    ct["Total"] = ct.sum(axis=1)

    # --- TOTAL row ---
    total = ct.sum()
    ct = pd.concat([ct, total.to_frame().T])
    ct = ct.rename(index={0: "TOTAL"})
    ct.index.name = "Sender"

    # --- relative frequencies ---
    rel = ct[cols].div(ct["Total"], axis=0).mul(100).round(1)

    # --- MultiIndex output ---
    result = pd.DataFrame(index=ct.index)

    for c in cols:
        result[(c, "Abs.")] = ct[c]
        result[(c, "Rel(%)")] = rel[c]

    result[("Total", "")] = ct["Total"]

    result.columns = pd.MultiIndex.from_tuples(result.columns)

    return result
#print(get_requirement_termination_by_sender(con))



def get_negotiation_by_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Frequency distribution of sanction regimes by sender and negotiation.

    Sender is collapsed at case level:
    - (EEC, EU) → "EEC & EU"

    Negotiation categories:
    - Has negotiation (1)
    - Lacks negotiation (0)
    """
    sql = """
    SELECT
        rc.case_id,
        rc.negotiations,
        s.decod AS sender
    FROM RegimeCase rc
    JOIN Case_Sender cs ON rc.case_id = cs.case_id
    JOIN Sender s       ON cs.sender_id = s.sender_id
    """
    
    df = query(sql, con)

    # --- collapse sender at case level ---
    sender_per_case = (
        df.groupby("case_id")["sender"]
          .apply(
              lambda x: "EEC & EU"
              if set(x) == {
                  "european economic community - european community",
                  "european union"
              }
              else x.iloc[0]
          )
    )

    # Drop duplicates to get one row per case
    df = df.drop_duplicates("case_id").copy()
    df["sender"] = df["case_id"].map(sender_per_case)

    # --- map sender labels ---
    df["sender"] = df["sender"].map(
        lambda x: decode.SENDER_ABBREV.get(x, x)
    )

    # --- classify negotiations ---
    def classify(x):
        if x == 1:
            return "Has negotiation"
        else:
            return "Lacks negotiation"

    df["negotiation_cat"] = df["negotiations"].apply(classify)

    # --- contingency table ---
    ct = (
        df.groupby(["sender", "negotiation_cat"])
          .size()
          .unstack(fill_value=0)
    )

    cols = [
        "Has negotiation",
        "Lacks negotiation"
    ]

    ct = ct.reindex(columns=cols, fill_value=0)
    ct["Total"] = ct.sum(axis=1)

    # --- TOTAL row ---
    total = ct.sum()
    ct = pd.concat([ct, total.to_frame().T])
    ct = ct.rename(index={0: "TOTAL"})
    ct.index.name = "Sender"

    # --- relative frequencies ---
    rel = ct[cols].div(ct["Total"], axis=0).mul(100).round(1)

    # --- MultiIndex output ---
    result = pd.DataFrame(index=ct.index)

    for c in cols:
        result[(c, "Abs.")] = ct[c]
        result[(c, "Rel(%)")] = rel[c]

    result[("Total", "")] = ct["Total"]

    result.columns = pd.MultiIndex.from_tuples(result.columns)

    return result
#print(get_negotiation_by_sender(con))    


def get_outcome_type_by_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Contingency table of sanction regimes by sender and outcome type.

    Multi-sender cases are collapsed at the case level in pandas:
    - (EEC, EU) is treated as 'EEC & EU'

    Then contingency table is built on cleaned sender categories.
    """

    sql = """
        SELECT
            rc.case_id,
            s.decod AS sender,
            co.outcome_type

        FROM RegimeCase rc
        JOIN Case_Sender cs ON rc.case_id = cs.case_id
        JOIN Sender s       ON cs.sender_id = s.sender_id
        JOIN Case_Outcome co ON rc.case_id = co.case_id
    """

    df = query(sql, con)

    # --- collapse multi-sender at CASE level ---
    sender_per_case = (
        df.groupby("case_id")["sender"]
          .apply(lambda x: "EEC & EU" if set(x) == {
              "european economic community - european community",
              "european union"
          } else x.iloc[0])
    )

    df = df.drop_duplicates("case_id").copy()
    df["sender"] = df["case_id"].map(sender_per_case)

    # --- map sender labels (as in your duration function) ---
    df["sender"] = df["sender"].map(
        lambda x: decode.SENDER_ABBREV.get(x, x)
    )

    # --- contingency table ---
    ct = (
        df.groupby(["sender", "outcome_type"])
          .size()
          .unstack(fill_value=0)
    )

    # Reindex to ensure consistent column order (optional, adjust as needed)
    # You can list all outcome types from your Outcome table here
    count_cols = sorted(ct.columns.tolist())

    ct = ct.reindex(columns=count_cols, fill_value=0)
    ct["Total"] = ct.sum(axis=1)

    # --- TOTAL row ---
    total = ct.sum()
    ct = pd.concat([ct, total.to_frame().T])
    ct = ct.rename(index={0: "TOTAL"})
    ct.index.name = "Sender"

    # --- relative frequencies ---
    rel = ct[count_cols].div(ct["Total"], axis=0).mul(100).round(1)

    # --- multi-index output ---
    result = pd.DataFrame(index=ct.index)

    for c in count_cols:
        result[(c, "Abs.")] = ct[c]
        result[(c, "Rel(%)")] = rel[c]

    result[("Total", "")] = ct["Total"]

    result.columns = pd.MultiIndex.from_tuples(result.columns)

    return result
#print(get_outcome_type_by_sender(con))    


def get_sender_cost_by_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Frequency distribution of sanction regimes by sender and sender cost.

    Multi-sender cases are collapsed at the case level in pandas:
    - (EEC, EU) is treated as 'EEC & EU'

    Then contingency table is built on cleaned sender categories.
    """

    sql = """
        SELECT
            rc.case_id,
            s.decod AS sender,
            rc.cost_sender

        FROM RegimeCase rc
        JOIN Case_Sender cs ON rc.case_id = cs.case_id
        JOIN Sender s       ON cs.sender_id = s.sender_id
    """

    df = query(sql, con)

    # --- collapse multi-sender at CASE level ---
    sender_per_case = (
        df.groupby("case_id")["sender"]
          .apply(lambda x: "EEC & EU" if set(x) == {
              "european economic community - european community",
              "european union"
          } else x.iloc[0])
    )

    df = df.drop_duplicates("case_id").copy()
    df["sender"] = df["case_id"].map(sender_per_case)

    # --- map sender labels (as in your duration function) ---
    df["sender"] = df["sender"].map(
        lambda x: decode.SENDER_ABBREV.get(x, x)
    )

    # --- contingency table ---
    ct = (
        df.groupby(["sender", "cost_sender"])
          .size()
          .unstack(fill_value=0)
    )

    # Reindex to ensure consistent column order (sorted by default)
    count_cols = sorted(ct.columns.tolist())

    ct = ct.reindex(columns=count_cols, fill_value=0)
    ct["Total"] = ct.sum(axis=1)

    # --- TOTAL row ---
    total = ct.sum()
    ct = pd.concat([ct, total.to_frame().T])
    ct = ct.rename(index={0: "TOTAL"})
    ct.index.name = "Sender"

    # --- relative frequencies ---
    rel = ct[count_cols].div(ct["Total"], axis=0).mul(100).round(1)

    # --- multi-index output ---
    result = pd.DataFrame(index=ct.index)

    for c in count_cols:
        result[(c, "Abs.")] = ct[c]
        result[(c, "Rel(%)")] = rel[c]

    result[("Total", "")] = ct["Total"]

    result.columns = pd.MultiIndex.from_tuples(result.columns)

    return result
#print(get_sender_cost_by_sender(con)) 


def get_inst_investment_by_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Frequency distribution of sanction regimes by sender and institutional investment.

    Sender is collapsed at case level:
    - (EEC, EU) → "EEC & EU"

    Institutional investment categories:
    - Has inst. invest. (1)
    - Lacks inst. invest. (0)
    """

    sql = """
    SELECT
        rc.case_id,
        rc.inst_investment,
        s.decod AS sender
    FROM RegimeCase rc
    JOIN Case_Sender cs ON rc.case_id = cs.case_id
    JOIN Sender s       ON cs.sender_id = s.sender_id
    """

    df = query(sql, con)

    # --- collapse sender at case level ---
    sender_per_case = (
        df.groupby("case_id")["sender"]
          .apply(
              lambda x: "EEC & EU"
              if set(x) == {
                  "european economic community - european community",
                  "european union"
              }
              else x.iloc[0]
          )
    )

    # Drop duplicates to get one row per case
    df = df.drop_duplicates("case_id").copy()
    df["sender"] = df["case_id"].map(sender_per_case)

    # --- map sender labels ---
    df["sender"] = df["sender"].map(
        lambda x: decode.SENDER_ABBREV.get(x, x)
    )

    # --- classify inst_investment ---
    def classify(x):
        if x == 1:
            return "Has inst. invest."
        else:
            return "Lacks inst. invest."

    df["inst_investment_cat"] = df["inst_investment"].apply(classify)

    # --- contingency table ---
    ct = (
        df.groupby(["sender", "inst_investment_cat"])
          .size()
          .unstack(fill_value=0)
    )

    cols = [
        "Has inst. invest.",
        "Lacks inst. invest."
    ]

    ct = ct.reindex(columns=cols, fill_value=0)

    ct["Total"] = ct.sum(axis=1)

    # --- TOTAL row ---
    total = ct.sum()
    ct = pd.concat([ct, total.to_frame().T])
    ct = ct.rename(index={0: "TOTAL"})
    ct.index.name = "Sender"

    # --- relative frequencies ---
    rel = ct[cols].div(ct["Total"], axis=0).mul(100).round(1)

    # --- MultiIndex output ---
    result = pd.DataFrame(index=ct.index)

    for c in cols:
        result[(c, "Abs.")] = ct[c]
        result[(c, "Rel(%)")] = rel[c]

    result[("Total", "")] = ct["Total"]

    result.columns = pd.MultiIndex.from_tuples(result.columns)

    return result
#print(get_inst_investment_by_sender(con))    


def get_target_cost_by_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Frequency distribution of sanction regimes by sender and target cost.

    Sender is collapsed at case level:
    - (EEC, EU) → "EEC & EU"

    Target cost categories:
    - All unique text values from RegimeCase.cost_target
    """

    sql = """
    SELECT
        rc.case_id,
        rc.cost_target,
        s.decod AS sender
    FROM RegimeCase rc
    JOIN Case_Sender cs ON rc.case_id = cs.case_id
    JOIN Sender s       ON cs.sender_id = s.sender_id
    """

    df = query(sql, con)

    # --- collapse sender at case level ---
    sender_per_case = (
        df.groupby("case_id")["sender"]
          .apply(
              lambda x: "EEC & EU"
              if set(x) == {
                  "european economic community - european community",
                  "european union"
              }
              else x.iloc[0]
          )
    )

    # Drop duplicates to get one row per case
    df = df.drop_duplicates("case_id").copy()
    df["sender"] = df["case_id"].map(sender_per_case)

    # --- map sender labels ---
    df["sender"] = df["sender"].map(
        lambda x: decode.SENDER_ABBREV.get(x, x)
    )

    # Use cost_target directly (assuming it's already clean)
    df["target_cost_cat"] = df["cost_target"]

    # --- contingency table ---
    # Get all unique target cost values for columns
    unique_costs = sorted(df["target_cost_cat"].unique())
    ct = (
        df.groupby(["sender", "target_cost_cat"])
          .size()
          .unstack(fill_value=0)
    )

    # Reindex to include all unique cost values
    ct = ct.reindex(columns=unique_costs, fill_value=0)

    ct["Total"] = ct.sum(axis=1)

    # --- TOTAL row ---
    total = ct.sum()
    ct = pd.concat([ct, total.to_frame().T])
    ct = ct.rename(index={0: "TOTAL"})
    ct.index.name = "Sender"

    # --- relative frequencies ---
    rel = ct[unique_costs].div(ct["Total"], axis=0).mul(100).round(1)

    # --- MultiIndex output ---
    result = pd.DataFrame(index=ct.index)

    for c in unique_costs:
        result[(c, "Abs.")] = ct[c]
        result[(c, "Rel(%)")] = rel[c]

    result[("Total", "")] = ct["Total"]

    result.columns = pd.MultiIndex.from_tuples(result.columns)

    return result
#print(get_target_cost_by_sender(con))    


def get_multilat_by_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Frequency distribution of sanction regimes by sender and multilateralism.

    Sender is collapsed at case level:
    - (EEC, EU) → "EEC & EU"

    Multilateralism categories:
    - Single Multilateralism (1 value)
    - Multiple Multilateralisms (>1 value)
    """

    sql = """
    SELECT
        rc.case_id,
        s.decod AS sender
    FROM RegimeCase rc
    JOIN Case_Sender cs ON rc.case_id = cs.case_id
    JOIN Sender s       ON cs.sender_id = s.sender_id
    """

    df = query(sql, con)

    # --- collapse sender at case level ---
    sender_per_case = (
        df.groupby("case_id")["sender"]
          .apply(
              lambda x: "EEC & EU"
              if set(x) == {
                  "european economic community - european community",
                  "european union"
              }
              else x.iloc[0]
          )
    )

    # Drop duplicates to get one row per case
    df = df.drop_duplicates("case_id").copy()
    df["sender"] = df["case_id"].map(sender_per_case)

    # --- map sender labels ---
    df["sender"] = df["sender"].map(
        lambda x: decode.SENDER_ABBREV.get(x, x)
    )

    # --- count multilateralism values per case ---
    multilateralism_counts = (
        con.execute("""
            SELECT
                case_id,
                COUNT(multilateralism_id) AS multilateralism_count
            FROM
                Case_Multilateralism
            GROUP BY
                case_id
        """)
        .fetchall()
    )

    multilateralism_counts_df = pd.DataFrame(
        multilateralism_counts,
        columns=["case_id", "multilateralism_count"]
    )

    # Merge multilateralism counts into the main DataFrame
    df = df.merge(multilateralism_counts_df, on="case_id", how="left")
    df["multilateralism_count"] = df["multilateralism_count"].fillna(0).astype(int)

    # --- classify multilateralism ---
    def classify(x):
        if x == 1:
            return "Single Multilateralism"
        elif x > 1:
            return "Multiple Multilateralisms"

    df["multilateralism_cat"] = df["multilateralism_count"].apply(classify)

    # --- contingency table ---
    ct = (
        df.groupby(["sender", "multilateralism_cat"])
          .size()
          .unstack(fill_value=0)
    )

    cols = [
        "Single Multilateralism",
        "Multiple Multilateralisms"
    ]

    ct = ct.reindex(columns=cols, fill_value=0)

    ct["Total"] = ct.sum(axis=1)

    # --- TOTAL row ---
    total = ct.sum()
    ct = pd.concat([ct, total.to_frame().T])
    ct = ct.rename(index={0: "TOTAL"})
    ct.index.name = "Sender"

    # --- relative frequencies ---
    rel = ct[cols].div(ct["Total"], axis=0).mul(100).round(1)

    # --- MultiIndex output ---
    result = pd.DataFrame(index=ct.index)

    for c in cols:
        result[(c, "Abs.")] = ct[c]
        result[(c, "Rel(%)")] = rel[c]

    result[("Total", "")] = ct["Total"]

    result.columns = pd.MultiIndex.from_tuples(result.columns)

    return result
#print(get_multilat_by_sender(con))    
