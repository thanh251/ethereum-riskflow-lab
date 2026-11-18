from __future__ import annotations

import argparse
import json

from .abm import SimulationConfig
from .pipeline import run_abm, run_mainnet
from .server import serve


def main() -> None:
    parser = argparse.ArgumentParser(prog="riskflow")
    sub = parser.add_subparsers(dest="command", required=True)
    abm = sub.add_parser("abm", help="Run the deterministic ABM demo")
    abm.add_argument("--agents", type=int, default=300)
    abm.add_argument("--steps", type=int, default=24)
    abm.add_argument("--seed", type=int, default=20261021)
    abm.add_argument("--adaptive-intensity", type=float, default=0.55)
    mainnet = sub.add_parser("mainnet", help="Fetch confirmed Mainnet USDC transfers")
    mainnet.add_argument("--blocks", type=int, default=None)
    dashboard = sub.add_parser("dashboard", help="Serve the local dashboard")
    dashboard.add_argument("--host", default=None)
    dashboard.add_argument("--port", type=int, default=None)
    args = parser.parse_args()

    if args.command == "abm":
        result = run_abm(SimulationConfig(
            agents=args.agents,
            steps=args.steps,
            seed=args.seed,
            adaptive_intensity=args.adaptive_intensity,
        ))
        print(json.dumps(result["metrics"], ensure_ascii=False, indent=2))
    elif args.command == "mainnet":
        result = run_mainnet(blocks=args.blocks)
        print(json.dumps(result["metrics"], ensure_ascii=False, indent=2))
    else:
        serve(args.host, args.port)


if __name__ == "__main__":
    main()

