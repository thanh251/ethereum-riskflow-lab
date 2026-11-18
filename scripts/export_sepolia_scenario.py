from __future__ import annotations

import json

import _bootstrap  # noqa: F401
from riskflow.config import PROCESSED_DIR
from riskflow.storage import read_json, write_json


graph = read_json(PROCESSED_DIR / "graph.json", {"nodes": [], "edges": []})
alerts = read_json(PROCESSED_DIR / "alerts.json", [])
scenario = read_json(PROCESSED_DIR / "scenario.json", {})
alert_map = {item["address"]: item for item in alerts}
selected_edges = sorted(graph.get("edges", []), key=lambda item: item.get("amount", 0), reverse=True)[:100]
payload = {
    "scenario_id": scenario.get("scenario_id", "manual-mainnet-derived"),
    "note": "Replay with MockUSDC only; no Mainnet balances or private data are copied.",
    "transfers": [
        {
            "from_agent": edge["source"],
            "to_agent": edge["target"],
            "amount_micro_usdc": int(round(edge["amount"] * 1_000_000)),
            "risk_score": alert_map.get(edge["target"], {}).get("score", 0),
        }
        for edge in selected_edges
    ],
}
output = PROCESSED_DIR / "sepolia_payload.json"
write_json(output, payload)
print(output)

