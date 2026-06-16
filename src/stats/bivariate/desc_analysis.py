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
from stats.helpers import _get_duration_per_case, _get_scalar_per_case, _build_contingency, _get_duration_per_case, _get_outcome_per_case, _get_sender_per_case, _get_multilateralism_per_case, query, check_expected_frequencies, normalize_contingency, collapse_rare_columns

# Connect to the database using the same BASE_DIR
con = sqlite3.connect(BASE_DIR / "data" / "IST-dataset.db")


#============================================================
# BIVARIATE ANALYSIS
#============================================================

# Y = DURATION ##############################################

    # ── expiry x duration ────────────────────────────────────────────────────────
def get_expiry_x_duration(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Contingency table of sanction regimes by expiry condition and
    duration interval. Relative frequencies are row-wise.
    """
    duration = _get_duration_per_case(con)
    expiry   = _get_scalar_per_case(con, "expiry").map(
        lambda x: "Stipulated" if x == 1
        else "Not stipulated" if x == 0
        else "Missing"
    )
    labels = ["0–6m", "6m–1y", "1–2y", "2–5y", "5–10y", "10–20y", "20+y"]
    return _build_contingency(expiry, duration, "Expiry", col_order=labels)
#print(get_expiry_x_duration(con))    


# ── review x duration ────────────────────────────────────────────────────────
def get_review_x_duration(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Contingency table of sanction regimes by review condition and
    duration interval. Relative frequencies are row-wise.
    """
    duration = _get_duration_per_case(con)
    review   = _get_scalar_per_case(con, "review").map(
        lambda x: "Review" if x == 1
        else "No review" if x == 0
        else "Missing"
    )
    labels = ["0–6m", "6m–1y", "1–2y", "2–5y", "5–10y", "10–20y", "20+y"]
    return _build_contingency(review, duration, "Review", col_order=labels)
#print(get_review_x_duration(con))    


# ── requirement_termination x duration ───────────────────────────────────────
def get_req_termination_x_duration(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Contingency table of sanction regimes by requirement termination
    clarity and duration interval. Relative frequencies are row-wise.
    """
    duration = _get_duration_per_case(con)
    req = _get_scalar_per_case(con, "requirement_termination").map(
        lambda x: "Missing" if (pd.isna(x) or x == "") else str(x).strip()
    )
    labels = ["0–6m", "6m–1y", "1–2y", "2–5y", "5–10y", "10–20y", "20+y"]
    return _build_contingency(req, duration, "Requirement Termination", col_order=labels)
#print(get_req_termination_x_duration(con))    

#============================================================
#============================================================

# Y = OUTCOME ##############################################

# ── expiry x outcome ─────────────────────────────────────────────────────────
def get_expiry_x_outcome(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Contingency table of sanction regimes by expiry condition and outcome.
    Relative frequencies are row-wise.
    """
    outcome = _get_outcome_per_case(con)
    expiry  = _get_scalar_per_case(con, "expiry").map(
        lambda x: "Stipulated" if x == 1
        else "Not stipulated" if x == 0
        else "Missing"
    )
    return _build_contingency(expiry, outcome, "Expiry")
#print(get_expiry_x_outcome(con))    

# ── review x outcome ─────────────────────────────────────────────────────────
def get_review_x_outcome(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Contingency table of sanction regimes by review condition and outcome.
    Relative frequencies are row-wise.
    """
    outcome = _get_outcome_per_case(con)
    review  = _get_scalar_per_case(con, "review").map(
        lambda x: "Review" if x == 1
        else "No review" if x == 0
        else "Missing"
    )
    return _build_contingency(review, outcome, "Review")
#print(get_review_x_outcome(con))

# ── requirement_termination x outcome ────────────────────────────────────────
def get_req_termination_x_outcome(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Contingency table of sanction regimes by requirement termination
    clarity and outcome. Relative frequencies are row-wise.
    """
    outcome = _get_outcome_per_case(con)
    req     = _get_scalar_per_case(con, "requirement_termination").map(
        lambda x: "Missing" if (pd.isna(x) or x == "") else str(x).strip()
    )
    return _build_contingency(req, outcome, "Requirement Termination")
#print(get_req_termination_x_outcome(con))    

#============================================================
#============================================================

# Y = SENDER ##############################################

# ── expiry x sender ───────────────────────────────────────────────────────────
def get_expiry_x_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Contingency table of sanction regimes by expiry condition and sender.
    Relative frequencies are row-wise.
    """
    sender = _get_sender_per_case(con)
    expiry = _get_scalar_per_case(con, "expiry").map(
        lambda x: "Stipulated" if x == 1
        else "Not stipulated" if x == 0
        else "Missing"
    )
    return _build_contingency(expiry, sender, "Expiry")
#print(get_expiry_x_sender(con))    


# ── review x sender ───────────────────────────────────────────────────────────
def get_review_x_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Contingency table of sanction regimes by review condition and sender.
    Relative frequencies are row-wise.
    """
    sender = _get_sender_per_case(con)
    review = _get_scalar_per_case(con, "review").map(
        lambda x: "Review" if x == 1
        else "No review" if x == 0
        else "Missing"
    )
    return _build_contingency(review, sender, "Review")
#print(get_review_x_sender(con))    


# ── requirement_termination x sender ─────────────────────────────────────────
def get_req_termination_x_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Contingency table of sanction regimes by requirement termination
    clarity and sender. Relative frequencies are row-wise.
    """
    sender = _get_sender_per_case(con)
    req    = _get_scalar_per_case(con, "requirement_termination").map(
        lambda x: "Missing" if (pd.isna(x) or x == "") else str(x).strip()
    )
    return _build_contingency(req, sender, "Requirement Termination")
#print(get_req_termination_x_sender(con))    

#============================================================
#============================================================


# Y = DURATION ##############################################

# ── gradual x duration ────────────────────────────────────────────────────────
def get_gradual_x_duration(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Contingency table of sanction regimes by termination modality and
    duration interval. Relative frequencies are row-wise.
    """
    duration = _get_duration_per_case(con)
    gradual  = _get_scalar_per_case(con, "gradual").map(
        lambda x: "Gradual" if x == 1
        else "Not Gradual" if x == 0
        else "Missing"
    )
    labels = ["0–6m", "6m–1y", "1–2y", "2–5y", "5–10y", "10–20y", "20+y"]
    return _build_contingency(gradual, duration, "Gradual", col_order=labels)
#print(get_gradual_x_duration(con))    


# ── adapt_goal x duration ─────────────────────────────────────────────────────
def get_adapt_goal_x_duration(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Contingency table of sanction regimes by goal adaptation and
    duration interval. Relative frequencies are row-wise.
    """
    duration   = _get_duration_per_case(con)

    adapt_sql  = """
        SELECT case_id, MAX(adapt_goal) AS adapt_goal
        FROM Case_Goal
        GROUP BY case_id
    """
    adapt_df   = query(adapt_sql, con)
    cases_sql  = "SELECT case_id FROM RegimeCase"
    cases_df   = query(cases_sql, con)
    merged     = cases_df.merge(adapt_df, on="case_id", how="left")
    adapt_goal = merged.set_index("case_id")["adapt_goal"].map(
        lambda x: "Adapted" if x == 1
        else "Not Adapted" if x == 0
        else "Missing"
    )

    labels = ["0–6m", "6m–1y", "1–2y", "2–5y", "5–10y", "10–20y", "20+y"]
    return _build_contingency(adapt_goal, duration, "Goal Adaptation", col_order=labels)
#print(get_adapt_goal_x_duration(con))    


# ── negotiations x duration ───────────────────────────────────────────────────
def get_negotiations_x_duration(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Contingency table of sanction regimes by negotiation presence and
    duration interval. Relative frequencies are row-wise.
    """
    duration     = _get_duration_per_case(con)
    negotiations = _get_scalar_per_case(con, "negotiations").map(
        lambda x: "Has Negotiations" if x == 1
        else "Lacks Negotiations" if x == 0
        else "Missing"
    )
    labels = ["0–6m", "6m–1y", "1–2y", "2–5y", "5–10y", "10–20y", "20+y"]
    return _build_contingency(negotiations, duration, "Negotiations", col_order=labels)
#print(get_negotiations_x_duration(con))    

#============================================================
#============================================================


# Y = OUTCOME ##############################################

# ── gradual x outcome ─────────────────────────────────────────────────────────
def get_gradual_x_outcome(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Contingency table of sanction regimes by termination modality and outcome.
    Relative frequencies are row-wise.
    """
    outcome = _get_outcome_per_case(con)
    gradual = _get_scalar_per_case(con, "gradual").map(
        lambda x: "Gradual" if x == 1
        else "Not Gradual" if x == 0
        else "Missing"
    )
    return _build_contingency(gradual, outcome, "Gradual")
#print(get_gradual_x_outcome(con))    


# ── adapt_goal x outcome ──────────────────────────────────────────────────────
def get_adapt_goal_x_outcome(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Contingency table of sanction regimes by goal adaptation and outcome.
    Relative frequencies are row-wise.
    """
    outcome    = _get_outcome_per_case(con)

    adapt_sql  = """
        SELECT case_id, MAX(adapt_goal) AS adapt_goal
        FROM Case_Goal
        GROUP BY case_id
    """
    adapt_df   = query(adapt_sql, con)
    cases_sql  = "SELECT case_id FROM RegimeCase"
    cases_df   = query(cases_sql, con)
    merged     = cases_df.merge(adapt_df, on="case_id", how="left")
    adapt_goal = merged.set_index("case_id")["adapt_goal"].map(
        lambda x: "Adapted" if x == 1
        else "Not Adapted" if x == 0
        else "Missing"
    )

    return _build_contingency(adapt_goal, outcome, "Goal Adaptation")
#print(get_adapt_goal_x_outcome(con))    


# ── negotiations x outcome ────────────────────────────────────────────────────
def get_negotiations_x_outcome(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Contingency table of sanction regimes by negotiation presence and outcome.
    Relative frequencies are row-wise.
    """
    outcome      = _get_outcome_per_case(con)
    negotiations = _get_scalar_per_case(con, "negotiations").map(
        lambda x: "Has Negotiations" if x == 1
        else "Lacks Negotiations" if x == 0
        else "Missing"
    )
    return _build_contingency(negotiations, outcome, "Negotiations")
#print(get_negotiations_x_outcome(con))    

#============================================================
#============================================================

# Y = SENDER ##############################################

# ── gradual x sender ──────────────────────────────────────────────────────────
def get_gradual_x_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Contingency table of sanction regimes by termination modality and sender.
    Relative frequencies are row-wise.
    """
    sender  = _get_sender_per_case(con)
    gradual = _get_scalar_per_case(con, "gradual").map(
        lambda x: "Gradual" if x == 1
        else "Not Gradual" if x == 0
        else "Missing"
    )
    return _build_contingency(gradual, sender, "Gradual")
#print(get_gradual_x_sender(con))    


# ── adapt_goal x sender ───────────────────────────────────────────────────────
def get_adapt_goal_x_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Contingency table of sanction regimes by goal adaptation and sender.
    Relative frequencies are row-wise.
    """
    sender     = _get_sender_per_case(con)

    adapt_sql  = """
        SELECT case_id, MAX(adapt_goal) AS adapt_goal
        FROM Case_Goal
        GROUP BY case_id
    """
    adapt_df   = query(adapt_sql, con)
    cases_sql  = "SELECT case_id FROM RegimeCase"
    cases_df   = query(cases_sql, con)
    merged     = cases_df.merge(adapt_df, on="case_id", how="left")
    adapt_goal = merged.set_index("case_id")["adapt_goal"].map(
        lambda x: "Adapted" if x == 1
        else "Not Adapted" if x == 0
        else "Missing"
    )
    return _build_contingency(adapt_goal, sender, "Goal Adaptation")
#print(get_adapt_goal_x_sender(con))    


# ── negotiations x sender ─────────────────────────────────────────────────────
def get_negotiations_x_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Contingency table of sanction regimes by negotiation presence and sender.
    Relative frequencies are row-wise.
    """
    sender       = _get_sender_per_case(con)
    negotiations = _get_scalar_per_case(con, "negotiations").map(
        lambda x: "Has Negotiation" if x == 1
        else "Lacks Negotiation" if x == 0
        else "Missing"
    )
    return _build_contingency(negotiations, sender, "Negotiations")
#print(get_negotiations_x_sender(con))    

#============================================================
#============================================================    

# Y = OUTCOME ##############################################

# ── multilateralism x outcome ─────────────────────────────────────────────────
def get_multilateralism_x_outcome(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Contingency table of sanction regimes by multilateralism and outcome.
    Relative frequencies are row-wise.
    """
    outcome         = _get_outcome_per_case(con)
    multilateralism = _get_multilateralism_per_case(con)
    return _build_contingency(multilateralism, outcome, "Multilateralism")
#print(get_multilateralism_x_outcome(con))    


# ── duration x outcome ────────────────────────────────────────────────────────
def get_duration_x_outcome(con: sqlite3.Connection) -> pd.DataFrame:
    """
    Contingency table of sanction regimes by duration interval and outcome.
    Relative frequencies are row-wise.
    """
    outcome  = _get_outcome_per_case(con)
    duration = _get_duration_per_case(con)
    labels   = ["0–6m", "6m–1y", "1–2y", "2–5y", "5–10y", "10–20y", "20+y"]
    return _build_contingency(duration, outcome, "Duration", col_order=None)
#print(get_duration_x_outcome(con))    



#print(get_expiry_x_duration(con))

#print(check_expected_frequencies(get_expiry_x_duration(con)))

#print(get_expiry_x_outcome(con))
# print(collapse_rare_columns(get_expiry_x_outcome(con)))
#print(remove_rel_freq(get_expiry_x_outcome(con)))