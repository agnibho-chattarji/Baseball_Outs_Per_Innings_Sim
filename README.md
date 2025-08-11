# Baseball Outs-per-Inning Simulator (v2)

Link to Medium article: [3 Outs? Try 5. The Data Says Baseball Would Be Shorter, Faster, and More Exciting](https://medium.com/p/e5f1b88c72bf)

Calibrated Monte Carlo simulator exploring baseball with **arbitrary outs per inning**, keeping baserunners **after 3 outs** (bases clear only when the inning ends). Includes **realistic base advancement**, **simple steals**, and a full **figure suite** for articles: heatmaps, histograms, variance vs mean, and EV curves.

## Install
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Quickstart
```bash
# Metrics for 9 innings × 3 outs
python src/cli.py --mode metrics --innings 9 --outs 3

# EV curve (outs 1..9)
python src/cli.py --mode curve --curve-sims 4000

# Heatmap of average runs per TEAM (1..9 outs × 1..9 innings)
python src/cli.py --mode grid --sims 800

# Run distribution histograms for 9×3 vs 6×4 vs 5×5
python src/cli.py --mode hist --sims 2000

# Variance vs mean for 9-inning games (vary outs)
python src/cli.py --mode varmean --sims 1500
```

All figures saved in `outputs/`.

## Config
Edit `configs/default.yaml` to change lineup stats, hit mix, steal rates, or walk/HBP bump. Defaults are lightly calibrated to place **9×3 ≈ 4.1–4.3 runs per TEAM**.

## Modeling Notes
- Event probs: **Walk/HBP ≈ OBP − BA + bump; Hit ≈ BA**; within hits, use `hit_distribution`.
- **Advancement**: singles often score runner from 2B; doubles sometimes score runner from 1B; HR clears bases.
- **Steals**: low attempt rates; occasional outs add variance.
- **Bases persist** through any number of outs — inning ends only at outs limit.

## License
MIT
