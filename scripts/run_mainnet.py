from __future__ import annotations

import argparse
import json

import _bootstrap  # noqa: F401
from riskflow.pipeline import run_mainnet


parser = argparse.ArgumentParser()
parser.add_argument("--blocks", type=int, default=None)
args = parser.parse_args()

result = run_mainnet(blocks=args.blocks)
print(json.dumps(result["metrics"], ensure_ascii=False, indent=2))

