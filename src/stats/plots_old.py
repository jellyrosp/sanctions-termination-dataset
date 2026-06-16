import sqlite3
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
src_dir = BASE_DIR / "src"

# Add src to sys.path so top-level imports work
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Now import descriptive as a top-level module
from stats import descriptive as desc

output_dir = BASE_DIR / "data_visual"
con = sqlite3.connect(BASE_DIR / "data" / "IST-dataset.db")

output_dir.mkdir(exist_ok=True)



def plot_termination_by_sender(con) -> None:
    """
    Stacked bar chart of sanction regime terminations by sender,
    expressed as relative frequencies.
    """

    filename = "termination_by_sender.svg"

    df = desc.get_termination_by_sender(con)

    # remove TOTAL row if present
    df = df.drop(index="TOTAL", errors="ignore")

    # --- extract relative frequency layer safely ---
    plot_df = df.xs("Rel(%)", axis=1, level=1)

    # enforce numeric type
    plot_df = plot_df.apply(pd.to_numeric, errors="coerce").fillna(0)

    # optional: ensure consistent column order (if available)
    preferred_order = [
        "De iure & de facto",
        "De iure",
        "De facto",
        "Ongoing",
    ]

    plot_df = plot_df.reindex(
        columns=[c for c in preferred_order if c in plot_df.columns]
    )

    fig, ax = plt.subplots(figsize=(12, 6))

    plot_df.plot(
        kind="bar",
        stacked=True,
        ax=ax,
        width=0.75,
        colormap="tab10",
    )

    ax.tick_params(axis='x', rotation=45)

    ax.set_title(
        "Sanction Termination Type by Sender (relative frequencies)",
        fontsize=14,
        pad=15,
    )

    ax.set_xlabel("Sender")
    ax.set_ylabel("Percentage of Cases")
    ax.set_ylim(0, 100)

    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda y, _: f"{y:.0f}%")
    )

    ax.legend(
        title="Termination Type",
        bbox_to_anchor=(1.01, 1),
        loc="upper left",
    )

    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()

    out_path = output_dir / filename
    fig.savefig(out_path, format="svg")

    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")
#plot_termination_by_sender(con)


def plot_duration_by_sender(con) -> None:
    """
    Stacked bar chart of sanction regime duration intervals by sender,
    expressed as relative frequencies.
    """
    filename = "duration_by_sender.svg"
    df = desc.get_duration_by_sender(con)
    df = df.drop(index="TOTAL", errors="ignore")

    plot_df = df.xs("Rel(%)", axis=1, level=1).astype(float)

    fig, ax = plt.subplots(figsize=(12, 6))

    plot_df.plot(
        kind="bar",
        stacked=True,
        ax=ax,
        width=0.75,
        colormap="tab10",
    )

    ax.tick_params(axis='x', rotation=45)

    ax.set_title(
        "Sanction Regime Duration by Sender (relative frequencies)",
        fontsize=14,
        pad=15,
    )
    ax.set_xlabel("Sender")
    ax.set_ylabel("Percentage of Cases")
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.legend(
        title="Duration Interval",
        bbox_to_anchor=(1.01, 1),
        loc="upper left",
    )
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()

    out_path = output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")
#plot_duration_by_sender(con)


def plot_gradual_by_sender(con) -> None:
    """
    Stacked bar chart of sanction termination modality by sender,
    expressed as relative frequencies.
    """
    filename = "gradual_by_sender.svg"
    df = desc.get_gradual_by_sender(con)
    df = df.drop(index="TOTAL", errors="ignore")

    plot_df = df.xs("Rel(%)", axis=1, level=1).astype(float)

    fig, ax = plt.subplots(figsize=(12, 6))

    plot_df.plot(
        kind="bar",
        stacked=True,
        ax=ax,
        width=0.75,
        colormap="tab10",
    )

    ax.tick_params(axis='x', rotation=45)

    ax.set_title(
        "Sanction Termination Modality by Sender (relative frequencies)",
        fontsize=14,
        pad=15,
    )
    ax.set_xlabel("Sender")
    ax.set_ylabel("Percentage of Cases")
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.legend(
        title="Termination Modality",
        bbox_to_anchor=(1.01, 1),
        loc="upper left",
    )
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()

    out_path = output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")
#plot_gradual_by_sender(con)    


def plot_expiry_by_sender(con) -> None:
    """
    Stacked bar chart of sanction expiry condition by sender,
    expressed as relative frequencies.
    """
    filename = "expiry_by_sender.svg"
    df = desc.get_expiry_by_sender(con)
    df = df.drop(index="TOTAL", errors="ignore")

    plot_df = df.xs("Rel(%)", axis=1, level=1).astype(float)

    fig, ax = plt.subplots(figsize=(12, 6))

    plot_df.plot(
        kind="bar",
        stacked=True,
        ax=ax,
        width=0.75,
        colormap="tab10",
    )

    ax.tick_params(axis='x', rotation=45)

    ax.set_title(
        "Sanction Expiry Condition by Sender (relative frequencies)",
        fontsize=14,
        pad=15,
    )
    ax.set_xlabel("Sender")
    ax.set_ylabel("Percentage of Cases")
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.legend(
        title="Expiry Condition",
        bbox_to_anchor=(1.01, 1),
        loc="upper left",
    )
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()

    out_path = output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")
#plot_expiry_by_sender(con)    


def plot_review_by_sender(con) -> None:
    """
    Stacked bar chart of sanction review regulation by sender,
    expressed as relative frequencies.
    """
    filename = "review_by_sender.svg"
    df = desc.get_review_by_sender(con)
    df = df.drop(index="TOTAL", errors="ignore")

    plot_df = df.xs("Rel(%)", axis=1, level=1).astype(float)

    fig, ax = plt.subplots(figsize=(12, 6))

    plot_df.plot(
        kind="bar",
        stacked=True,
        ax=ax,
        width=0.75,
        colormap="tab10",
    )

    ax.tick_params(axis='x', rotation=45)

    ax.set_title(
        "Sanction Review Regulation by Sender (relative frequencies)",
        fontsize=14,
        pad=15,
    )
    ax.set_xlabel("Sender")
    ax.set_ylabel("Percentage of Cases")
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.legend(
        title="Review",
        bbox_to_anchor=(1.01, 1),
        loc="upper left",
    )
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()

    out_path = output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")
#plot_expiry_by_sender(con)    

####################
####################


# Not useful for distorted relative frequency valuesndue to clusters limitation on measures combination values

# def plot_measure_by_sender(con) -> None:
#     """
#     Stacked bar chart of applied measure by sender,
#     expressed as relative frequencies.
#     """
#     filename = "measure_by_sender.svg"
#     df = desc.get_measure_by_sender(con)
#     df = df.drop(index="TOTAL", errors="ignore")

#     plot_df = df.xs("Rel(%)", axis=1, level=1).astype(float)

#     fig, ax = plt.subplots(figsize=(12, 6))

#     plot_df.plot(
#         kind="bar",
#         stacked=True,
#         ax=ax,
#         width=0.75,
#         colormap="tab10",
#     )

#     ax.tick_params(axis='x', rotation=45)

#     ax.set_title(
#         "Applied measure by Sender (relative frequencies)",
#         fontsize=14,
#         pad=15,
#     )
#     ax.set_xlabel("Sender")
#     ax.set_ylabel("Percentage of Cases")
#     ax.set_ylim(0, 100)
#     ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
#     ax.legend(
#         title="Measure",
#         bbox_to_anchor=(1.01, 1),
#         loc="upper left",
#     )
#     ax.grid(axis="y", linestyle="--", alpha=0.5)

#     plt.tight_layout()

#     out_path = output_dir / filename
#     fig.savefig(out_path, format="svg")
#     plt.show()
#     plt.close(fig)

#     print(f"Plot saved to: {out_path}")
#plot_measure_by_sender(con)    

####################
####################

def plot_measure_distribution(con) -> None:
    """
    Vertical bar chart of sanction regimes by applied measure.
    """
    filename = "measure distribution.svg"
    df = desc.get_measure_distribution(con)
    plot_df = df["Case Frq"].astype(float).sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(10, 6))

    plot_df.plot(
        kind="bar",  
        color="steelblue",
        edgecolor="white",
    )

    ax.set_title(
        "Sanction Measures Distribution",
        fontsize=14,
        pad=15,
    )
    ax.set_xlabel("Measure")           
    ax.set_ylabel("Case Frequency")         
    ax.grid(axis="y", linestyle="--", alpha=0.5)  

    plt.tight_layout()

    out_path = output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")
#plot_measure_frequency(con)    


def plot_measure_count_by_sender(con) -> None:
    """
    Stacked bar chart of sanction regimes by sender and number of measures,
    expressed as relative frequencies.
    """

    filename = "measure_count_by_sender.svg"

    df = desc.get_measure_count_by_sender(con)

    # drop total row
    df = df.drop(index="TOTAL", errors="ignore")

    # extract relative frequencies
    plot_df = df.xs("Rel(%)", axis=1, level=1).astype(float)

    fig, ax = plt.subplots(figsize=(12, 6))

    plot_df.plot(
        kind="bar",
        stacked=True,
        ax=ax,
        width=0.75,
        colormap="tab10"
    )

    ax.set_title(
        "Sanction Regimes by Sender and Number of Measures (relative frequencies)",
        fontsize=14,
        pad=15
    )

    ax.set_xlabel("Sender")
    ax.set_ylabel("Percentage of Cases")
    ax.set_ylim(0, 100)

    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda y, _: f"{y:.0f}%")
    )

    ax.legend(
        title="Number of Measures",
        bbox_to_anchor=(1.01, 1),
        loc="upper left"
    )

    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()

    out_path = output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")
#plot_measure_count_by_sender(con)    


def plot_goal_distribution(con) -> None:
    """
    Bar chart of sanction regimes by exact number of goals per case,
    expressed as relative frequencies.
    """
    filename = "goal_distribution.svg"
    df = desc.get_goal_distribution(con)
    df = df.drop(index="TOTAL", errors="ignore")

    # Extract relative frequencies and convert to float
    plot_df = df.xs("Rel(%)", axis=1, level=1).astype(float)

    fig, ax = plt.subplots(figsize=(10, 6))

    plot_df.plot(
        kind="bar",
        ax=ax,
        width=0.75,
        color="skyblue",
    )

    ax.tick_params(axis='x', rotation=0)

    ax.set_title(
        "Sanction Regimes by Exact Number of Goals (relative frequencies)",
        fontsize=14,
        pad=15,
    )
    ax.set_xlabel("Number of Goals")
    ax.set_ylabel("Percentage of Cases")
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()

    out_path = output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")
#print(plot_goal_distribution(con))


def plot_goal_count_by_sender(con) -> None:
    """
    Stacked bar chart of sanction regimes by sender and number of goals,
    expressed as relative frequencies.
    """

    filename = "goal_count_by_sender.svg"

    df = desc.get_goal_count_by_sender(con)

    # drop total row
    df = df.drop(index="TOTAL", errors="ignore")

    # extract relative frequencies
    plot_df = df.xs("Rel(%)", axis=1, level=1).astype(float)

    fig, ax = plt.subplots(figsize=(12, 6))

    plot_df.plot(
        kind="bar",
        stacked=True,
        ax=ax,
        width=0.75,
        colormap="tab10"
    )

    ax.set_title(
        "Sanction Regimes by Sender and Number of Goals (relative frequencies)",
        fontsize=14,
        pad=15
    )

    ax.set_xlabel("Sender")
    ax.set_ylabel("Percentage of Cases")
    ax.set_ylim(0, 100)

    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda y, _: f"{y:.0f}%")
    )

    ax.legend(
        title="Number of Goals",
        bbox_to_anchor=(1.01, 1),
        loc="upper left"
    )

    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()

    out_path = output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")
#print(plot_goal_count_by_sender(con))    



def get_goal_adaptation_by_sender(con) -> None:
    """
    Stacked bar chart of adaptation of goal by sender,
    expressed as relative frequencies.
    """
    filename = "adaptation_by_sender.svg"
    df = desc.get_review_by_sender(con)
    df = df.drop(index="TOTAL", errors="ignore")

    plot_df = df.xs("Rel(%)", axis=1, level=1).astype(float)

    fig, ax = plt.subplots(figsize=(12, 6))

    plot_df.plot(
        kind="bar",
        stacked=True,
        ax=ax,
        width=0.75,
        colormap="tab10",
    )

    ax.tick_params(axis='x', rotation=45)

    ax.set_title(
        "Adaptation of Goal by Sender (relative frequencies)",
        fontsize=14,
        pad=15,
    )
    ax.set_xlabel("Sender")
    ax.set_ylabel("Percentage of Cases")
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.legend(
        bbox_to_anchor=(1.01, 1),
        loc="upper left",
    )
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()

    out_path = output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")
#print(get_goal_adaptation_by_sender(con))    


def plot_target_salience_by_sender(con) -> None:
    """
    Stacked bar chart of target salience by sender,
    expressed as relative frequencies.
    """
    filename = "target_salience_by_sender.svg"
    df = desc.get_target_salience_by_sender(con)
    df = df.drop(index="TOTAL", errors="ignore")

    plot_df = df.xs("Rel(%)", axis=1, level=1).astype(float)

    fig, ax = plt.subplots(figsize=(12, 6))

    plot_df.plot(
        kind="bar",
        stacked=True,
        ax=ax,
        width=0.75,
        colormap="tab10",
    )

    ax.tick_params(axis='x', rotation=45)

    ax.set_title(
        "Target Salience by Sender (relative frequencies)",
        fontsize=14,
        pad=15,
    )
    ax.set_xlabel("Sender")
    ax.set_ylabel("Percentage of Cases")
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.legend(
        bbox_to_anchor=(1.01, 1),
        loc="upper left",
    )
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()

    out_path = output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")
#print(plot_target_salience_by_sender(con))    


def plot_sender_salience_by_sender(con) -> None:
    """
    Stacked bar chart of sender salience by sender,
    expressed as relative frequencies.
    """
    filename = "sender_salience_by_sender.svg"
    df = desc.get_sender_salience_by_sender(con)
    df = df.drop(index="TOTAL", errors="ignore")

    plot_df = df.xs("Rel(%)", axis=1, level=1).astype(float)

    fig, ax = plt.subplots(figsize=(12, 6))

    plot_df.plot(
        kind="bar",
        stacked=True,
        ax=ax,
        width=0.75,
        colormap="tab10",
    )

    ax.tick_params(axis='x', rotation=45)

    ax.set_title(
        "Sender Salience by Sender (relative frequencies)",
        fontsize=14,
        pad=15,
    )
    ax.set_xlabel("Sender")
    ax.set_ylabel("Percentage of Cases")
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.legend(
        bbox_to_anchor=(1.01, 1),
        loc="upper left",
    )
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()

    out_path = output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")
#print(plot_sender_salience_by_sender(con))    


def plot_requirement_termination_by_sender(con) -> None:
    """
    Stacked bar chart of requirement termination by sender,
    expressed as relative frequencies.
    """
    filename = "requirement_termination_by_sender.svg"
    df = desc.get_requirement_termination_by_sender(con)
    df = df.drop(index="TOTAL", errors="ignore")

    plot_df = df.xs("Rel(%)", axis=1, level=1).astype(float)

    fig, ax = plt.subplots(figsize=(12, 6))

    plot_df.plot(
        kind="bar",
        stacked=True,
        ax=ax,
        width=0.75,
        colormap="tab10",
    )

    ax.tick_params(axis='x', rotation=45)

    ax.set_title(
        "Requirement Termination by Sender (relative frequencies)",
        fontsize=14,
        pad=15,
    )
    ax.set_xlabel("Sender")
    ax.set_ylabel("Percentage of Cases")
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.legend(
        title="Requirement Termination",
        bbox_to_anchor=(1.01, 1),
        loc="upper left",
    )
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()

    out_path = output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")
#print(plot_requirement_termination_by_sender(con))    


def plot_negotiation_by_sender(con) -> None:
    """
    Stacked bar chart of negotiation by sender,
    expressed as relative frequencies.
    """
    filename = "negotiation_by_sender.svg"
    df = desc.get_negotiation_by_sender(con)
    df = df.drop(index="TOTAL", errors="ignore")

    plot_df = df.xs("Rel(%)", axis=1, level=1).astype(float)

    fig, ax = plt.subplots(figsize=(12, 6))

    plot_df.plot(
        kind="bar",
        stacked=True,
        ax=ax,
        width=0.75,
        colormap="tab10",
    )

    ax.tick_params(axis='x', rotation=45)

    ax.set_title(
        "Negotiation by Sender (relative frequencies)",
        fontsize=14,
        pad=15,
    )
    ax.set_xlabel("Sender")
    ax.set_ylabel("Percentage of Cases")
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.legend(
        bbox_to_anchor=(1.01, 1),
        loc="upper left",
    )
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()

    out_path = output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")
#print(plot_negotiation_by_sender(con))    


def plot_outcome_type_by_sender(con) -> None:
    """
    Stacked bar chart of sanction regime outcomes by sender,
    expressed as relative frequencies.
    """

    filename = "outcome_type_by_sender.svg"

    df = desc.get_outcome_type_by_sender(con)

    # remove TOTAL row if present
    df = df.drop(index="TOTAL", errors="ignore")

    # --- extract relative frequency layer safely ---
    plot_df = df.xs("Rel(%)", axis=1, level=1)

    # enforce numeric type
    plot_df = plot_df.apply(pd.to_numeric, errors="coerce").fillna(0)

    fig, ax = plt.subplots(figsize=(14, 6))

    plot_df.plot(
        kind="bar",
        stacked=True,
        ax=ax,
        width=0.75,
        colormap="tab10",
    )

    ax.tick_params(axis='x', rotation=45)

    ax.set_title(
        "Sanction Outcome Type by Sender (relative frequencies)",
        fontsize=14,
        pad=15,
    )

    ax.set_xlabel("Sender")
    ax.set_ylabel("Percentage of Cases")
    ax.set_ylim(0, 100)

    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda y, _: f"{y:.0f}%")
    )

    ax.legend(
        title="Outcome Type",
        bbox_to_anchor=(1.01, 1),
        loc="upper left",
    )

    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()

    out_path = output_dir / filename
    fig.savefig(out_path, format="svg")

    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")
#plot_outcome_type_by_sender(con)


def plot_sender_cost_by_sender(con) -> None:
    """
    Stacked bar chart of sender cost by sender,
    expressed as relative frequencies.
    """

    filename = "sender_cost_by_sender.svg"

    df = desc.get_sender_cost_by_sender(con)

    # remove TOTAL row if present
    df = df.drop(index="TOTAL", errors="ignore")

    # --- extract relative frequency layer safely ---
    plot_df = df.xs("Rel(%)", axis=1, level=1)

    # enforce numeric type
    plot_df = plot_df.apply(pd.to_numeric, errors="coerce").fillna(0)

    fig, ax = plt.subplots(figsize=(14, 6))

    plot_df.plot(
        kind="bar",
        stacked=True,
        ax=ax,
        width=0.75,
        colormap="tab10",
    )

    ax.tick_params(axis='x', rotation=45)

    ax.set_title(
        "Sender Cost by Sender (relative frequencies)",
        fontsize=14,
        pad=15,
    )

    ax.set_xlabel("Sender")
    ax.set_ylabel("Percentage of Cases")
    ax.set_ylim(0, 100)

    ax.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda y, _: f"{y:.0f}%")
    )

    ax.legend(
        title="Sender Cost",
        bbox_to_anchor=(1.01, 1),
        loc="upper left",
    )

    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()

    out_path = output_dir / filename
    fig.savefig(out_path, format="svg")

    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")
#plot_sender_cost_by_sender(con)


def plot_inst_investment_by_sender(con) -> None:
    """
    Stacked bar chart of institutional investment by sender,
    expressed as relative frequencies.
    """
    filename = "inst_investment_by_sender.svg"
    df = desc.get_inst_investment_by_sender(con)
    df = df.drop(index="TOTAL", errors="ignore")

    plot_df = df.xs("Rel(%)", axis=1, level=1).astype(float)

    fig, ax = plt.subplots(figsize=(12, 6))

    plot_df.plot(
        kind="bar",
        stacked=True,
        ax=ax,
        width=0.75,
        colormap="tab10",
    )

    ax.tick_params(axis='x', rotation=45)

    ax.set_title(
        "Institutional Investment by Sender (relative frequencies)",
        fontsize=14,
        pad=15,
    )
    ax.set_xlabel("Sender")
    ax.set_ylabel("Percentage of Cases")
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.legend(
        title="Institutional Investment",
        bbox_to_anchor=(1.01, 1),
        loc="upper left",
    )
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()

    out_path = output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")
#plot_inst_investment_by_sender(con)


def plot_target_cost_by_sender(con) -> None:
    """
    Stacked bar chart of target cost by sender,
    expressed as relative frequencies.
    """
    filename = "target_cost_by_sender.svg"
    df = desc.get_target_cost_by_sender(con)
    df = df.drop(index="TOTAL", errors="ignore")

    plot_df = df.xs("Rel(%)", axis=1, level=1).astype(float)

    fig, ax = plt.subplots(figsize=(12, 6))

    plot_df.plot(
        kind="bar",
        stacked=True,
        ax=ax,
        width=0.75,
        colormap="tab10",
    )

    ax.tick_params(axis='x', rotation=45)

    ax.set_title(
        "Target Cost by Sender (relative frequencies)",
        fontsize=14,
        pad=15,
    )
    ax.set_xlabel("Sender")
    ax.set_ylabel("Percentage of Cases")
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.legend(
        title="Target Cost",
        bbox_to_anchor=(1.01, 1),
        loc="upper left",
    )
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()

    out_path = output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")
#print(plot_target_cost_by_sender(con))


def plot_multilat_by_sender(con) -> None:
    """
    Stacked bar chart of multilateralism by sender,
    expressed as relative frequencies.
    """
    filename = "multilateralism_by_sender.svg"
    df = desc.get_multilat_by_sender(con)
    df = df.drop(index="TOTAL", errors="ignore")

    plot_df = df.xs("Rel(%)", axis=1, level=1).astype(float)

    fig, ax = plt.subplots(figsize=(12, 6))

    plot_df.plot(
        kind="bar",
        stacked=True,
        ax=ax,
        width=0.75,
        colormap="tab10",
    )

    ax.tick_params(axis='x', rotation=45)

    ax.set_title(
        "Multilateralism by Sender (relative frequencies)",
        fontsize=14,
        pad=15,
    )
    ax.set_xlabel("Sender")
    ax.set_ylabel("Percentage of Cases")
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.legend(
        title="Multilateralism",
        bbox_to_anchor=(1.01, 1),
        loc="upper left",
    )
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()

    out_path = output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")
#print(plot_multilat_by_sender(con))    