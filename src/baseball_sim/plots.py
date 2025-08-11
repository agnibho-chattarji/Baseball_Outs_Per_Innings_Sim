import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
from .config import SimConfig, Batter
from .simulator import simulate_game, simulate_many, expected_runs_per_inning_curve

def heatmap_runs_grid(values, outs_range, innings_range, title, annotate=True, cmap="OrRd"):
    plt.figure(figsize=(10,7))
    ax = sns.heatmap(values, annot=annotate, fmt=".1f", cmap=cmap, cbar_kws={'label': 'Avg Runs per TEAM'})
    ax.invert_yaxis()
    ax.set_xlabel("Innings per Game")
    ax.set_ylabel("Outs per Inning")
    ax.set_title(title)
    ax.set_xticklabels(list(innings_range))
    ax.set_yticklabels(list(outs_range))
    plt.tight_layout()

def variance_vs_mean(points, title):
    means = [p[0] for p in points]; stds = [p[1] for p in points]; labels = [p[2] for p in points]
    plt.figure(figsize=(8,6))
    plt.scatter(means, stds, s=80)
    for m,s,lbl in points:
        plt.text(m, s, str(lbl), ha='center', va='bottom', fontsize=9)
    plt.xlabel("Average Runs per TEAM per Game")
    plt.ylabel("Standard Deviation (per TEAM)")
    plt.title(title)
    plt.grid(True); plt.tight_layout()

def hist_runs(series_dict, bins=None, title="Run Distributions per TEAM"):
    plt.figure(figsize=(10,6))
    if bins is None:
        max_r = max(max(v) for v in series_dict.values())
        bins = np.arange(0, max_r+2) - 0.5
    for label, data in series_dict.items():
        plt.hist(data, bins=bins, alpha=0.55, density=True, label=f"{label} (μ={np.mean(data):.2f}, σ={np.std(data):.2f})")
    plt.xlabel("Runs per TEAM per Game")
    plt.ylabel("Probability Density")
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
