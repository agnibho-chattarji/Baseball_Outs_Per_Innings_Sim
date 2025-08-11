import random
from typing import Dict, List, Tuple
import numpy as np
from .config import SimConfig, Batter

DEFAULT_BATTERS: Dict[str, Batter] = {
    'C':  Batter(BA=0.239, OBP=0.307),
    '1B': Batter(BA=0.249, OBP=0.324),
    '2B': Batter(BA=0.242, OBP=0.311),
    '3B': Batter(BA=0.245, OBP=0.317),
    'SS': Batter(BA=0.257, OBP=0.321),
    'LF': Batter(BA=0.248, OBP=0.321),
    'CF': Batter(BA=0.250, OBP=0.320),
    'RF': Batter(BA=0.255, OBP=0.324),
    'DH': Batter(BA=0.252, OBP=0.330),
}

LINEUP_DEFAULT = ['SS','2B','CF','1B','DH','RF','LF','3B','C']

# ---------------- Advancement helpers (calibrated) ----------------
def _force_walk(bases: List[int]) -> Tuple[List[int], int]:
    b1,b2,b3 = bases
    if b1 and b2 and b3:
        return [1,1,1], 1
    new_b3 = b3 or b2
    new_b2 = b2 or b1
    new_b1 = 1
    return [new_b1, new_b2, new_b3], 0

def _adv_single(bases: List[int], rng: random.Random) -> Tuple[List[int], int]:
    b1,b2,b3 = bases
    runs = 0
    runs += b3
    nb1, nb2, nb3 = 1,0,0  # batter to 1B
    if b2:
        if rng.random() < 0.68:
            runs += 1
        else:
            nb3 = 1
    if b1:
        if rng.random() < 0.30:
            nb3 = 1
        else:
            nb2 = 1
    return [nb1, nb2, nb3], runs

def _adv_double(bases: List[int], rng: random.Random) -> Tuple[List[int], int]:
    b1,b2,b3 = bases
    runs = 0
    runs += b3
    runs += b2
    nb3 = 0
    if b1:
        if rng.random() < 0.45:
            runs += 1
        else:
            nb3 = 1
    return [0,1,nb3], runs  # batter on 2B

def _adv_triple(bases: List[int]) -> Tuple[List[int], int]:
    b1,b2,b3 = bases
    return [0,0,1], (b1 + b2 + b3)

def _adv_homer(bases: List[int]) -> Tuple[List[int], int]:
    b1,b2,b3 = bases
    return [0,0,0], (b1 + b2 + b3 + 1)

def _maybe_steal(bases: List[int], outs: int, cfg: SimConfig, rng: random.Random) -> Tuple[List[int], int, int]:
    b1,b2,b3 = bases
    runs = 0; outs_added = 0
    # 1B -> 2B
    if b1 and not b2 and rng.random() < cfg.steal_att_1b_to_2b:
        if rng.random() < cfg.steal_succ_1b_to_2b:
            b1, b2 = 0, 1
        else:
            b1 = 0
            outs_added += 1
    # 2B -> 3B (avoid with 2 outs to keep it conservative)
    if b2 and not b3 and outs + outs_added < 2 and rng.random() < cfg.steal_att_2b_to_3b:
        if rng.random() < cfg.steal_succ_2b_to_3b:
            b2, b3 = 0, 1
        else:
            b2 = 0
            outs_added += 1
    return [b1,b2,b3], outs_added, runs

def simulate_half_inning(outs_per_inning: int, cfg: SimConfig,
                         start_batter_idx: int = 0,
                         rng: random.Random = None) -> Tuple[int, int, List[int]]:
    """IMPORTANT: Bases persist until the inning ENDS; inning ends after outs_per_inning outs."""
    if rng is None:
        rng = random.Random()
    lineup = cfg.lineup or LINEUP_DEFAULT
    batters = cfg.batters or DEFAULT_BATTERS
    hd = cfg.hit_distribution

    outs = 0; runs = 0; bases = [0,0,0]; batter_idx = start_batter_idx
    s = hd['single']; d = s + hd['double']; t = d + hd['triple']

    while outs < outs_per_inning:
        # pre-PA steals
        bases, steal_outs, steal_runs = _maybe_steal(bases, outs, cfg, rng)
        outs += steal_outs; runs += steal_runs
        if outs >= outs_per_inning:
            break

        pos = lineup[batter_idx % len(lineup)]
        batter = batters[pos]
        prob_walk = max(0.0, batter.OBP - batter.BA) + cfg.walk_hbp_bump
        prob_hit = batter.BA

        r = rng.random()
        if r < prob_walk:
            bases, r_scored = _force_walk(bases); runs += r_scored
        elif r < prob_walk + prob_hit:
            r2 = rng.random()
            if r2 < s:
                bases, r_scored = _adv_single(bases, rng)
            elif r2 < d:
                bases, r_scored = _adv_double(bases, rng)
            elif r2 < t:
                bases, r_scored = _adv_triple(bases)
            else:
                bases, r_scored = _adv_homer(bases)
            runs += r_scored
        else:
            outs += 1

        batter_idx += 1

    return runs, batter_idx % len(lineup), bases

def simulate_game(innings: int, outs_per_inning: int, cfg: SimConfig, return_progress=False):
    rng = random.Random(cfg.seed)
    lineup = cfg.lineup or LINEUP_DEFAULT
    batters = cfg.batters or DEFAULT_BATTERS
    hd = cfg.hit_distribution

    t1_runs = 0; t2_runs = 0
    t1_bidx = 0; t2_bidx = 0
    if return_progress:
        t1_prog, t2_prog = [], []

    for _ in range(innings):
        r1, t1_bidx, _ = simulate_half_inning(outs_per_inning, cfg, start_batter_idx=t1_bidx, rng=rng)
        r2, t2_bidx, _ = simulate_half_inning(outs_per_inning, cfg, start_batter_idx=t2_bidx, rng=rng)
        t1_runs += r1; t2_runs += r2
        if return_progress:
            t1_prog.append(t1_runs); t2_prog.append(t2_runs)

    if return_progress:
        return (t1_runs, t2_runs), (t1_prog, t2_prog)
    return {'team1': t1_runs, 'team2': t2_runs, 'total': t1_runs + t2_runs}

def simulate_many(innings: int, outs_per_inning: int, cfg: SimConfig, n: int = 2000):
    totals = []; t1s = []; t2s = []
    seed0 = cfg.seed
    for i in range(n):
        cfg.seed = seed0 + i*7919
        res = simulate_game(innings, outs_per_inning, cfg)
        totals.append(res['total']); t1s.append(res['team1']); t2s.append(res['team2'])
    cfg.seed = seed0
    return {
        'avg_total_runs': float(np.mean(totals)),
        'std_total_runs': float(np.std(totals)),
        'avg_runs_per_team': float(np.mean(t1s + t2s)),
        'std_runs_per_team': float(np.std(t1s + t2s)),
    }

def expected_runs_per_inning_curve(cfg: SimConfig, max_outs: int = 9, sims_per_point: int = 4000):
    ev, sd = [], []
    seed0 = cfg.seed
    for o in range(1, max_outs+1):
        runs = []
        for i in range(sims_per_point):
            cfg.seed = seed0 + i*104729 + o*1299709
            r, _, _ = simulate_half_inning(o, cfg, start_batter_idx=0, rng=random.Random(cfg.seed))
            runs.append(r)
        ev.append(float(np.mean(runs))); sd.append(float(np.std(runs)))
    cfg.seed = seed0
    return {'outs': list(range(1, max_outs+1)), 'ev': ev, 'sd': sd}
