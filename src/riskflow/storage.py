from __future__ import annotations

import csv
from dataclasses import asdict
from hashlib import sha256
import json
from pathlib import Path
from typing import Iterable

from .models import Transfer


TRANSFER_FIELDS = [
    "tx_hash", "log_index", "block_number", "timestamp", "from_address",
    "to_address", "amount", "source", "scenario_label",
]


def write_transfers(path: Path, transfers: Iterable[Transfer]) -> int:
    rows = list(transfers)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=TRANSFER_FIELDS)
        writer.writeheader()
        for transfer in rows:
            writer.writerow(asdict(transfer))
    return len(rows)


def read_transfers(path: Path) -> list[Transfer]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [
            Transfer(
                tx_hash=row["tx_hash"],
                log_index=int(row["log_index"]),
                block_number=int(row["block_number"]),
                timestamp=int(row["timestamp"]),
                from_address=row["from_address"].lower(),
                to_address=row["to_address"].lower(),
                amount=float(row["amount"]),
                source=row.get("source", "mainnet"),
                scenario_label=row.get("scenario_label", "unknown"),
            )
            for row in csv.DictReader(handle)
        ]


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path, default: object | None = None) -> object:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))

