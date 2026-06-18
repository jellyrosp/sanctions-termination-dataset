from pathlib import Path
import sys
from itertools import islice
import io
from contextlib import redirect_stdout

# Project root: 3 levels up from this file
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
src_dir = BASE_DIR / "src"

if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from stats.bivariate import desc_analysis as desc
from stats import helpers as hlp


TABLE_FUNCS = {
    # Y=DURATION
    "expiry_x_duration": desc.get_expiry_x_duration,
    "review_x_duration": desc.get_review_x_duration,
    "req_termination_x_duration": desc.get_req_termination_x_duration,
    # Y=OUTCOME
    "expiry_x_outcome": desc.get_expiry_x_outcome,
    "review_x_outcome": desc.get_review_x_outcome,
    "req_termination_x_outcome": desc.get_req_termination_x_outcome,

    # Y=DURATION
    "gradual_x_duration": desc.get_gradual_x_duration,
    "negotiations_x_duration": desc.get_negotiations_x_duration,
    # Y=OUTCOME
    "gradual_x_outcome": desc.get_gradual_x_outcome,
    "adapt_goal_x_outcome": desc.get_adapt_goal_x_outcome,
    "negotiations_x_outcome": desc.get_negotiations_x_outcome,

    # Y=OUTCOME
    "multilateralism_x_outcome": desc.get_multilateralism_x_outcome,
    "duration_x_outcome": desc.get_duration_x_outcome,
}

tables = {name: func(desc.con) for name, func in TABLE_FUNCS.items()}

# Absolute frequencies and not-null values only
tables_cleaned = {
    name: hlp.normalize_table(table)
    for name, table in tables.items()
}


# Recoding OUTCOME values
outcome_mapping = {
    "Negotiated settlement":                                None,
    "Stalemate":                                            None,
    "Negotiated settlement & Sender capitulation":          "Sender capitulation",
    "Negotiated settlement & Target complete acquiescence": "Target complete acquiescence",
    "Negotiated settlement & Target partial acquiescence":  "Target partial acquiescence",
}



#############################################
# TABLES REFACTORING ########################
#############################################


# DURATION ####################

# expiry_x_duration PASSED 

# review_x_duration PASSED

# req_termination_x_duration PASSED


# OUTCOME ####################

# expiry_x_outcome PASSED
tables_cleaned["expiry_x_outcome"] = hlp.remap_columns(
    tables_cleaned["expiry_x_outcome"],
    mapping=outcome_mapping,
)
# review_x_outcome PASSED
tables_cleaned["review_x_outcome"] = hlp.remap_columns(
    tables_cleaned["review_x_outcome"],
    mapping=outcome_mapping,
)
# req_termination_x_outcome PASSED
tables_cleaned["req_termination_x_outcome"] = hlp.remap_columns(
    tables_cleaned["req_termination_x_outcome"],
    mapping=outcome_mapping,
)


# DURATION ####################

# gradual_x_duration PASSED

# negotiations_x_duration PASSED


# OUTCOME ####################

# gradual_x_outcome PASSED
tables_cleaned["gradual_x_outcome"] = hlp.remap_columns(
    tables_cleaned["gradual_x_outcome"],
    mapping=outcome_mapping,
)

# adapt_goal_x_outcome PASSED
tables_cleaned["adapt_goal_x_outcome"] = hlp.remap_columns(
    tables_cleaned["adapt_goal_x_outcome"],
    mapping=outcome_mapping,
)

# negotiations_x_outcome PASSED
tables_cleaned["negotiations_x_outcome"] = hlp.remap_columns(
    tables_cleaned["negotiations_x_outcome"],
    mapping=outcome_mapping,
)


# OUTCOME ####################

# multilateralism_x_outcome
tables_cleaned["multilateralism_x_outcome"] = hlp.remap_columns(
    tables_cleaned["multilateralism_x_outcome"],
    mapping=outcome_mapping,
)

# duration_x_outcome PASSED
tables_cleaned["duration_x_outcome"] = hlp.remap_columns(
    tables_cleaned["duration_x_outcome"],
    mapping=outcome_mapping,
)
rows_to_remove = {"20+y":None}
tables_cleaned["duration_x_outcome"] = hlp.remap_rows(
    tables_cleaned["duration_x_outcome"],
    mapping=rows_to_remove,
)




#print(tables_cleaned["multilateralism_x_outcome"])



