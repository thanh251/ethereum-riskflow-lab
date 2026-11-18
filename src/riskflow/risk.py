from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .models import Alert, NodeFeatures


@dataclass(frozen=True)
class RiskThresholds:
    fan_out: int = 5
    fan_in: int = 5
    fast_forward_ratio: float = 0.60
    relay_ratio: float = 0.80
    new_wallet_span: int = 3600
    new_wallet_tx_count: int = 4


def severity(score: int) -> str:
    if score >= 70:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


def score_node(node: NodeFeatures, thresholds: RiskThresholds | None = None) -> Alert:
    rules = thresholds or RiskThresholds()
    reasons: list[dict] = []
    score = 0

    def add(code: str, points: int, value: object, threshold: object, message: str) -> None:
        nonlocal score
        score += points
        reasons.append({"code": code, "points": points, "value": value, "threshold": threshold, "message": message})

    receivers = len(node.unique_receivers)
    senders = len(node.unique_senders)
    if receivers >= rules.fan_out:
        add("FAN_OUT", 25, receivers, rules.fan_out, "Chuyển tới nhiều địa chỉ trong cửa sổ quan sát")
    if senders >= rules.fan_in:
        add("FAN_IN", 25, senders, rules.fan_in, "Nhận tiền từ nhiều địa chỉ trong cửa sổ quan sát")
    if node.out_count >= 2 and node.fast_forward_ratio >= rules.fast_forward_ratio:
        add("FAST_FORWARD", 25, round(node.fast_forward_ratio, 3), rules.fast_forward_ratio, "Tiền thường được chuyển tiếp nhanh sau khi nhận")
    if node.in_count >= 2 and node.out_count >= 2 and node.relay_ratio >= rules.relay_ratio:
        add("RELAY_BALANCE", 17, round(node.relay_ratio, 3), rules.relay_ratio, "Giá trị vào và ra cân bằng, phù hợp vai trò chuyển tiếp")
    if node.tx_count >= rules.new_wallet_tx_count and node.active_span <= rules.new_wallet_span:
        add("BURST_NEW", 15, node.active_span, rules.new_wallet_span, "Hoạt động dày trong một khoảng thời gian ngắn")
    if node.seed_hops is not None and node.seed_hops <= 3:
        exposure_points = {0: 40, 1: 30, 2: 20, 3: 10}[node.seed_hops]
        add("SEED_EXPOSURE", exposure_points, node.seed_hops, 3, "Có đường đi tới seed address công khai")

    final_score = min(100, score)
    return Alert(
        address=node.address,
        score=final_score,
        severity=severity(final_score),
        reasons=tuple(reasons),
        observed_at=node.last_seen,
    )


def score_graph(nodes: Iterable[NodeFeatures], minimum_score: int = 20) -> list[Alert]:
    alerts = [score_node(node) for node in nodes]
    return sorted((alert for alert in alerts if alert.score >= minimum_score), key=lambda item: item.score, reverse=True)

