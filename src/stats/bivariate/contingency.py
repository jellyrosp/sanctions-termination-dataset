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
    "eq_termination_x_outcome": desc.get_req_termination_x_outcome,
    # Y= SENDER
    "expiry_x_sender": desc.get_expiry_x_sender,
    "review_x_sender": desc.get_review_x_sender,
    "req_termination_x_sender": desc.get_req_termination_x_sender,


    # Y=DURATION
    "gradual_x_duration": desc.get_gradual_x_duration,
    "adapt_goal_x_duration": desc.get_adapt_goal_x_duration,
    "negotiations_x_duration": desc.get_negotiations_x_duration,
    # Y=OUTCOME
    "gradual_x_outcome": desc.get_gradual_x_outcome,
    "adapt_goal_x_outcome": desc.get_adapt_goal_x_outcome,
    "negotiations_x_outcome": desc.get_negotiations_x_outcome,
    # Y= SENDER
    "gradual_x_sender": desc.get_gradual_x_sender,
    "adapt_goal_x_sender": desc.get_adapt_goal_x_sender,
    "negotiations_x_sender": desc.get_negotiations_x_sender,

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




report_path = BASE_DIR / "expected_freq_report.txt"

with open(report_path, "w", encoding="utf-8") as f:
    for name, table in tables_cleaned.items():
        buf = io.StringIO()
        with redirect_stdout(buf):
            hlp.check_expected_frequencies(table, verbose=True)
        f.write(f"{'#' * 65}\n")
        f.write(f"# TABLE: {name}\n")
        f.write(f"{'#' * 65}\n\n")
        f.write(buf.getvalue())
        f.write("\n")


expiry_x_outcome = tables_cleaned["expiry_x_outcome"]

with open("expiry_x_outcome.txt", "w", encoding="utf-8") as f:
    f.write(expiry_x_outcome.to_string())



# print(hlp.check_expected_frequencies(expiry_x_outcome))
# expiry_x_outcome_pruned = hlp.collapse_rare_columns(expiry_x_outcome, keep_total=False)

# print(expiry_x_outcome_pruned)

# print(hlp.check_expected_frequencies(expiry_x_outcome_pruned))


# tables_pruned = {}
# status_lines = []

# for name, table in tables_cleaned.items():
#     ok = hlp.check_expected_frequencies(table, verbose=False)

#     if ok:
#         tables_pruned[name] = table
#         status_lines.append(f"{name}: passed_first_test")
#     else:
#         collapsed = hlp.collapse_rare_columns(table, keep_total=False)
#         ok2 = hlp.check_expected_frequencies(collapsed, verbose=False)

#         if ok2:
#             tables_pruned[name] = collapsed
#             status_lines.append(f"{name}: passed_after_collapse")
#         else:
#             tables_pruned[name] = table
#             status_lines.append(f"{name}: failed_kept_original")

# report_path = BASE_DIR / "tables_pruned_status.txt"

# with open(report_path, "w", encoding="utf-8") as f:
#     f.write("\n".join(status_lines))
#     f.write("\n")







# expiry_x_outcome = tables_cleaned["expiry_x_outcome"]

# print(hlp.collapse_rare_columns(expiry_x_outcome))




# with open("expiry_x_outcome.txt", "w", encoding="utf-8") as f:
#     f.write(expiry_x_outcome.to_string())
# print("")
# print(hlp.check_expected_frequencies(tables_cleaned["expiry_x_outcome"]))



# output_lines = []

# results = {}
# for name, table in tables_cleaned.items():
#     buf = io.StringIO()
#     with redirect_stdout(buf):
#         passed = hlp.check_expected_frequencies(table, verbose=True)
#     output_lines.append(f"### {name}")
#     output_lines.append(buf.getvalue())
#     output_lines.append(f"  → Returned: {'PASS ✅' if passed else 'FAIL ❌'}\n")
#     results[name] = passed

# output_path = BASE_DIR / "expected_freq_check.txt"
# output_path.parent.mkdir(parents=True, exist_ok=True)

# with open(output_path, "w", encoding="utf-8") as f:
#     f.write("\n".join(output_lines))

# print(f"Written to: {output_path}")
# print(f"\nSummary: {sum(results.values())} / {len(results)} tables passed")




