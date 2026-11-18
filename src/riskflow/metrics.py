from __future__ import annotations

from statistics import median

from .models import Alert, Transfer


def detection_metrics(alerts: list[Alert], truth: set[str], universe: set[str], threshold: int = 40) -> dict:
    predicted = {alert.address for alert in alerts if alert.score >= threshold}
    tp = len(predicted & truth)
    fp = len(predicted - truth)
    fn = len(truth - predicted)
    tn = len(universe - truth - predicted)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    fpr = fp / (fp + tn) if fp + tn else 0.0
    return {
        "threshold": threshold,
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "false_positive_rate": round(fpr, 4),
    }


def dataset_metrics(transfers: list[Transfer], node_count: int, edge_count: int) -> dict:
    amounts = [item.amount for item in transfers]
    timestamps = [item.timestamp for item in transfers]
    return {
        "transfer_count": len(transfers),
        "node_count": node_count,
        "edge_count": edge_count,
        "total_amount": round(sum(amounts), 6),
        "median_amount": round(median(amounts), 6) if amounts else 0,
        "first_timestamp": min(timestamps) if timestamps else None,
        "last_timestamp": max(timestamps) if timestamps else None,
    }

