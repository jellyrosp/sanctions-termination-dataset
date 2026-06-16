import sqlite3
from pathlib import Path
import sys

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Project root: 3 levels up from this file
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
src_dir = BASE_DIR / "src"

# Add src to sys.path so `import decode` works
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

import decode
from stats.helpers import query, _get_multilateralism_per_case

# Connect to the database using the same BASE_DIR
con = sqlite3.connect(BASE_DIR / "data" / "IST-dataset.db")

#============================================================
# UNIVARIATE ANALYSIS
#============================================================

def get_expiry_distribution(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Univariate frequency distribution of sanction regimes by expiry condition.
    expiry = 1: sanctions document stipulates an expiry date.
    expiry = 0: no expiry date stipulated.
    """
    sql = """
        SELECT
            CASE
                WHEN expiry = 1 THEN 'Stipulated'
                WHEN expiry = 0 THEN 'Not stipulated'
                ELSE 'Missing'
            END AS expiry_condition,
            COUNT(*) AS n_cases
        FROM RegimeCase
        GROUP BY expiry
        ORDER BY expiry DESC
    """
    df = query(sql, con)
    total = df["n_cases"].sum()
    df["Rel(%)"] = (df["n_cases"] / total * 100).round(1)
    df = df.rename(columns={"expiry_condition": "Expiry", "n_cases": "Abs."})
    df = df.set_index("Expiry")

    total_row = pd.Series({"Abs.": total, "Rel(%)": 100.0}, name="TOTAL")
    df = pd.concat([df, total_row.to_frame().T])

    return df
#print(get_expiry_distribution(con))


def get_review_distribution(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Univariate frequency distribution of sanction regimes by rieview condition.
    review = 1: sanctions document reviewed.
    expiry = 0: sanctions document not reviewed.
    """
    sql = """
        SELECT
            CASE
                WHEN review = 1 THEN 'Has review'
                WHEN review = 0 THEN 'Lacks review'
                ELSE 'Missing'
            END AS review_condition,
            COUNT(*) AS n_cases
        FROM RegimeCase
        GROUP BY review
        ORDER BY review DESC
    """
    df = query(sql, con)
    total = df["n_cases"].sum()
    df["Rel(%)"] = (df["n_cases"] / total * 100).round(1)
    df = df.rename(columns={"review_condition": "Review", "n_cases": "Abs."})
    df = df.set_index("Review")

    total_row = pd.Series({"Abs.": total, "Rel(%)": 100.0}, name="TOTAL")
    df = pd.concat([df, total_row.to_frame().T])

    return df
#print(get_review_distribution(con))


def get_req_termination_distribution(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Univariate frequency distribution of sanction regimes by
    requirement termination clarity.
    Values: Clear, Ambiguous, Missing (NULL).
    """
    sql = """
        SELECT
            CASE
                WHEN requirement_termination IS NULL THEN 'Missing'
                ELSE requirement_termination
            END AS req_termination,
            COUNT(*) AS n_cases
        FROM RegimeCase
        GROUP BY req_termination
        ORDER BY n_cases DESC
    """
    df = query(sql, con)
    total = df["n_cases"].sum()
    df["Rel(%)"] = (df["n_cases"] / total * 100).round(1)
    df = df.rename(columns={"req_termination": "Requirement Termination", "n_cases": "Abs."})
    df = df.set_index("Requirement Termination")

    total_row = pd.Series({"Abs.": total, "Rel(%)": 100.0}, name="TOTAL")
    df = pd.concat([df, total_row.to_frame().T])

    return df
#print(get_req_termination_distribution(con))


def get_outcome_distribution(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Univariate frequency distribution of sanction regimes by outcome.
    Each case may have multiple outcomes (many-to-many) or none (NULL).
    Outcomes are collapsed at case level into a sorted combination string.
    Cases with no outcome are labelled 'Missing'.
    """
    outcome_sql = """
        SELECT co.case_id, o.outcome_type
        FROM Case_Outcome co
        JOIN Outcome o ON co.outcome_type = o.outcome_type
    """
    cases_sql = "SELECT case_id FROM RegimeCase"

    outcome_df = query(outcome_sql, con)
    cases_df   = query(cases_sql,   con)

    # Collapse multiple outcomes per case into sorted combo string
    outcome_grouped = (
        outcome_df.groupby("case_id")["outcome_type"]
        .apply(lambda x: " & ".join(sorted(x)))
        .reset_index(name="outcome_combo")
    )

    # Left join to include cases with no outcome
    df = cases_df.merge(outcome_grouped, on="case_id", how="left")
    df["outcome_combo"] = df["outcome_combo"].fillna("Missing")

    total = len(df)

    ct = (
        df.groupby("outcome_combo")
        .size()
        .reset_index(name="Abs.")
        .sort_values("Abs.", ascending=False)
    )
    ct["Rel(%)"] = (ct["Abs."] / total * 100).round(1)
    ct = ct.rename(columns={"outcome_combo": "Outcome"})
    ct = ct.set_index("Outcome")

    total_row = pd.Series({"Abs.": total, "Rel(%)": 100.0}, name="TOTAL")
    df = pd.concat([ct, total_row.to_frame().T])

    return df
#print(get_outcome_distribution(con))


def get_sender_distribution(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Univariate frequency distribution of sanction regimes by sender.
    Sender is collapsed at case level: cases with multiple senders
    are labelled as a sorted combination (e.g. 'EEC & EU').
    """
    sql = """
        SELECT cs.case_id, s.decod AS sender
        FROM Case_Sender cs
        JOIN Sender s ON cs.sender_id = s.sender_id
    """
    df = query(sql, con)

    df["sender"] = df["sender"].map(
        lambda x: decode.SENDER_ABBREV.get(x, x)
    )

    # Collapse multiple senders per case into sorted combo string
    sender_grouped = (
        df.groupby("case_id")["sender"]
        .apply(lambda x: " & ".join(sorted(x)))
        .reset_index(name="sender_combo")
    )

    total = len(sender_grouped)

    ct = (
        sender_grouped.groupby("sender_combo")
        .size()
        .reset_index(name="Abs.")
        .sort_values("Abs.", ascending=False)
    )
    ct["Rel(%)"] = (ct["Abs."] / total * 100).round(1)
    ct = ct.rename(columns={"sender_combo": "Sender"})
    ct = ct.set_index("Sender")

    total_row = pd.Series({"Abs.": total, "Rel(%)": 100.0}, name="TOTAL")
    ct = pd.concat([ct, total_row.to_frame().T])

    return ct
#print(get_sender_distribution(con))  


def get_duration_distribution(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Univariate frequency distribution of sanction regimes by duration interval.
    Duration is computed from start_date to ter_date for terminated cases,
    or to 2018-12-31 for ongoing cases.
    Intervals: 0-6m, 6m-1y, 1-2y, 2-5y, 5-10y, 10-20y, 20+y.
    """
    sql = """
        SELECT
            rc.case_id,
            rc.start_date,
            CASE
                WHEN rc.ongoing = 1 THEN '2018-12-31'
                ELSE rc.ter_date
            END AS end_date
        FROM RegimeCase rc
        WHERE rc.start_date IS NOT NULL
          AND (rc.ter_date IS NOT NULL OR rc.ongoing = 1)
    """
    df = query(sql, con)

    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
    df["end_date"]   = pd.to_datetime(df["end_date"],   errors="coerce")

    df["months"] = (
        (df["end_date"].dt.year  - df["start_date"].dt.year) * 12 +
        (df["end_date"].dt.month - df["start_date"].dt.month)
    )

    bins   = [0, 6, 12, 24, 60, 120, 240, float("inf")]
    labels = ["0–6m", "6m–1y", "1–2y", "2–5y", "5–10y", "10–20y", "20+y"]

    df["interval"] = pd.cut(df["months"], bins=bins, labels=labels, right=False)

    total = len(df)

    ct = (
        df.groupby("interval", observed=True)
          .size()
          .reindex(labels, fill_value=0)
          .reset_index(name="Abs.")
    )
    ct["Rel(%)"] = (ct["Abs."] / total * 100).round(1)
    ct = ct.rename(columns={"interval": "Duration"})
    ct = ct.set_index("Duration")

    total_row = pd.Series({"Abs.": total, "Rel(%)": 100.0}, name="TOTAL")
    ct = pd.concat([ct, total_row.to_frame().T])

    return ct
#print(get_duration_distribution(con))    


def get_gradual_distribution(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Univariate frequency distribution of sanction regimes by
    termination modality.
    gradual = 1: Gradual termination.
    gradual = 0: Lifted at once.
    gradual = NULL: Missing.
    """
    sql = """
        SELECT
            CASE
                WHEN gradual = 1 THEN 'Gradual'
                WHEN gradual = 0 THEN 'Not Gradual'
                ELSE 'Missing'
            END AS gradual_condition,
            COUNT(*) AS n_cases
        FROM RegimeCase
        GROUP BY gradual
        ORDER BY gradual DESC
    """
    df = query(sql, con)
    total = df["n_cases"].sum()
    df["Rel(%)"] = (df["n_cases"] / total * 100).round(1)
    df = df.rename(columns={"gradual_condition": "Gradual", "n_cases": "Abs."})
    df = df.set_index("Gradual")

    total_row = pd.Series({"Abs.": total, "Rel(%)": 100.0}, name="TOTAL")
    df = pd.concat([df, total_row.to_frame().T])

    return df
#print(get_gradual_distribution(con))    


def get_adapt_goal_distribution(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Univariate frequency distribution of sanction regimes by
    goal adaptation.
    adapt_goal = 1: Goal was adapted during the regime.
    adapt_goal = 0: Goal was not adapted.
    adapt_goal = NULL: Missing.
    One row per case (if a case has multiple goals, take the max
    adapt_goal value to flag whether any goal was adapted).
    """
    sql = """
        SELECT
            case_id,
            MAX(adapt_goal) AS adapt_goal
        FROM Case_Goal
        GROUP BY case_id
    """
    df = query(sql, con)

    # Include cases with no goals at all (adapt_goal = NULL)
    cases_sql = "SELECT case_id FROM RegimeCase"
    cases_df  = query(cases_sql, con)
    df = cases_df.merge(df, on="case_id", how="left")

    df["adapt_goal"] = df["adapt_goal"].map(
        lambda x: "Adapted" if x == 1
        else "Not Adapted" if x == 0
        else "Missing"
    )

    total = len(df)

    ct = (
        df.groupby("adapt_goal")
          .size()
          .reset_index(name="Abs.")
          .sort_values("Abs.", ascending=False)
    )
    ct["Rel(%)"] = (ct["Abs."] / total * 100).round(1)
    ct = ct.rename(columns={"adapt_goal": "Goal Adaptation"})
    ct = ct.set_index("Goal Adaptation")

    total_row = pd.Series({"Abs.": total, "Rel(%)": 100.0}, name="TOTAL")
    ct = pd.concat([ct, total_row.to_frame().T])

    return ct
#print(get_adapt_goal_distribution(con))    


def get_negotiation_distribution(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Univariate frequency distribution of sanction regimes by
    negotiation presence.
    negotiations = 1: Negotiations took place.
    negotiations = 0: No negotiations.
    negotiations = NULL: Missing.
    """
    sql = """
        SELECT
            CASE
                WHEN negotiations = 1 THEN 'Has Negotiation'
                WHEN negotiations = 0 THEN 'Lacks Negotiation'
                ELSE 'Missing'
            END AS negotiation_condition,
            COUNT(*) AS n_cases
        FROM RegimeCase
        GROUP BY negotiations
        ORDER BY negotiations DESC
    """
    df = query(sql, con)
    total = df["n_cases"].sum()
    df["Rel(%)"] = (df["n_cases"] / total * 100).round(1)
    df = df.rename(columns={"negotiation_condition": "Negotiation", "n_cases": "Abs."})
    df = df.set_index("Negotiation")

    total_row = pd.Series({"Abs.": total, "Rel(%)": 100.0}, name="TOTAL")
    df = pd.concat([df, total_row.to_frame().T])

    return df
#print(get_negotiation_distribution(con))    


def get_multilateralism_distribution(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Univariate frequency distribution of sanction regimes by multilateralism.
    Multiple multilateralism values per case are collapsed into a sorted
    combination string. Cases with no multilateralism are labelled 'Missing'.
    """
    multilat = _get_multilateralism_per_case(con)

    total = len(multilat)

    ct = (
        multilat.groupby(multilat)
        .size()
        .reset_index(name="Abs.")
        .sort_values("Abs.", ascending=False)
    )
    ct["Rel(%)"] = (ct["Abs."] / total * 100).round(1)
    ct = ct.rename(columns={"multilateralism": "Multilateralism"})
    ct = ct.set_index("Multilateralism")

    total_row = pd.Series({"Abs.": total, "Rel(%)": 100.0}, name="TOTAL")
    ct = pd.concat([ct, total_row.to_frame().T])

    return ct
#print(get_multilateralism_distribution(con))    