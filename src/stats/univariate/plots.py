import sqlite3
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Project root
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
src_dir = BASE_DIR / "src"

# Add src to sys.path so top-level imports work
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Import univariate descriptive 
from stats.univariate import desc_analysis as desc

univariate_output_dir = BASE_DIR / "data_visual" / "univariate"
con = sqlite3.connect(BASE_DIR / "data" / "IST-dataset.db")

univariate_output_dir.mkdir(exist_ok=True)



#============================================================
# UNIVARIATE PLOTS
#============================================================

def plot_expiry_distribution(con) -> None:
    """
    Bar chart of sanction regimes by expiry condition,
    expressed as relative frequencies.
    """
    filename = "expiry_distribution.svg"
    df = desc.get_expiry_distribution(con)
    df = df.drop(index="TOTAL", errors="ignore")

    plot_df = df["Rel(%)"].astype(float)

    fig, ax = plt.subplots(figsize=(6, 5))

    plot_df.plot(
        kind="bar",
        ax=ax,
        color="steelblue",
        edgecolor="white",
        width=0.4,
    )

    ax.set_title(
        "Frequency Distribution of Expiry Condition",
        fontsize=13,
        pad=15,
    )
    ax.set_ylabel("Regime Cases")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.tick_params(axis="x", rotation=15)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()

    out_path = univariate_output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")
#print(plot_expiry_distribution(con))    



def plot_review_distribution(con) -> None:
    """
    Bar chart of sanction regimes by review condition,
    expressed as relative frequencies.
    """
    filename = "review_distribution.svg"
    df = desc.get_review_distribution(con)
    df = df.drop(index="TOTAL", errors="ignore")

    plot_df = df["Rel(%)"].astype(float)

    fig, ax = plt.subplots(figsize=(6, 5))

    plot_df.plot(
        kind="bar",
        ax=ax,
        color="steelblue",
        edgecolor="white",
        width=0.4,
    )

    ax.set_title(
        "Frequency Distribution of Review Condition",
        fontsize=13,
        pad=15,
    )
    ax.set_ylabel("Regime Cases")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.tick_params(axis="x", rotation=15)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()

    out_path = univariate_output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")
#print(plot_review_distribution(con))    


def plot_req_termination_distribution(con) -> None:
    """
    Bar chart of sanction regimes by requirement termination clarity,
    expressed as relative frequencies.
    """
    filename = "req_termination_distribution.svg"
    df = desc.get_req_termination_distribution(con)
    df = df.drop(index="TOTAL", errors="ignore")

    plot_df = df["Rel(%)"].astype(float)

    fig, ax = plt.subplots(figsize=(6, 5))

    plot_df.plot(
        kind="bar",
        ax=ax,
        color="steelblue",
        edgecolor="white",
        width=0.4,
    )

    ax.set_title(
        "Frequency Distribution of Requirement Termination",
        fontsize=13,
        pad=15,
    )
    ax.set_ylabel("Regime Cases")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.tick_params(axis="x", rotation=15)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()

    out_path = univariate_output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")
#print(plot_req_termination_distribution(con))  


def plot_outcome_distribution(con) -> None:
    """
    Horizontal bar chart of sanction regimes by outcome combination,
    expressed as relative frequencies.
    """
    filename = "outcome_distribution.svg"
    df = desc.get_outcome_distribution(con)
    df = df.drop(index="TOTAL", errors="ignore")

    plot_df = df["Rel(%)"].astype(float).sort_values()

    fig, ax = plt.subplots(figsize=(10, 6))

    plot_df.plot(
        kind="barh",
        ax=ax,
        color="steelblue",
        edgecolor="white",
    )

    ax.set_title(
        "Frequency Distribution of Sanction Outcomes",
        fontsize=13,
        pad=15,
    )
    ax.set_xlabel("Regime Cases")
    ax.set_ylabel("Outcome")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax.grid(axis="x", linestyle="--", alpha=0.5)

    plt.tight_layout()

    out_path = univariate_output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")
#print(plot_outcome_distribution(con))    


def plot_sender_distribution(con) -> None:
    filename = "sender_distribution.svg"
    df = desc.get_sender_distribution(con)
    df = df.drop(index="TOTAL", errors="ignore")

    plot_df = df["Rel(%)"].astype(float).sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(10, 6))

    plot_df.plot(
        kind="bar",
        ax=ax,
        color="steelblue",
        edgecolor="white",
    )

    ax.set_title(
        "Frequency Distribution of Sanction Regimes by Sender",
        fontsize=13,
        pad=15,
    )
    ax.set_xlabel("Sender")
    ax.set_ylabel("Regime Cases")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()

    out_path = univariate_output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")
#print(plot_sender_distribution(con))    


def plot_duration_distribution(con) -> None:
    """
    Bar chart of sanction regimes by duration interval,
    expressed as relative frequencies.
    """
    filename = "duration_distribution.svg"
    df = desc.get_duration_distribution(con)
    df = df.drop(index="TOTAL", errors="ignore")

    plot_df = df["Rel(%)"].astype(float)

    fig, ax = plt.subplots(figsize=(9, 5))

    plot_df.plot(
        kind="bar",
        ax=ax,
        color="steelblue",
        edgecolor="white",
        width=0.6,
    )

    ax.set_title(
        "Frequency Distribution of Sanction Regime Duration",
        fontsize=13,
        pad=15,
    )
    ax.set_xlabel("Duration Interval")
    ax.set_ylabel("Regime Cases")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.tick_params(axis="x", rotation=30)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()

    out_path = univariate_output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")
#print(plot_duration_distribution(con))    


def plot_gradual_distribution(con) -> None:
    """
    Bar chart of sanction regimes by termination modality,
    expressed as relative frequencies.
    """
    filename = "gradual_distribution.svg"
    df = desc.get_gradual_distribution(con)
    df = df.drop(index="TOTAL", errors="ignore")

    plot_df = df["Rel(%)"].astype(float)

    fig, ax = plt.subplots(figsize=(6, 5))

    plot_df.plot(
        kind="bar",
        ax=ax,
        color="steelblue",
        edgecolor="white",
        width=0.4,
    )

    ax.set_title(
        "Frequency Distribution of Termination Modality",
        fontsize=13,
        pad=15,
    )
    ax.set_ylabel("Regime Cases")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.tick_params(axis="x", rotation=15)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()

    out_path = univariate_output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")
#print(plot_gradual_distribution(con))    


def plot_adapt_goal_distribution(con) -> None:
    """
    Bar chart of sanction regimes by goal adaptation,
    expressed as relative frequencies.
    """
    filename = "adapt_goal_distribution.svg"
    df = desc.get_adapt_goal_distribution(con)
    df = df.drop(index="TOTAL", errors="ignore")

    plot_df = df["Rel(%)"].astype(float)

    fig, ax = plt.subplots(figsize=(6, 5))

    plot_df.plot(
        kind="bar",
        ax=ax,
        color="steelblue",
        edgecolor="white",
        width=0.4,
    )

    ax.set_title(
        "Frequency Distribution of Goal Adaptation",
        fontsize=13,
        pad=15,
    )
    ax.set_ylabel("Regime Cases")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.tick_params(axis="x", rotation=15)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()

    out_path = univariate_output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")
#print(plot_adapt_goal_distribution(con))    


def plot_negotiation_distribution(con) -> None:
    """
    Bar chart of sanction regimes by negotiation presence,
    expressed as relative frequencies.
    """
    filename = "negotiation_distribution.svg"
    df = desc.get_negotiation_distribution(con)
    df = df.drop(index="TOTAL", errors="ignore")

    plot_df = df["Rel(%)"].astype(float)

    fig, ax = plt.subplots(figsize=(6, 5))

    plot_df.plot(
        kind="bar",
        ax=ax,
        color="steelblue",
        edgecolor="white",
        width=0.4,
    )

    ax.set_title(
        "Frequency Distribution of Negotiation Presence",
        fontsize=13,
        pad=15,
    )
    ax.set_ylabel("Regime Cases")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.tick_params(axis="x", rotation=15)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()

    out_path = univariate_output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")
#print(plot_negotiation_distribution(con))    


def plot_multilateralism_distribution(con) -> None:
    """
    Horizontal bar chart of sanction regimes by multilateralism,
    expressed as relative frequencies.
    """
    filename = "multilateralism_distribution.svg"
    df = desc.get_multilateralism_distribution(con)
    df = df.drop(index="TOTAL", errors="ignore")

    plot_df = df["Rel(%)"].astype(float).sort_values()

    fig, ax = plt.subplots(figsize=(10, 6))

    plot_df.plot(
        kind="barh",
        ax=ax,
        color="steelblue",
        edgecolor="white",
    )

    ax.set_title(
        "Frequency Distribution of Multilateralism",
        fontsize=13,
        pad=15,
    )
    ax.set_xlabel("Percentage of Cases")
    ax.set_ylabel("Multilateralism")
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax.grid(axis="x", linestyle="--", alpha=0.5)

    plt.tight_layout()

    out_path = univariate_output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")
#print(plot_multilateralism_distribution(con))    

#============================================================
#============================================================
#============================================================