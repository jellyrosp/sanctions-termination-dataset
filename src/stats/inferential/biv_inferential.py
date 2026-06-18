"""
===============
Step 1 — Bivariate inferential tests.

.
"""

from pathlib import Path
import sys

import numpy as np
import pandas as pd
from scipy import stats as sstats

# ── path setup (mirrors contingency.py) ──────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
src_dir = BASE_DIR / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from stats import helpers as hlp
from stats.bivariate import contingency as ct


# ──────────────────────────────────────────────────────────────────────────
# 1. IV CLASSIFICATION
# ──────────────────────────────────────────────────────────────────────────
# Maps each table name (as produced in contingency.TABLE_FUNCS) to the
# variable type of its IV, which determines which test gets run.
#
# Types:
#   "boolean"  -> 2 levels, Missing already dropped (e.g. Clear/Ambiguous)
#   "nominal"  -> >=2 unordered categorical levels
#   "ordinal"  -> >=3 ordered categorical levels (natural ordering exists)
#
# All IVs below are confirmed boolean (2 levels, Missing dropped).
# duration_x_outcome is the exception: duration itself is ordinal here,
# entered as the IV against nominal outcome (Test 5).

IV_TYPES = {
    # Y = DURATION
    "expiry_x_duration":            "boolean",
    "review_x_duration":            "boolean",
    "req_termination_x_duration":   "boolean",
    "gradual_x_duration":           "boolean",
    "negotiations_x_duration":      "boolean",

    # Y = OUTCOME (all chi-square + Cramer's V regardless of IV type)
    "expiry_x_outcome":             "boolean",
    "review_x_outcome":             "boolean",
    "req_termination_x_outcome":    "boolean",
    "gradual_x_outcome":            "boolean",
    "adapt_goal_x_outcome":         "boolean",
    "negotiations_x_outcome":       "boolean",
    "multilateralism_x_outcome":    "boolean",
    "duration_x_outcome":           "ordinal",   # Test 5: duration as IV
}

# Tables whose DV is duration (ordinal) -- everything else is outcome (nominal)
DURATION_DV_TABLES = {
    "expiry_x_duration",
    "review_x_duration",
    "req_termination_x_duration",
    "gradual_x_duration",
    "negotiations_x_duration",
}


# ──────────────────────────────────────────────────────────────────────────
# 2. TEST IMPLEMENTATIONS
# ──────────────────────────────────────────────────────────────────────────

def run_chi_square(table: pd.DataFrame) -> dict:
    """Chi-square test of independence + Cramer's V. For nominal IV/DV pairs
    (outcome as DV, or duration-as-nominal-IV in Test 5)."""
    chi2, p, dof, expected = sstats.chi2_contingency(table)
    cramers_v = hlp.cramers_v(table, chi2=chi2)  # TODO confirm helper exists/signature
    return {
        "test": "chi-square",
        "statistic": chi2,
        "p_value": p,
        "dof": dof,
        "effect_size_name": "Cramer's V",
        "effect_size": cramers_v,
        "n": table.values.sum(),
    }


def run_cochran_armitage(table: pd.DataFrame) -> dict:
    """Cochran-Armitage trend test. For boolean IV (2 levels) x ordinal
    duration DV. Rows = IV levels (2), columns = ordered duration bins."""
    result = hlp.cochran_armitage(table)  # TODO confirm helper exists/signature
    return {
        "test": "Cochran-Armitage",
        "statistic": result["z"],
        "p_value": result["p_value"],
        "effect_size_name": "trend r",
        "effect_size": result.get("r"),
        "n": table.values.sum(),
    }



# ──────────────────────────────────────────────────────────────────────────
# 3. ROUTING
# ──────────────────────────────────────────────────────────────────────────

def route_test(name: str, table: pd.DataFrame) -> dict:
    """Pick the correct bivariate test for a given table based on its IV
    type and whether its DV is duration (ordinal) or outcome (nominal)."""
    iv_type = IV_TYPES.get(name)
    if iv_type is None:
        raise KeyError(f"No IV type registered for table '{name}' in IV_TYPES.")

    is_duration_dv = name in DURATION_DV_TABLES

    if not is_duration_dv:
        # outcome (nominal) is always chi-square + Cramer's V, regardless
        # of IV type -- includes Test 5's duration_x_outcome.
        return run_chi_square(table)

    # duration (ordinal) as DV: route by IV type
    if iv_type == "boolean":
        return run_cochran_armitage(table)
    elif iv_type == "ordinal":
        return run_jonckheere_terpstra(table)
    else:
        raise ValueError(f"Unrecognized IV type '{iv_type}' for table '{name}'.")


# ──────────────────────────────────────────────────────────────────────────
# 4. EXECUTION (script-style: runs on import)
# ──────────────────────────────────────────────────────────────────────────

results = {}
for name, table in ct.tables_cleaned.items():
    try:
        results[name] = route_test(name, table)
    except Exception as exc:
        results[name] = {"error": str(exc)}

results_df = pd.DataFrame.from_dict(results, orient="index")

if __name__ == "__main__":
    pd.set_option("display.width", 120)
    print(results_df)