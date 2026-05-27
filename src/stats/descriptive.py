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
        SELECT
            rc.case_id,
            rc.start_date,
            rc.ter_date,
            rc.ongoing,
            s.decod  AS sender,
            t.decod  AS target
        FROM RegimeCase rc
        LEFT JOIN Case_Sender cs ON rc.case_id = cs.case_id
        LEFT JOIN Sender s       ON cs.sender_id = s.sender_id
        LEFT JOIN Case_Target ct ON rc.case_id = ct.case_id
        LEFT JOIN Target t       ON ct.target_id = t.target_id
    """
    return query(sql, con)