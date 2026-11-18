from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class Transfer:
    tx_hash: str
    log_index: int
    block_number: int
    timestamp: int
    from_address: str
    to_address: str
    amount: float
    source: str = "mainnet"
    scenario_label: str = "unknown"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class NodeFeatures:
    address: str
    in_count: int = 0
    out_count: int = 0
    in_amount: float = 0.0
    out_amount: float = 0.0
    unique_senders: set[str] = field(default_factory=set)
    unique_receivers: set[str] = field(default_factory=set)
    first_seen: int = 0
    last_seen: int = 0
    fast_forward_ratio: float = 0.0
    relay_ratio: float = 0.0
    seed_hops: int | None = None

    @property
    def tx_count(self) -> int:
        return self.in_count + self.out_count

    @property
    def active_span(self) -> int:
        return max(0, self.last_seen - self.first_seen)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["unique_senders"] = len(self.unique_senders)
        data["unique_receivers"] = len(self.unique_receivers)
        data["tx_count"] = self.tx_count
        data["active_span"] = self.active_span
        return data


@dataclass(frozen=True)
class Alert:
    address: str
    score: int
    severity: str
    reasons: tuple[dict[str, Any], ...]
    observed_at: int
    model_version: str = "rules-v1"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

