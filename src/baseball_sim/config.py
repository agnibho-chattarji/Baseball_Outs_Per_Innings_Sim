from dataclasses import dataclass, field
from typing import Dict, List

@dataclass
class Batter:
    BA: float
    OBP: float

@dataclass
class SimConfig:
    lineup: List[str] = field(default_factory=lambda: ['SS','2B','CF','1B','DH','RF','LF','3B','C'])
    batters: Dict[str, 'Batter'] = field(default_factory=dict)
    hit_distribution: Dict[str, float] = field(default_factory=lambda: {
        'single': 0.69, 'double': 0.21, 'triple': 0.02, 'home_run': 0.08
    })
    # Steal parameters (aggregate, rough calibration)
    steal_att_1b_to_2b: float = 0.02
    steal_att_2b_to_3b: float = 0.006
    steal_succ_1b_to_2b: float = 0.74
    steal_succ_2b_to_3b: float = 0.70
    # Walk/HBP bump to nudge baserunners
    walk_hbp_bump: float = 0.003
    seed: int = 42
