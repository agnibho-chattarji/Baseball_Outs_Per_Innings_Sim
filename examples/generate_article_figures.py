import os, numpy as np, matplotlib.pyplot as plt
from baseball_sim.config import SimConfig, Batter
from baseball_sim.simulator import simulate_game, expected_runs_per_inning_curve
from baseball_sim.plots import heatmap_runs_grid, variance_vs_mean, hist_runs

OUTDIR = "outputs"
os.makedirs(OUTDIR, exist_ok=True)

cfg = SimConfig()

# 1) Grid heatmap 1..9 outs × 1..9 innings
outs_range = range(1,10)
inn_range  = range(1,10)
grid = np.zeros((len(outs_range), len(inn_range)))
for i,o in enumerate(outs_range):
    for j,ninn in enumerate(inn_range):
        sims = []
        for s in range(800):
            res = simulate_game(ninn, o, cfg)
            sims.append((res['team1']+res['team2'])/2.0)
        grid[i,j] = float(np.mean(sims))
heatmap_runs_grid(grid, outs_range, inn_range, "Avg Runs per TEAM per Game (1–9 outs × 1–9 innings)", annotate=True, cmap="OrRd")
plt.savefig(os.path.join(OUTDIR, "grid_runs.png"), dpi=150); plt.close()

# 2) Variance vs mean for 9-inning games; labels = outs
pts = []
for o in range(1,10):
    runs = []
    for s in range(1500):
        res = simulate_game(9, o, cfg)
        runs.append((res['team1']+res['team2'])/2.0)
    pts.append((float(np.mean(runs)), float(np.std(runs)), o))
variance_vs_mean(pts, "Variance vs Mean Runs (9 innings; labels = outs per inning)")
plt.savefig(os.path.join(OUTDIR, "var_vs_mean.png"), dpi=150); plt.close()

# 3) Histograms for 9×3 vs 6×4 vs 5×5
series = {}
for inn, o, label in [(9,3,"9×3"),(6,4,"6×4"),(5,5,"5×5")]:
    runs = []
    for s in range(2000):
        res = simulate_game(inn, o, cfg)
        runs.append(res['team1']); runs.append(res['team2'])
    series[label] = np.array(runs)
hist_runs(series, title="Run Distributions per TEAM — 9×3 vs 6×4 vs 5×5")
plt.savefig(os.path.join(OUTDIR, "hist_9x3_6x4_5x5.png"), dpi=150); plt.close()

print("Saved figures to", OUTDIR)
