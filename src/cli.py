#!/usr/bin/env python3
import argparse, os, json, yaml, numpy as np
from baseball_sim.config import SimConfig, Batter
from baseball_sim.simulator import DEFAULT_BATTERS, simulate_game, simulate_many, expected_runs_per_inning_curve
from baseball_sim.plots import heatmap_runs_grid, variance_vs_mean, hist_runs
import matplotlib.pyplot as plt
import seaborn as sns

def load_config(path: str) -> SimConfig:
    with open(path,'r') as f: raw = yaml.safe_load(f)
    batters = {k: Batter(**v) for k,v in raw.get('batters', {}).items()}
    return SimConfig(
        lineup = raw.get('lineup', ['SS','2B','CF','1B','DH','RF','LF','3B','C']),
        batters = batters if batters else None,
        hit_distribution = raw.get('hit_distribution', {'single':0.69,'double':0.21,'triple':0.02,'home_run':0.08}),
        steal_att_1b_to_2b = float(raw.get('steal_att_1b_to_2b', 0.02)),
        steal_att_2b_to_3b = float(raw.get('steal_att_2b_to_3b', 0.006)),
        steal_succ_1b_to_2b = float(raw.get('steal_succ_1b_to_2b', 0.74)),
        steal_succ_2b_to_3b = float(raw.get('steal_succ_2b_to_3b', 0.70)),
        walk_hbp_bump = float(raw.get('walk_hbp_bump', 0.003)),
        #seed = int(raw.get('seed', 42))
        seed = None
    )

def main():
    ap = argparse.ArgumentParser(description="Baseball Outs-per-Inning Monte Carlo (calibrated, bases persist)")
    ap.add_argument("--config", default="configs/default.yaml", help="YAML config")
    ap.add_argument("--outs", type=int, default=3, help="Outs per half-inning")
    ap.add_argument("--innings", type=int, default=9, help="Innings per game")
    ap.add_argument("--sims", type=int, default=2000, help="Games to simulate")
    ap.add_argument("--mode", choices=["metrics","curve","grid","hist","varmean"], default="metrics")
    ap.add_argument("--curve-sims", type=int, default=4000)
    ap.add_argument("--outdir", default="outputs")
    args = ap.parse_args()

    os.makedirs(args.outdir, exist_ok=True)
    cfg = load_config(args.config)

    if args.mode == "metrics":
        metrics = simulate_many(args.innings, args.outs, cfg, n=args.sims)
        print(json.dumps(metrics, indent=2))

    elif args.mode == "curve":
        data = expected_runs_per_inning_curve(cfg, max_outs=9, sims_per_point=args.curve_sims)
        np.save(os.path.join(args.outdir, "ev_curve.npy"), data, allow_pickle=True)
        plt.figure(figsize=(9,6))
        plt.errorbar(data['outs'], data['ev'], yerr=data['sd'], fmt='o', capsize=5)
        plt.title("Expected Runs per Inning vs Outs (bases persist until inning ends)")
        plt.xlabel("Outs per Inning"); plt.ylabel("Expected Runs per Inning"); plt.ylim(0,None); plt.grid(True)
        plt.tight_layout(); plt.savefig(os.path.join(args.outdir, "ev_curve.png"), dpi=150)
        print("Saved EV curve →", os.path.join(args.outdir, "ev_curve.png"))

    elif args.mode == "grid":
        outs_range = range(1,10); inn_range = range(1,10)
        grid = np.zeros((len(outs_range), len(inn_range)))
        for i,o in enumerate(outs_range):
            vals = []
            for j,ninn in enumerate(inn_range):
                sims = []
                for s in range(args.sims):
                    res = simulate_game(ninn, o, cfg)
                    sims.append((res['team1']+res['team2'])/2.0)
                grid[i,j] = float(np.mean(sims))
        np.save(os.path.join(args.outdir, "grid_runs.npy"), grid)
        heatmap_runs_grid(grid, outs_range, inn_range, "Avg Runs per TEAM per Game (1–9 outs × 1–9 innings)", annotate=True, cmap="OrRd")
        plt.savefig(os.path.join(args.outdir, "grid_runs.png"), dpi=150)
        print("Saved grid heatmap →", os.path.join(args.outdir, "grid_runs.png"))

    elif args.mode == "hist":
        # compare 9x3 vs 6x4 vs 5x5
        formats = [(9,3,"9×3"), (6,4,"6×4"), (5,5,"5×5")]
        series = {}
        for inn, o, label in formats:
            runs = []
            for s in range(args.sims):
                res = simulate_game(inn, o, cfg)
                runs.append(res['team1']); runs.append(res['team2'])
            series[label] = np.array(runs)
        hist_runs(series, title="Run Distributions per TEAM — 9×3 vs 6×4 vs 5×5")
        plt.savefig(os.path.join(args.outdir, "hist_9x3_6x4_5x5.png"), dpi=150)
        print("Saved histograms →", os.path.join(args.outdir, "hist_9x3_6x4_5x5.png"))

    elif args.mode == "varmean":
        # variance vs mean for standard 9-inning games, varying outs
        pts = []
        for o in range(1,10):
            runs = []
            for s in range(args.sims):
                res = simulate_game(9, o, cfg)
                runs.append((res['team1']+res['team2'])/2.0)
            pts.append((float(np.mean(runs)), float(np.std(runs)), o))
        variance_vs_mean(pts, "Variance vs Mean Runs (9 innings; labels = outs per inning)")
        plt.savefig(os.path.join(args.outdir, "var_vs_mean.png"), dpi=150)
        print("Saved variance-vs-mean →", os.path.join(args.outdir, "var_vs_mean.png"))

if __name__ == "__main__":
    main()
