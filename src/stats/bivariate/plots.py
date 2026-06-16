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

# Import biivariate descriptive 
from stats.bivariate import desc_analysis as desc

bivariate_output_dir = BASE_DIR / "data_visual" / "bivariate"
con = sqlite3.connect(BASE_DIR / "data" / "IST-dataset.db")

bivariate_output_dir.mkdir(exist_ok=True)



#============================================================
# BIVARIATE PLOTS
#============================================================

# HELPERS #########################################

def _plot_bivariate(
    df: pd.DataFrame,
    title: str,
    xlabel: str,
    legend_title: str,
    filename: str,
    figsize: tuple = (12, 5),
    rotation: int = 15,
) -> None:
    """
    Generic stacked bar chart for bivariate contingency tables.
    Expects a MultiIndex column DataFrame with 'Rel(%)' level.
    """
    df = df.drop(index="TOTAL", errors="ignore")
    plot_df = df.xs("Rel(%)", axis=1, level=1).astype(float)

    fig, ax = plt.subplots(figsize=figsize)

    plot_df.plot(kind="bar", stacked=True, ax=ax, width=0.6, colormap="tab10")

    ax.set_title(title, fontsize=13, pad=15)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Regime Cases")
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.tick_params(axis="x", rotation=rotation)
    ax.legend(title=legend_title, bbox_to_anchor=(1.01, 1), loc="upper left")
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()

    out_path = bivariate_output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)

    print(f"Plot saved to: {out_path}")

##########################################################################
    

#  Y = DURATION==================================================

# ── expiry x duration ────────────────────────────────────────────────────────
def plot_expiry_x_duration(con) -> None:
    filename = "expiry_x_duration.svg"
    df = desc.get_expiry_x_duration(con)
    df = df.drop(index="TOTAL", errors="ignore")
    plot_df = df.xs("Rel(%)", axis=1, level=1).astype(float)

    fig, ax = plt.subplots(figsize=(10, 5))
    plot_df.plot(kind="bar", stacked=True, ax=ax, width=0.6, colormap="tab10")
    ax.set_title("Duration by Expiry Condition (relative frequencies)", fontsize=13, pad=15)
    ax.set_ylabel("Regime Cases")
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.tick_params(axis="x", rotation=15)
    ax.legend(title="Duration", bbox_to_anchor=(1.01, 1), loc="upper left")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    out_path = bivariate_output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)
    print(f"Plot saved to: {out_path}")
#print(plot_expiry_x_duration(con))    


# ── review x duration ────────────────────────────────────────────────────────
def plot_review_x_duration(con) -> None:
    filename = "review_x_duration.svg"
    df = desc.get_review_x_duration(con)
    df = df.drop(index="TOTAL", errors="ignore")
    plot_df = df.xs("Rel(%)", axis=1, level=1).astype(float)

    fig, ax = plt.subplots(figsize=(10, 5))
    plot_df.plot(kind="bar", stacked=True, ax=ax, width=0.6, colormap="tab10")
    ax.set_title("Duration by Review Condition (relative frequencies)", fontsize=13, pad=15)
    ax.set_ylabel("Regime Cases")
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.tick_params(axis="x", rotation=15)
    ax.legend(title="Duration", bbox_to_anchor=(1.01, 1), loc="upper left")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    out_path = bivariate_output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)
    print(f"Plot saved to: {out_path}")
#print(plot_review_x_duration(con))    


# ── requirement_termination x duration ───────────────────────────────────────
def plot_req_termination_x_duration(con) -> None:
    filename = "req_termination_x_duration.svg"
    df = desc.get_req_termination_x_duration(con)
    df = df.drop(index="TOTAL", errors="ignore")
    plot_df = df.xs("Rel(%)", axis=1, level=1).astype(float)

    fig, ax = plt.subplots(figsize=(10, 5))
    plot_df.plot(kind="bar", stacked=True, ax=ax, width=0.6, colormap="tab10")
    ax.set_title("Duration by Requirement Termination (relative frequencies)", fontsize=13, pad=15)
    ax.set_ylabel("Regime Cases")
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.tick_params(axis="x", rotation=15)
    ax.legend(title="Duration", bbox_to_anchor=(1.01, 1), loc="upper left")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    out_path = bivariate_output_dir / filename
    fig.savefig(out_path, format="svg")
    plt.show()
    plt.close(fig)
    print(f"Plot saved to: {out_path}")
#print(plot_req_termination_x_duration(con))    

#================================================================================


#  Y = OUTCOME ==================================================

def plot_expiry_x_outcome(con) -> None:
    _plot_bivariate(
        df           = desc.get_expiry_x_outcome(con),
        title        = "Outcome by Expiry Condition (relative frequencies)",
        xlabel       = "Expiry Condition",
        legend_title = "Outcome",
        filename     = "expiry_x_outcome.svg",
    )
#print(plot_expiry_x_outcome(con))    


def plot_review_x_outcome(con) -> None:
    _plot_bivariate(
        df           = desc.get_review_x_outcome(con),
        title        = "Outcome by Review Condition (relative frequencies)",
        xlabel       = "Review Condition",
        legend_title = "Outcome",
        filename     = "review_x_outcome.svg",
    )    
#print(plot_review_x_outcome(con))  


def plot_req_termination_x_outcome(con) -> None:
    _plot_bivariate(
        df           = desc.get_req_termination_x_outcome(con),
        title        = "Outcome by Requirement Termination (relative frequencies)",
        xlabel       = "Requirement Termination",
        legend_title = "Outcome",
        filename     = "req_termination_x_outcome.svg",
    )
#print(plot_req_termination_x_outcome(con))  

#================================================================================


#  Y = SENDER ==================================================

def plot_expiry_x_sender(con) -> None:
    _plot_bivariate(
        df           = desc.get_expiry_x_sender(con),
        title        = "Sender by Expiry Condition (relative frequencies)",
        xlabel       = "Expiry Condition",
        legend_title = "Sender",
        filename     = "expiry_x_sender.svg",
    )
#print(plot_expiry_x_sender(con))    


def plot_review_x_sender(con) -> None:
    _plot_bivariate(
        df           = desc.get_review_x_sender(con),
        title        = "Sender by Review Condition (relative frequencies)",
        xlabel       = "Review Condition",
        legend_title = "Sender",
        filename     = "review_x_sender.svg",
    )
#print(plot_review_x_sender(con))    


def plot_req_termination_x_sender(con) -> None:
    _plot_bivariate(
        df           = desc.get_req_termination_x_sender(con),
        title        = "Sender by Requirement Termination (relative frequencies)",
        xlabel       = "Requirement Termination",
        legend_title = "Sender",
        filename     = "req_termination_x_sender.svg",
    )
#print(plot_req_termination_x_sender(con)) 

#================================================================================



#  Y = DURATION ==================================================    

def plot_gradual_x_duration(con) -> None:
    _plot_bivariate(
        df           = desc.get_gradual_x_duration(con),
        title        = "Duration by Termination Modality (relative frequencies)",
        xlabel       = "Termination Modality",
        legend_title = "Duration",
        filename     = "gradual_x_duration.svg",
    )
#print(plot_gradual_x_duration(con))    


def plot_adapt_goal_x_duration(con) -> None:
    _plot_bivariate(
        df           = desc.get_adapt_goal_x_duration(con),
        title        = "Duration by Goal Adaptation (relative frequencies)",
        xlabel       = "Goal Adaptation",
        legend_title = "Duration",
        filename     = "adapt_goal_x_duration.svg",
    )
#print(plot_adapt_goal_x_duration(con))    


def plot_negotiations_x_duration(con) -> None:
    _plot_bivariate(
        df           = desc.get_negotiations_x_duration(con),
        title        = "Duration by Negotiation Presence (relative frequencies)",
        xlabel       = "Negotiation Presence",
        legend_title = "Duration",
        filename     = "negotiations_x_duration.svg",
    )
#print(plot_negotiations_x_duration(con))    

#================================================================================    


#  Y = OUTCOME ==================================================    

def plot_gradual_x_outcome(con) -> None:
    _plot_bivariate(
        df           = desc.get_gradual_x_outcome(con),
        title        = "Outcome by Termination Modality (relative frequencies)",
        xlabel       = "Termination Modality",
        legend_title = "Outcome",
        filename     = "gradual_x_outcome.svg",
    )
#print(plot_gradual_x_outcome(con))    


def plot_adapt_goal_x_outcome(con) -> None:
    _plot_bivariate(
        df           = desc.get_adapt_goal_x_outcome(con),
        title        = "Outcome by Goal Adaptation (relative frequencies)",
        xlabel       = "Goal Adaptation",
        legend_title = "Outcome",
        filename     = "adapt_goal_x_outcome.svg",
    )
#print(plot_adapt_goal_x_outcome(con))    


def plot_negotiations_x_outcome(con) -> None:
    _plot_bivariate(
        df           = desc.get_negotiations_x_outcome(con),
        title        = "Outcome by Negotiation Presence (relative frequencies)",
        xlabel       = "Negotiation Presence",
        legend_title = "Outcome",
        filename     = "negotiations_x_outcome.svg",
    )
#print(plot_negotiations_x_outcome(con))    

#================================================================================        



#  Y = SENDER ==================================================    

def plot_gradual_x_sender(con) -> None:
    _plot_bivariate(
        df           = desc.get_gradual_x_sender(con),
        title        = "Sender by Termination Modality (relative frequencies)",
        xlabel       = "Termination Modality",
        legend_title = "Sender",
        filename     = "gradual_x_sender.svg",
    )
#print(plot_gradual_x_sender(con))    


def plot_adapt_goal_x_sender(con) -> None:
    _plot_bivariate(
        df           = desc.get_adapt_goal_x_sender(con),
        title        = "Sender by Goal Adaptation (relative frequencies)",
        xlabel       = "Goal Adaptation",
        legend_title = "Sender",
        filename     = "adapt_goal_x_sender.svg",
    )
#print(plot_adapt_goal_x_sender(con))    


def plot_negotiations_x_sender(con) -> None:
    _plot_bivariate(
        df           = desc.get_negotiations_x_sender(con),
        title        = "Sender by Negotiation Presence (relative frequencies)",
        xlabel       = "Negotiation Presence",
        legend_title = "Sender",
        filename     = "negotiations_x_sender.svg",
    )
#print(plot_negotiations_x_sender(con))

#================================================================================   
         

#  Y = OUTCOME ==================================================  

def plot_multilateralism_x_outcome(con) -> None:
    _plot_bivariate(
        df           = desc.get_multilateralism_x_outcome(con),
        title        = "Outcome by Multilateralism (relative frequencies)",
        xlabel       = "Multilateralism",
        legend_title = "Outcome",
        filename     = "multilateralism_x_outcome.svg",
        figsize      = (14, 5),
        rotation     = 30,
    )
#print(plot_multilateralism_x_outcome(con))    


def plot_duration_x_outcome(con) -> None:
    _plot_bivariate(
        df           = desc.get_duration_x_outcome(con),
        title        = "Outcome by Duration Interval (relative frequencies)",
        xlabel       = "Duration Interval",
        legend_title = "Outcome",
        filename     = "duration_x_outcome.svg",
    ) 
#print(plot_duration_x_outcome(con))              

#================================================================================   