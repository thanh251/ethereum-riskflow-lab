from __future__ import annotations

import argparse
import json

import _bootstrap  # noqa: F401
from riskflow.abm import SimulationConfig
from riskflow.pipeline import run_abm


parser = argparse.ArgumentParser()
parser.add_argument("--agents", type=int, default=300)
parser.add_argument("--steps", type=int, default=24)
parser.add_argument("--seed", type=int, default=20261021)
parser.add_argument("--adaptive-intensity", type=float, default=0.55)
args = parser.parse_args()

result = run_abm(SimulationConfig(
    agents=args.agents,
    steps=args.steps,
    seed=args.seed,
    adaptive_intensity=args.adaptive_intensity,
))
print(json.dumps(result["metrics"], ensure_ascii=False, indent=2))

