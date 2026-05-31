import sqlite3
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def query(sql: str, con: sqlite3.Connection) -> pd.DataFrame:
    """Execute SQL and return results as a DataFrame."""
    return pd.read_sql_query(sql, con)    



def get_cases_overview(con: sqlite3.Connection) -> pd.DataFrame:
    """textual description."""
    sql = """
        WITH valid_cases AS (
    SELECT DISTINCT case_id
    FROM RegimeCase
    WHERE ter_date IS NOT NULL
       OR de_facto_ter IS NOT NULL
       OR ongoing = 1
),
sender_totals AS (
    SELECT
        s.decod AS sender,
        COUNT(DISTINCT vc.case_id) AS total_cases,
        SUM(CASE WHEN rc.ter_date IS NOT NULL THEN 1 ELSE 0 END) AS total_ter_date,
        SUM(CASE WHEN rc.de_facto_ter IS NOT NULL THEN 1 ELSE 0 END) AS total_de_facto_ter,
        SUM(CASE WHEN rc.ongoing = 1 THEN 1 ELSE 0 END) AS total_ongoing
    FROM valid_cases vc
    JOIN Case_Sender cs ON vc.case_id = cs.case_id
    JOIN Sender s ON cs.sender_id = s.sender_id
    JOIN RegimeCase rc ON vc.case_id = rc.case_id
    GROUP BY s.decod
)
SELECT
    sender,
    total_cases,
    total_ter_date,
    total_de_facto_ter,
    total_ongoing
FROM sender_totals
UNION ALL
SELECT
    'TOTAL' AS sender,
    SUM(total_cases) AS total_cases,
    SUM(total_ter_date) AS total_ter_date,
    SUM(total_de_facto_ter) AS total_de_facto_ter,
    SUM(total_ongoing) AS total_ongoing
FROM sender_totals
ORDER BY sender DESC;
    """
    return query(sql, con)


def get_calculate_duration(con: sqlite3.Connection) -> pd.DataFrame:
    """textual description."""
    sql = """
    SELECT
    s.decod AS sender,
    CASE
        WHEN rc.ongoing = 1 THEN
            CASE
                WHEN (julianday('2018-12-31') - julianday(rc.start_date)) / 365.25 < 0.5 THEN '0–6 months'
                WHEN (julianday('2018-12-31') - julianday(rc.start_date)) / 365.25 < 1 THEN '6 months–1 year'
                WHEN (julianday('2018-12-31') - julianday(rc.start_date)) / 365.25 < 2 THEN '1–2 years'
                WHEN (julianday('2018-12-31') - julianday(rc.start_date)) / 365.25 < 5 THEN '2–5 years'
                WHEN (julianday('2018-12-31') - julianday(rc.start_date)) / 365.25 < 10 THEN '5–10 years'
                WHEN (julianday('2018-12-31') - julianday(rc.start_date)) / 365.25 < 20 THEN '10–20 years'
                ELSE '20+ years'
            END
        ELSE
            CASE
                WHEN (julianday(rc.ter_date) - julianday(rc.start_date)) / 365.25 < 0.5 THEN '0–6 months'
                WHEN (julianday(rc.ter_date) - julianday(rc.start_date)) / 365.25 < 1 THEN '6 months–1 year'
                WHEN (julianday(rc.ter_date) - julianday(rc.start_date)) / 365.25 < 2 THEN '1–2 years'
                WHEN (julianday(rc.ter_date) - julianday(rc.start_date)) / 365.25 < 5 THEN '2–5 years'
                WHEN (julianday(rc.ter_date) - julianday(rc.start_date)) / 365.25 < 10 THEN '5–10 years'
                WHEN (julianday(rc.ter_date) - julianday(rc.start_date)) / 365.25 < 20 THEN '10–20 years'
                ELSE '20+ years'
            END
        END AS duration_range,
    COUNT(DISTINCT rc.case_id) AS case_frequency
FROM
    RegimeCase rc
JOIN
    Case_Sender cs ON rc.case_id = cs.case_id
JOIN
    Sender s ON cs.sender_id = s.sender_id
WHERE
    rc.ter_date IS NOT NULL
    OR rc.ongoing = 1
GROUP BY
    s.decod, duration_range
ORDER BY
    s.decod, duration_range;
    """
    return query(sql, con)


def get_gradual_termination_distribution(con: sqlite3.Connection) -> pd.DataFrame:
    """textual description."""
    sql = """
    WITH valid_cases AS (
    SELECT DISTINCT case_id
    FROM RegimeCase
    WHERE gradual IS NOT NULL
),
sender_totals AS (
    SELECT
        s.decod AS sender,
        COUNT(DISTINCT CASE WHEN rc.gradual = 1 THEN vc.case_id END) AS gradual_yes,
        COUNT(DISTINCT CASE WHEN rc.gradual = 0 THEN vc.case_id END) AS gradual_no,
        COUNT(DISTINCT vc.case_id) AS total_cases
    FROM valid_cases vc
    JOIN Case_Sender cs ON vc.case_id = cs.case_id
    JOIN Sender s ON cs.sender_id = s.sender_id
    JOIN RegimeCase rc ON vc.case_id = rc.case_id
    GROUP BY s.decod
)
SELECT
    sender,
    gradual_yes,
    gradual_no,
    total_cases
FROM sender_totals
UNION ALL
SELECT
    'TOTAL' AS sender,
    SUM(gradual_yes) AS gradual_yes,
    SUM(gradual_no) AS gradual_no,
    SUM(total_cases) AS total_cases
FROM sender_totals
ORDER BY sender DESC;
    """
    return query(sql, con)


def get_expiry_date_distribution(con: sqlite3.Connection) -> pd.DataFrame:
    """textual description."""
    sql = """
    WITH valid_cases AS (
    SELECT DISTINCT case_id
    FROM RegimeCase
    WHERE expiry IS NOT NULL
),
sender_totals AS (
    SELECT
        s.decod AS sender,
        COUNT(DISTINCT CASE WHEN rc.expiry = 1 THEN vc.case_id END) AS expiry_yes,
        COUNT(DISTINCT CASE WHEN rc.expiry = 0 THEN vc.case_id END) AS expiry_no,
        COUNT(DISTINCT vc.case_id) AS total_cases
    FROM valid_cases vc
    JOIN Case_Sender cs ON vc.case_id = cs.case_id
    JOIN Sender s ON cs.sender_id = s.sender_id
    JOIN RegimeCase rc ON vc.case_id = rc.case_id
    GROUP BY s.decod
)
SELECT
    sender,
    expiry_yes,
    expiry_no,
    total_cases
FROM sender_totals
UNION ALL
SELECT
    'TOTAL' AS sender,
    SUM(expiry_yes) AS expiry_yes,
    SUM(expiry_no) AS expiry_no,
    SUM(total_cases) AS total_cases
FROM sender_totals
ORDER BY sender DESC;
    """
    return query(sql, con)

def get_review_distribution(con: sqlite3.Connection) -> pd.DataFrame:
    """textual description."""
    sql = """
   WITH valid_cases AS (
    SELECT DISTINCT case_id
    FROM RegimeCase
    WHERE review IS NOT NULL
),
sender_totals AS (
    SELECT
        s.decod AS sender,
        COUNT(DISTINCT CASE WHEN rc.review = 1 THEN vc.case_id END) AS review_yes,
        COUNT(DISTINCT CASE WHEN rc.review = 0 THEN vc.case_id END) AS review_no,
        COUNT(DISTINCT vc.case_id) AS total_cases
    FROM valid_cases vc
    JOIN Case_Sender cs ON vc.case_id = cs.case_id
    JOIN Sender s ON cs.sender_id = s.sender_id
    JOIN RegimeCase rc ON vc.case_id = rc.case_id
    GROUP BY s.decod
)
SELECT
    sender,
    review_yes,
    review_no,
    total_cases
FROM sender_totals
UNION ALL
SELECT
    'TOTAL' AS sender,
    SUM(review_yes) AS review_yes,
    SUM(review_no) AS review_no,
    SUM(total_cases) AS total_cases
FROM sender_totals
ORDER BY sender DESC;
    """
    return query(sql, con)



def get_measure_distribution_per_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """textual description."""
    sql = """
    SELECT
    s.decod AS sender,
    m.decod AS measure,
    COUNT(DISTINCT cm.case_id) AS case_count
FROM
    Case_Measure cm
JOIN
    RegimeCase rc ON cm.case_id = rc.case_id
JOIN
    Case_Sender cs ON rc.case_id = cs.case_id
JOIN
    Sender s ON cs.sender_id = s.sender_id
JOIN
    Measure m ON cm.measure_id = m.measure_id
GROUP BY
    s.decod, m.decod
ORDER BY
    s.decod, m.decod;
    """
    return query(sql, con)



def get_measure_distribution(con: sqlite3.Connection) -> pd.DataFrame:
    """textual description."""
    sql = """
    SELECT
    m.decod AS measure,
    COUNT(DISTINCT cm.case_id) AS case_count
FROM
    Case_Measure cm
JOIN
    Measure m ON cm.measure_id = m.measure_id
GROUP BY
    m.decod
ORDER BY
    case_count DESC, m.decod;
    """
    return query(sql, con)


def get_measure_distribution_range(con: sqlite3.Connection) -> pd.DataFrame:
    """textual description."""
    sql = """
    WITH measure_counts AS (
    SELECT
        cs.sender_id,
        rc.case_id,
        COUNT(cm.measure_id) AS measure_count
    FROM RegimeCase rc
    JOIN Case_Sender cs ON rc.case_id = cs.case_id
    JOIN Case_Measure cm ON rc.case_id = cm.case_id
    GROUP BY cs.sender_id, rc.case_id
),
sender_totals AS (
    SELECT
        TRIM(s.decod) AS sender,
        COUNT(CASE WHEN mc.measure_count <= 2 THEN mc.case_id END) AS up_to_2_measures,
        COUNT(CASE WHEN mc.measure_count > 2 AND mc.measure_count <= 5 THEN mc.case_id END) AS up_to_5_measures,
        COUNT(CASE WHEN mc.measure_count > 5 AND mc.measure_count <= 8 THEN mc.case_id END) AS up_to_8_measures,
        COUNT(CASE WHEN mc.measure_count > 8 AND mc.measure_count <= 11 THEN mc.case_id END) AS up_to_11_measures,
        COUNT(mc.case_id) AS total_cases
    FROM Sender s
    LEFT JOIN measure_counts mc ON TRIM(s.sender_id) = TRIM(mc.sender_id)
    GROUP BY TRIM(s.decod)
)
SELECT
    sender,
    up_to_2_measures,
    up_to_5_measures,
    up_to_8_measures,
    up_to_11_measures,
    total_cases
FROM sender_totals

UNION ALL

SELECT
    'TOTAL',
    SUM(up_to_2_measures),
    SUM(up_to_5_measures),
    SUM(up_to_8_measures),
    SUM(up_to_11_measures),
    (SELECT COUNT(*) FROM Case_Sender)
FROM sender_totals

ORDER BY sender DESC;
    """
    return query(sql, con)



def get_goal_distribution(con: sqlite3.Connection) -> pd.DataFrame:
    """textual description."""
    sql = """
    SELECT
    g.decod AS goal,
    COUNT(DISTINCT cg.case_id) AS case_count
FROM
    Case_Goal cg
JOIN
    Goal g ON cg.goal_id = g.goal_id
GROUP BY
    g.decod
ORDER BY
    case_count DESC, g.decod;
    """
    return query(sql, con)


def get_goal_distribution_per_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """textual description."""
    sql = """
    SELECT
    s.decod AS sender,
    g.decod AS goal,
    COUNT(DISTINCT cg.case_id) AS case_count
FROM
    Case_Goal cg
JOIN
    RegimeCase rc ON cg.case_id = rc.case_id
JOIN
    Case_Sender cs ON rc.case_id = cs.case_id
JOIN
    Sender s ON cs.sender_id = s.sender_id
JOIN
    Goal g ON cg.goal_id = g.goal_id
GROUP BY
    s.decod, g.decod
ORDER BY
    s.decod, g.decod;
    """
    return query(sql, con)


def get_goal_distribution_range(con: sqlite3.Connection) -> pd.DataFrame:
    """textual description."""
    sql = """
    WITH goal_counts AS (
    SELECT
        cs.sender_id,
        rc.case_id,
        COUNT(cg.goal_id) AS goal_count
    FROM RegimeCase rc
    JOIN Case_Sender cs ON rc.case_id = cs.case_id
    JOIN Case_Goal cg ON rc.case_id = cg.case_id
    GROUP BY cs.sender_id, rc.case_id
),
sender_totals AS (
    SELECT
        TRIM(s.decod) AS sender,
        COUNT(CASE WHEN gc.goal_count <= 2 THEN gc.case_id END) AS up_to_2_goals,
        COUNT(CASE WHEN gc.goal_count > 2 AND gc.goal_count <= 5 THEN gc.case_id END) AS up_to_5_goals,
        COUNT(CASE WHEN gc.goal_count > 5 AND gc.goal_count <= 8 THEN gc.case_id END) AS up_to_8_goals,
        COUNT(gc.case_id) AS total_cases
    FROM Sender s
    LEFT JOIN goal_counts gc ON TRIM(s.sender_id) = TRIM(gc.sender_id)
    GROUP BY TRIM(s.decod)
)
SELECT
    sender,
    up_to_2_goals,
    up_to_5_goals,
    up_to_8_goals,
    total_cases
FROM sender_totals

UNION ALL

SELECT
    'TOTAL',
    SUM(up_to_2_goals),
    SUM(up_to_5_goals),
    SUM(up_to_8_goals),
    (SELECT COUNT(*) FROM Case_Sender)
FROM sender_totals

ORDER BY sender DESC;
    """
    return query(sql, con)


def get_adapt_goal_distribution_per_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """textual description."""
    sql = """
    WITH valid_cases AS (
    SELECT DISTINCT case_id
    FROM Case_Goal
    WHERE adapt_goal IS NOT NULL
),
sender_totals AS (
    SELECT
        s.decod AS sender,
        COUNT(DISTINCT CASE WHEN cg.adapt_goal = 1 THEN vc.case_id END) AS adapt_goal_yes,
        COUNT(DISTINCT CASE WHEN cg.adapt_goal = 0 THEN vc.case_id END) AS adapt_goal_no,
        COUNT(DISTINCT vc.case_id) AS total_cases
    FROM valid_cases vc
    JOIN Case_Sender cs ON vc.case_id = cs.case_id
    JOIN Sender s ON cs.sender_id = s.sender_id
    JOIN Case_Goal cg ON vc.case_id = cg.case_id
    GROUP BY s.decod
)
SELECT
    sender,
    adapt_goal_yes,
    adapt_goal_no,
    total_cases
FROM sender_totals
UNION ALL
SELECT
    'TOTAL' AS sender,
    SUM(adapt_goal_yes) AS adapt_goal_yes,
    SUM(adapt_goal_no) AS adapt_goal_no,
    SUM(total_cases) AS total_cases
FROM sender_totals
ORDER BY sender DESC;
    """
    return query(sql, con)

def get_target_salience_distribution_per_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """textual description."""
    sql = """
    WITH valid_cases AS (
    SELECT DISTINCT case_id
    FROM RegimeCase
    WHERE target_salience IS NOT NULL
),
sender_totals AS (
    SELECT
        s.decod AS sender,
        COUNT(DISTINCT CASE WHEN rc.target_salience = 1 THEN vc.case_id END) AS target_salience_yes,
        COUNT(DISTINCT CASE WHEN rc.target_salience = 0 THEN vc.case_id END) AS target_salience_no,
        COUNT(DISTINCT vc.case_id) AS total_cases
    FROM valid_cases vc
    JOIN Case_Sender cs ON vc.case_id = cs.case_id
    JOIN Sender s ON cs.sender_id = s.sender_id
    JOIN RegimeCase rc ON vc.case_id = rc.case_id
    GROUP BY s.decod
)
SELECT
    sender,
    target_salience_yes,
    target_salience_no,
    total_cases
FROM sender_totals
UNION ALL
SELECT
    'TOTAL' AS sender,
    SUM(target_salience_yes) AS target_salience_yes,
    SUM(target_salience_no) AS target_salience_no,
    SUM(total_cases) AS total_cases
FROM sender_totals
ORDER BY sender DESC;
    """
    return query(sql, con)



def get_sender_salience_distribution_per_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """textual description."""
    sql = """
    WITH valid_cases AS (
    SELECT DISTINCT case_id
    FROM RegimeCase
    WHERE sender_salience IS NOT NULL
),
sender_totals AS (
    SELECT
        s.decod AS sender,
        COUNT(DISTINCT CASE WHEN rc.sender_salience = 1 THEN vc.case_id END) AS sender_salience_yes,
        COUNT(DISTINCT CASE WHEN rc.sender_salience = 0 THEN vc.case_id END) AS sender_salience_no,
        COUNT(DISTINCT vc.case_id) AS total_cases
    FROM valid_cases vc
    JOIN Case_Sender cs ON vc.case_id = cs.case_id
    JOIN Sender s ON cs.sender_id = s.sender_id
    JOIN RegimeCase rc ON vc.case_id = rc.case_id
    GROUP BY s.decod
)
SELECT
    sender,
    sender_salience_yes,
    sender_salience_no,
    total_cases
FROM sender_totals
UNION ALL
SELECT
    'TOTAL' AS sender,
    SUM(sender_salience_yes) AS sender_salience_yes,
    SUM(sender_salience_no) AS sender_salience_no,
    SUM(total_cases) AS total_cases
FROM sender_totals
ORDER BY sender DESC;
    """
    return query(sql, con)

def get_requirement_termination_distribution_per_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """textual description."""
    sql = """
SELECT 
    s.decod AS Sender,
    SUM(CASE WHEN TRIM(rc.requirement_termination) = 'Ambiguous' THEN 1 ELSE 0 END) AS Ambiguous,
    SUM(CASE WHEN TRIM(rc.requirement_termination) = 'Clear' THEN 1 ELSE 0 END) AS Clear,
    SUM(CASE WHEN TRIM(rc.requirement_termination) = 'missing' THEN 1 ELSE 0 END) AS Missing,
    COUNT(*) AS Total
FROM RegimeCase rc
JOIN Case_Sender cs ON rc.case_id = cs.case_id
JOIN Sender s ON cs.sender_id = s.sender_id
GROUP BY s.sender_id, s.decod

UNION ALL

SELECT 
    'TOTAL',
    SUM(CASE WHEN TRIM(rc.requirement_termination) = 'Ambiguous' THEN 1 ELSE 0 END),
    SUM(CASE WHEN TRIM(rc.requirement_termination) = 'Clear' THEN 1 ELSE 0 END),
    SUM(CASE WHEN TRIM(rc.requirement_termination) = 'missing' THEN 1 ELSE 0 END),
    COUNT(*)
FROM RegimeCase rc
JOIN Case_Sender cs ON rc.case_id = cs.case_id
JOIN Sender s ON cs.sender_id = s.sender_id

ORDER BY Sender;
 """
    return query(sql, con)

def get_negotiations_distribution_per_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """textual description."""
    sql = """
    WITH valid_cases AS (
    SELECT DISTINCT case_id
    FROM RegimeCase
    WHERE negotiations IS NOT NULL
),
sender_totals AS (
    SELECT
        s.decod AS sender,
        COUNT(DISTINCT CASE WHEN rc.negotiations = 1 THEN vc.case_id END) AS negotiations_yes,
        COUNT(DISTINCT CASE WHEN rc.negotiations = 0 THEN vc.case_id END) AS negotiations_no,
        COUNT(DISTINCT vc.case_id) AS total_cases
    FROM valid_cases vc
    JOIN Case_Sender cs ON vc.case_id = cs.case_id
    JOIN Sender s ON cs.sender_id = s.sender_id
    JOIN RegimeCase rc ON vc.case_id = rc.case_id
    GROUP BY s.decod
)
SELECT
    sender,
    negotiations_yes,
    negotiations_no,
    total_cases
FROM sender_totals
UNION ALL
SELECT
    'TOTAL' AS sender,
    SUM(negotiations_yes) AS negotiations_yes,
    SUM(negotiations_no) AS negotiations_no,
    SUM(total_cases) AS total_cases
FROM sender_totals
ORDER BY sender DESC;
    """
    return query(sql, con)


def get_inst_investment_distribution_per_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """textual description."""
    sql = """
    WITH valid_cases AS (
    SELECT DISTINCT case_id
    FROM RegimeCase
    WHERE inst_investment IS NOT NULL
),
sender_totals AS (
    SELECT
        s.decod AS sender,
        COUNT(DISTINCT CASE WHEN rc.inst_investment = 1 THEN vc.case_id END) AS inst_investment_yes,
        COUNT(DISTINCT CASE WHEN rc.inst_investment = 0 THEN vc.case_id END) AS inst_investment_no,
        COUNT(DISTINCT vc.case_id) AS total_cases
    FROM valid_cases vc
    JOIN Case_Sender cs ON vc.case_id = cs.case_id
    JOIN Sender s ON cs.sender_id = s.sender_id
    JOIN RegimeCase rc ON vc.case_id = rc.case_id
    GROUP BY s.decod
)
SELECT
    sender,
    inst_investment_yes,
    inst_investment_no,
    total_cases
FROM sender_totals
UNION ALL
SELECT
    'TOTAL' AS sender,
    SUM(inst_investment_yes) AS inst_investment_yes,
    SUM(inst_investment_no) AS inst_investment_no,
    SUM(total_cases) AS total_cases
FROM sender_totals
ORDER BY sender DESC;
"""
    return query(sql, con)

def get_outcomes_distribution_per_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """textual description."""
    sql = """
WITH sender_totals AS (
    SELECT
        TRIM(s.decod) AS sender,
        COUNT(CASE WHEN TRIM(co.outcome_type) = 'Blank' THEN co.case_id END) AS Blank,
        COUNT(CASE WHEN TRIM(co.outcome_type) = 'Negotiated settlement' THEN co.case_id END) AS Negotiated_settlement,
        COUNT(CASE WHEN TRIM(co.outcome_type) = 'Sender capitulation' THEN co.case_id END) AS Sender_capitulation,
        COUNT(CASE WHEN TRIM(co.outcome_type) = 'Stalemate' THEN co.case_id END) AS Stalemate,
        COUNT(CASE WHEN TRIM(co.outcome_type) = 'Target complete acquiescence' THEN co.case_id END) AS Target_complete_acquiescence,
        COUNT(CASE WHEN TRIM(co.outcome_type) = 'Target partial acquiescence' THEN co.case_id END) AS Target_partial_acquiescence,
        COUNT(co.case_id) AS total_cases
    FROM Sender s
    LEFT JOIN Case_Sender cs ON TRIM(s.sender_id) = TRIM(cs.sender_id)
    LEFT JOIN Case_Outcome co ON cs.case_id = co.case_id
    GROUP BY TRIM(s.decod)
)
SELECT
    sender,
    Blank,
    Negotiated_settlement,
    Sender_capitulation,
    Stalemate,
    Target_complete_acquiescence,
    Target_partial_acquiescence,
    total_cases
FROM sender_totals

UNION ALL

SELECT
    'TOTAL',
    SUM(Blank),
    SUM(Negotiated_settlement),
    SUM(Sender_capitulation),
    SUM(Stalemate),
    SUM(Target_complete_acquiescence),
    SUM(Target_partial_acquiescence),
    (SELECT COUNT(*) FROM Case_Sender)
FROM sender_totals

ORDER BY sender DESC;
"""
    return query(sql, con)


def get_cost_sender_distribution_per_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """textual description."""
    sql = """
WITH sender_totals AS (
    SELECT
        TRIM(s.decod) AS sender,
        COUNT(CASE WHEN TRIM(rc.cost_sender) = 'Blank' THEN rc.case_id END) AS Blank,
        COUNT(CASE WHEN TRIM(rc.cost_sender) = 'Minor' THEN rc.case_id END) AS Minor,
        COUNT(CASE WHEN TRIM(rc.cost_sender) = 'Major' THEN rc.case_id END) AS Major,
        COUNT(rc.case_id) AS total_cases
    FROM Sender s
    LEFT JOIN Case_Sender cs ON TRIM(s.sender_id) = TRIM(cs.sender_id)
    LEFT JOIN RegimeCase rc ON cs.case_id = rc.case_id
    GROUP BY TRIM(s.decod)
)
SELECT
    sender,
    Blank,
    Minor,
    Major,
    total_cases
FROM sender_totals

UNION ALL

SELECT
    'TOTAL',
    SUM(Blank),
    SUM(Minor),
    SUM(Major),
    (SELECT COUNT(*) FROM Case_Sender)
FROM sender_totals

ORDER BY sender DESC;
"""
    return query(sql, con)


def get_cost_target_distribution_per_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """textual description."""
    sql = """
WITH sender_totals AS (
    SELECT
        TRIM(s.decod) AS sender,
        COUNT(CASE WHEN TRIM(rc.cost_target) = 'Minor' THEN rc.case_id END) AS Minor,
        COUNT(CASE WHEN TRIM(rc.cost_target) = 'Major' THEN rc.case_id END) AS Major,
        COUNT(CASE WHEN TRIM(rc.cost_target) = 'Severe' THEN rc.case_id END) AS Severe,
        COUNT(rc.case_id) AS total_cases
    FROM Sender s
    LEFT JOIN Case_Sender cs ON TRIM(s.sender_id) = TRIM(cs.sender_id)
    LEFT JOIN RegimeCase rc ON cs.case_id = rc.case_id
    GROUP BY TRIM(s.decod)
)
SELECT
    sender,
    Minor,
    Major,
    Severe,
    total_cases
FROM sender_totals

UNION ALL

SELECT
    'TOTAL',
    SUM(Minor),
    SUM(Major),
    SUM(Severe),
    (SELECT COUNT(*) FROM Case_Sender)
FROM sender_totals

ORDER BY sender DESC;
"""
    return query(sql, con)


def get_multilateralism_distribution_per_sender(con: sqlite3.Connection) -> pd.DataFrame:
    """textual description."""
    sql = """
WITH multi_counts AS (
    SELECT
        TRIM(cs.sender_id) AS sender_id,
        TRIM(cm.case_id) AS case_id,
        COUNT(TRIM(cm.multilateralism_id)) AS multi_count
    FROM Case_Multilateralism cm
    JOIN Case_Sender cs ON TRIM(cm.case_id) = TRIM(cs.case_id)
    GROUP BY TRIM(cs.sender_id), TRIM(cm.case_id)
),
sender_totals AS (
    SELECT
        TRIM(s.decod) AS sender,
        COUNT(CASE WHEN mc.multi_count = 1 THEN mc.case_id END) AS unilateral,
        COUNT(CASE WHEN mc.multi_count > 1 THEN mc.case_id END) AS multilateral,
        COUNT(mc.case_id) AS total_cases
    FROM Sender s
    LEFT JOIN multi_counts mc ON TRIM(s.sender_id) = mc.sender_id
    GROUP BY TRIM(s.decod)
)
SELECT
    sender,
    unilateral,
    multilateral,
    total_cases
FROM sender_totals

UNION ALL

SELECT
    'TOTAL',
    SUM(unilateral),
    SUM(multilateral),
    (SELECT COUNT(*) FROM Case_Sender)
FROM sender_totals

ORDER BY sender DESC;
"""
    return query(sql, con)