import sqlite3
import pandas as pd
import decode
import numpy as np
from pathlib import Path
import sys


#  GENERAL==================================================
def query(sql: str, con: sqlite3.Connection) -> pd.DataFrame:
    """Execute SQL and return results as a DataFrame."""
    return pd.read_sql_query(sql, con)    


def _get_scalar_per_case(con: sqlite3.Connection, column: str) -> pd.Series:
    """
    Returns a Series indexed by case_id for any scalar RegimeCase column.
    """
    sql = f"SELECT case_id, {column} FROM RegimeCase"
    df = query(sql, con)
    return df.set_index("case_id")[column]


def _get_multilateralism_per_case(con: sqlite3.Connection) -> pd.Series:
    """
    Returns a Series indexed by case_id with collapsed multilateralism label.
    Multiple multilateralism values per case are collapsed into a sorted
    combination string.
    """
    sql = """
        SELECT case_id, multilateralism_id
        FROM Case_Multilateralism
    """
    df = query(sql, con)

    multilat_grouped = (
        df.groupby("case_id")["multilateralism_id"]
        .apply(lambda x: " & ".join(sorted(x)))
        .rename("multilateralism")
    )

    cases_sql = "SELECT case_id FROM RegimeCase"
    cases_df  = query(cases_sql, con)

    merged = cases_df.merge(multilat_grouped, on="case_id", how="left")
    merged["multilateralism"] = merged["multilateralism"].fillna("Missing")

    return merged.set_index("case_id")["multilateralism"]    


def _build_contingency(
    row_var: pd.Series,
    col_var: pd.Series,
    row_name: str,
    col_order: list[str] | None = None,
) -> pd.DataFrame:
    """
    Build a contingency table with absolute and relative frequencies
    from two case-level Series. Relative frequencies are row-wise.
    """
    df = pd.concat([row_var.rename("row"), col_var.rename("col")], axis=1).dropna()

    ct = (
        df.groupby(["row", "col"])
          .size()
          .unstack(fill_value=0)
    )
    ct.index.name = row_name

    if col_order:
        ct = ct.reindex(columns=col_order, fill_value=0)

    ct["Total"] = ct.sum(axis=1)

    total_row = ct.sum()
    ct = pd.concat([ct, total_row.to_frame().T])
    ct = ct.rename(index={0: "TOTAL"})

    col_cols = [c for c in ct.columns if c != "Total"]
    rel = ct[col_cols].div(ct["Total"], axis=0).mul(100).round(1)

    result = pd.DataFrame(index=ct.index)
    for c in col_cols:
        result[(c, "Abs.")] = ct[c]
        result[(c, "Rel(%)")] = rel[c]
    result[("Total", "")] = ct["Total"]

    result.columns = pd.MultiIndex.from_tuples(result.columns)

    return result

#  Y = DURATION==================================================
def _get_duration_per_case(con: sqlite3.Connection) -> pd.Series:
    """
    Returns a Series indexed by case_id with duration interval label.
    Reusable by any function needing duration at case level.
    """
    sql = """
        SELECT
            case_id,
            start_date,
            CASE
                WHEN ongoing = 1 THEN '2018-12-31'
                ELSE ter_date
            END AS end_date
        FROM RegimeCase
        WHERE start_date IS NOT NULL
          AND (ter_date IS NOT NULL OR ongoing = 1)
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
    return df.set_index("case_id")["interval"]



#  Y = OUTCOME==================================================    
def _get_outcome_per_case(con: sqlite3.Connection) -> pd.Series:
    """
    Returns a Series indexed by case_id with outcome combination label.
    Multiple outcomes per case are collapsed into a sorted combination string.
    Cases with no outcome are labelled 'No outcome recorded'.
    Reusable by any function needing outcome at case level.
    """
    outcome_sql = """
        SELECT co.case_id, o.outcome_type
        FROM Case_Outcome co
        JOIN Outcome o ON co.outcome_type = o.outcome_type
    """
    cases_sql = "SELECT case_id FROM RegimeCase"

    outcome_df = query(outcome_sql, con)
    cases_df   = query(cases_sql,   con)

    outcome_grouped = (
        outcome_df.groupby("case_id")["outcome_type"]
        .apply(lambda x: " & ".join(sorted(x)))
        .reset_index(name="outcome_combo")
    )

    df = cases_df.merge(outcome_grouped, on="case_id", how="left")
    df["outcome_combo"] = df["outcome_combo"].fillna("Missing")

    return df.set_index("case_id")["outcome_combo"]


#  Y = SENDER==================================================    
def _get_sender_per_case(con: sqlite3.Connection) -> pd.Series:
    """
    Returns a Series indexed by case_id with collapsed sender label.
    Multi-sender cases: (EEC, EU) → 'EEC & EU', others take single sender.
    Reusable by any function needing sender at case level.
    """
    sql = """
        SELECT cs.case_id, s.decod AS sender
        FROM Case_Sender cs
        JOIN Sender s ON cs.sender_id = s.sender_id
    """
    df = query(sql, con)

    sender_grouped = (
        df.groupby("case_id")["sender"]
        .apply(lambda x: "EEC & EU" if set(x) == {
            "european economic community - european community",
            "european union"
        } else x.iloc[0])
        .rename("sender")
    )

    return sender_grouped.map(lambda x: decode.SENDER_ABBREV.get(x, x))


def normalize_contingency(contingency_df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalizes a contingency table to a clean flat DataFrame of integer counts.
    
    - Flattens MultiIndex columns, keeping only Abs. counts
    - Drops Total and Missing rows/columns (case-insensitive)
    - Returns a plain DataFrame with string index and string columns
    """
    df = contingency_df.copy()

    # ── 1. Flatten MultiIndex: keep only Abs. columns ─────────────────────────
    if isinstance(df.columns, pd.MultiIndex):
        abs_cols = [(l0, l1) for l0, l1 in df.columns if l1 == "Abs."]
        df = df[abs_cols]
        df.columns = [l0 for l0, _ in abs_cols]

    # ── 2. Drop Total / Missing rows ──────────────────────────────────────────
    drop_rows = [i for i in df.index if str(i).strip().upper() in ("TOTAL", "MISSING")]
    df = df.drop(index=drop_rows)

    # ── 3. Drop Total / Missing columns ───────────────────────────────────────
    drop_cols = [c for c in df.columns if str(c).strip().upper() in ("TOTAL", "MISSING")]
    df = df.drop(columns=drop_cols)

    # ── 4. Cast to int ────────────────────────────────────────────────────────
    df = df.astype(int)

    return df


def check_expected_frequencies(
    contingency_df: pd.DataFrame,
    min_expected: float = 5.0,
    max_ratio_below: float | None = None,   # None → adaptive
    verbose: bool = True
) -> bool:
    """
    Validate chi-square expected-frequency assumptions.

    Thresholds adapt to table geometry:
      - 2×2 (df=1)  : all cells must be ≥ 5 (max_ratio_below = 0.0)
      - small tables (total_cells ≤ 9, but not 2×2): 20 % tolerance
      - medium tables (10–24 cells)                 : 15 % tolerance
      - large tables (≥ 25 cells)                   : 10 % tolerance

    The hard minimum (E ≥ 1.0 in every cell) is always enforced.
    For df=1 tables a Yates-correction warning is emitted regardless of pass/fail.

    Args:
        contingency_df : Observed-count contingency table.
        min_expected   : Soft threshold for "small expected count" (default 5.0).
        max_ratio_below: Override the adaptive ratio. Pass an explicit float to
                         replicate the old fixed-threshold behaviour.
        verbose        : Print the diagnostic report.

    Returns:
        True if the table meets the applicable expected-frequency criteria.
    """

    df = normalize_contingency(contingency_df)

    n_rows, n_cols = df.shape
    if n_rows < 2 or n_cols < 2:
        if verbose:
            print("⚠️  Table too small after stripping — need at least 2×2.")
        return False

    counts        = df.values.astype(float)
    grand_total   = counts.sum()
    row_totals    = counts.sum(axis=1)
    col_totals    = counts.sum(axis=0)
    expected      = np.outer(row_totals, col_totals) / grand_total

    total_cells   = expected.size
    dof           = (n_rows - 1) * (n_cols - 1)
    min_exp_val   = expected.min()
    n_below       = (expected < min_expected).sum()

    # ------------------------------------------------------------------ #
    #  Adaptive threshold selection                                        #
    # ------------------------------------------------------------------ #
    if max_ratio_below is not None:                    # caller override
        effective_ratio = max_ratio_below
        ratio_source    = "user-supplied"
    elif dof == 1:                                     # 2×2
        effective_ratio = 0.0
        ratio_source    = "adaptive (2×2: all cells must meet threshold)"
    elif total_cells <= 9:                             # up to ~3×3
        effective_ratio = 0.20
        ratio_source    = "adaptive (small table ≤ 9 cells)"
    elif total_cells <= 24:                            # up to ~4×6
        effective_ratio = 0.15
        ratio_source    = "adaptive (medium table 10–24 cells)"
    else:                                              # 5×5 and beyond
        effective_ratio = 0.10
        ratio_source    = "adaptive (large table ≥ 25 cells)"

    ratio_below = n_below / total_cells
    passed = (ratio_below <= effective_ratio) and (min_exp_val >= 1.0)

    if verbose:
        sep = "=" * 65
        print(sep)
        print("EXPECTED FREQUENCY CHECK")
        print(sep)
        print(f"  Table shape          : {n_rows} rows × {n_cols} cols "
              f"({total_cells} cells, df={dof})")
        print(f"  Grand total (N)      : {int(grand_total)}")
        print(f"  Threshold source     : {ratio_source}")
        print(f"  Cells below E={min_expected:<4}  : {n_below} / {total_cells} "
              f"({ratio_below:.1%})  [limit: {effective_ratio:.0%}]")
        print(f"  Minimum expected     : {min_exp_val:.2f}  "
              f"[hard minimum: 1.0]")
        print(f"  Result               : "
              f"{'✅ PASS — χ² valid' if passed else '❌ FAIL — use Fisher or collapse categories'}")

        if dof == 1:
            print(f"\n  ⚠️  df=1: consider Yates' continuity correction "
                  f"or Fisher's exact test even when this check passes.")

        if n_below > 0:
            col_w = 35
            print(f"\n  Cells with expected < {min_expected}:")
            print(f"  {'Row':<{col_w}} {'Col':<{col_w}} {'Expected':>10}")
            print("  " + "-" * (col_w * 2 + 12))
            rows_idx, cols_idx = np.where(expected < min_expected)
            for r, c in zip(rows_idx, cols_idx):
                print(f"  {str(df.index[r]):<{col_w}} "
                      f"{str(df.columns[c]):<{col_w}} "
                      f"{expected[r, c]:>10.2f}")

        print(sep)

    return passed


def collapse_rare_columns(
    df: pd.DataFrame,
    min_count: float = 5,
    other_label: str = "Other",
    drop_rows: list[str] | None = None,
    drop_cols: list[str] | None = None,
    keep_total: bool = False,
):
    """
    χ² preprocessing pipeline (ABS ONLY).

    - collapses rare columns into 'Other'
    - optionally drops specific rows/columns
    - returns absolute frequencies only
    """

    # ------------------------------------------------------------
    # 0. TOTAL handling
    # ------------------------------------------------------------
    has_total = "TOTAL" in df.index
    if has_total:
        df = df.drop(index="TOTAL")

    # ------------------------------------------------------------
    # 1. hard exclusions (explicit drops only, no Missing logic)
    # ------------------------------------------------------------
    drop_rows = set(drop_rows or [])
    drop_cols = set(drop_cols or [])

    df = df.drop(index=[r for r in drop_rows if r in df.index], errors="ignore")
    df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore")

    # ------------------------------------------------------------
    # 2. compute column marginals for collapsing decision
    # ------------------------------------------------------------
    col_totals = df.sum(axis=0)
    keep_cols  = [c for c in col_totals[col_totals >= min_count].index
                  if c not in drop_cols]

    # ------------------------------------------------------------
    # 3. collapse rare columns
    # ------------------------------------------------------------
    out = df[keep_cols].copy()

    remaining = [c for c in df.columns if c not in keep_cols]
    if remaining:
        out[other_label] = df[remaining].sum(axis=1)

    if out.shape[1] == 0:
        out[other_label] = df.sum(axis=1)

    # ------------------------------------------------------------
    # 4. TOTAL row (optional)
    # ------------------------------------------------------------
    if keep_total:
        total_row = out.sum(axis=0).to_frame("TOTAL").T
        out = pd.concat([out, total_row])

    return out


def normalize_table(
    df: pd.DataFrame,
    drop_label: str = "Missing",
    drop_rows: list[str] | None = None,
    drop_cols: list[str] | None = None,
    cast_int: bool = True,
) -> pd.DataFrame:
    """
    Convert contingency table to pure absolute-frequency matrix.

    - removes relative-frequency layer
    - removes structural label (default: 'Missing')
    - returns clean observed counts matrix for inference (e.g., χ²)
    """

    # ------------------------------------------------------------
    # 0. remove TOTAL row if present
    # ------------------------------------------------------------
    if "TOTAL" in df.index:
        df = df.drop(index="TOTAL")

    drop_rows = set(drop_rows or [])
    drop_cols = set(drop_cols or [])

    drop_rows.add(drop_label)
    drop_cols.add(drop_label)

    # ------------------------------------------------------------
    # 1. keep only ABS layer
    # ------------------------------------------------------------
    if not isinstance(df.columns, pd.MultiIndex):
        raise ValueError("Expected MultiIndex columns (category, metric).")

    abs_df = df.xs("Abs.", axis=1, level=1)

    # ------------------------------------------------------------
    # 2. remove forbidden rows/cols
    # ------------------------------------------------------------
    abs_df = abs_df.loc[~abs_df.index.isin(drop_rows)]
    abs_df = abs_df.loc[:, ~abs_df.columns.isin(drop_cols)]

    # ------------------------------------------------------------
    # 3. optional cleanup
    # ------------------------------------------------------------
    if cast_int:
        abs_df = abs_df.round(0).astype(int)

    return abs_df   








def report_expected_frequency_issues(
    contingency_df: pd.DataFrame,
    report_path: str | Path,
    min_expected: float = 5.0,
    verbose: bool = True
) -> bool:
    """
    Write a text report listing cells with expected counts below min_expected.

    Returns:
        True if the table passes the expected-frequency check, False otherwise.
    """
    df = normalize_contingency(contingency_df)

    n_rows, n_cols = df.shape
    if n_rows < 2 or n_cols < 2:
        text = "⚠️  Table too small after stripping — need at least 2×2.\n"
        Path(report_path).write_text(text, encoding="utf-8")
        if verbose:
            print(text, end="")
        return False

    counts      = df.values.astype(float)
    grand_total = counts.sum()
    row_totals  = counts.sum(axis=1)
    col_totals  = counts.sum(axis=0)
    expected    = np.outer(row_totals, col_totals) / grand_total

    total_cells = expected.size
    dof         = (n_rows - 1) * (n_cols - 1)
    min_exp_val = expected.min()
    n_below     = (expected < min_expected).sum()

    if dof == 1:
        effective_ratio = 0.0
        ratio_source = "adaptive (2×2: all cells must meet threshold)"
    elif total_cells <= 9:
        effective_ratio = 0.20
        ratio_source = "adaptive (small table ≤ 9 cells)"
    elif total_cells <= 24:
        effective_ratio = 0.15
        ratio_source = "adaptive (medium table 10–24 cells)"
    else:
        effective_ratio = 0.10
        ratio_source = "adaptive (large table ≥ 25 cells)"

    ratio_below = n_below / total_cells
    passed = (ratio_below <= effective_ratio) and (min_exp_val >= 1.0)

    lines = []
    sep = "=" * 65
    lines.append(sep)
    lines.append("EXPECTED FREQUENCY CHECK")
    lines.append(sep)
    lines.append(f"Table shape          : {n_rows} rows × {n_cols} cols ({total_cells} cells, df={dof})")
    lines.append(f"Grand total (N)      : {int(grand_total)}")
    lines.append(f"Threshold source     : {ratio_source}")
    lines.append(f"Cells below E={min_expected:<4}  : {n_below} / {total_cells} ({ratio_below:.1%}) [limit: {effective_ratio:.0%}]")
    lines.append(f"Minimum expected     : {min_exp_val:.2f} [hard minimum: 1.0]")
    lines.append(f"Result               : {'PASS' if passed else 'FAIL'}")

    if dof == 1:
        lines.append("⚠️  df=1: consider Yates' continuity correction or Fisher's exact test.")

    below_mask = expected < min_expected
    if below_mask.any():
        col_w = 35
        lines.append("")
        lines.append(f"Cells with expected < {min_expected}:")
        lines.append(f"{'Row':<{col_w}} {'Col':<{col_w}} {'Expected':>10}")
        lines.append("-" * (col_w * 2 + 12))
        rows_idx, cols_idx = np.where(below_mask)
        for r, c in zip(rows_idx, cols_idx):
            lines.append(f"{str(df.index[r]):<{col_w}} {str(df.columns[c]):<{col_w}} {expected[r, c]:>10.2f}")

    lines.append(sep)

    report_path = Path(report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if verbose:
        print("\n".join(lines))

    return passed





#============================================================
#============================================================    