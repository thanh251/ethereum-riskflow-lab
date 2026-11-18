from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .abm import SimulationConfig, risk_ground_truth, simulate
from .config import PROCESSED_DIR, RAW_DIR, Settings
from .graph import build_graph
from .metrics import dataset_metrics, detection_metrics
from .models import Transfer
from .risk import score_graph
from .rpc import EthereumRpc, fetch_usdc_transfers
from .storage import file_sha256, write_json, write_transfers


def process(transfers: list[Transfer], settings: Settings, labels: dict[str, str] | None = None) -> dict:
    graph = build_graph(transfers, settings.seed_addresses)
    alerts = score_graph(graph.nodes.values())
    metrics = dataset_metrics(transfers, len(graph.nodes), len(graph.edges))
    if labels:
        metrics["detection"] = detection_metrics(
            alerts,
            risk_ground_truth(labels),
            set(graph.nodes),
        )
        metrics["agent_labels"] = {
            kind: sum(1 for value in labels.values() if value == kind)
            for kind in sorted(set(labels.values()))
        }
    write_json(PROCESSED_DIR / "graph.json", graph.to_dict())
    write_json(PROCESSED_DIR / "alerts.json", [item.to_dict() for item in alerts])
    write_json(PROCESSED_DIR / "metrics.json", metrics)
    return {"graph": graph, "alerts": alerts, "metrics": metrics}


def run_abm(config: SimulationConfig | None = None, settings: Settings | None = None) -> dict:
    cfg = config or SimulationConfig()
    active_settings = settings or Settings.from_env()
    transfers, labels = simulate(cfg)
    csv_path = RAW_DIR / f"abm_seed_{cfg.seed}.csv"
    write_transfers(csv_path, transfers)
    result = process(transfers, active_settings, labels)
    write_json(PROCESSED_DIR / "scenario.json", {
        "scenario_id": f"abm-{cfg.seed}",
        "seed": cfg.seed,
        "agents": cfg.agents,
        "steps": cfg.steps,
        "adaptive_intensity": cfg.adaptive_intensity,
        "csv": str(csv_path.relative_to(csv_path.parents[2])),
        "sha256": file_sha256(csv_path),
    })
    return result


def run_mainnet(settings: Settings | None = None, blocks: int | None = None) -> dict:
    active = settings or Settings.from_env()
    rpc = EthereumRpc(active.mainnet_rpc_url)
    latest = rpc.block_number()
    to_block = latest - active.confirmations
    count = blocks or active.blocks
    from_block = max(0, to_block - count + 1)
    transfers = fetch_usdc_transfers(rpc, from_block, to_block, active.rpc_block_chunk)
    csv_path = RAW_DIR / f"mainnet_usdc_{from_block}_{to_block}.csv"
    write_transfers(csv_path, transfers)
    manifest = {
        "chain_id": 1,
        "asset": "USDC",
        "contract": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "from_block": from_block,
        "to_block": to_block,
        "confirmations": active.confirmations,
        "transfer_count": len(transfers),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "csv": csv_path.name,
        "sha256": file_sha256(csv_path),
        "source": active.mainnet_rpc_url.split("?", 1)[0],
    }
    write_json(csv_path.with_suffix(".manifest.json"), manifest)
    result = process(transfers, active)
    write_json(PROCESSED_DIR / "source.json", manifest)
    return result

