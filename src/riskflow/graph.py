from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Iterable

from .models import NodeFeatures, Transfer


ZERO_ADDRESS = "0x0000000000000000000000000000000000000000"


@dataclass
class TemporalGraph:
    transfers: list[Transfer]
    nodes: dict[str, NodeFeatures]
    edges: dict[tuple[str, str], dict]
    adjacency: dict[str, set[str]]

    def to_dict(self, node_limit: int = 250, edge_limit: int = 700) -> dict:
        ranked = sorted(self.nodes.values(), key=lambda node: (node.tx_count, node.in_amount + node.out_amount), reverse=True)
        selected = {node.address for node in ranked[:node_limit]}
        nodes = [node.to_dict() for node in ranked[:node_limit]]
        edge_rows = []
        for (source, target), data in sorted(
            self.edges.items(), key=lambda item: item[1]["amount"], reverse=True
        ):
            if source in selected and target in selected:
                edge_rows.append({"source": source, "target": target, **data})
            if len(edge_rows) >= edge_limit:
                break
        return {"nodes": nodes, "edges": edge_rows, "meta": {"node_count": len(self.nodes), "edge_count": len(self.edges)}}


def build_graph(
    transfers: Iterable[Transfer],
    seed_addresses: Iterable[str] = (),
    fast_window_seconds: int = 900,
) -> TemporalGraph:
    ordered = sorted(transfers, key=lambda item: (item.timestamp, item.block_number, item.log_index))
    nodes: dict[str, NodeFeatures] = {}
    edges: dict[tuple[str, str], dict] = {}
    adjacency: dict[str, set[str]] = defaultdict(set)
    incoming_times: dict[str, deque[int]] = defaultdict(deque)
    fast_out: dict[str, int] = defaultdict(int)

    def node(address: str, ts: int) -> NodeFeatures:
        if address not in nodes:
            nodes[address] = NodeFeatures(address=address, first_seen=ts, last_seen=ts)
        current = nodes[address]
        current.first_seen = min(current.first_seen, ts)
        current.last_seen = max(current.last_seen, ts)
        return current

    for tx in ordered:
        source = tx.from_address.lower()
        target = tx.to_address.lower()
        if source == ZERO_ADDRESS or target == ZERO_ADDRESS:
            continue
        source_node = node(source, tx.timestamp)
        target_node = node(target, tx.timestamp)
        source_node.out_count += 1
        source_node.out_amount += tx.amount
        source_node.unique_receivers.add(target)
        target_node.in_count += 1
        target_node.in_amount += tx.amount
        target_node.unique_senders.add(source)

        while incoming_times[source] and tx.timestamp - incoming_times[source][0] > fast_window_seconds:
            incoming_times[source].popleft()
        if incoming_times[source]:
            fast_out[source] += 1
        incoming_times[target].append(tx.timestamp)

        key = (source, target)
        if key not in edges:
            edges[key] = {"amount": 0.0, "count": 0, "first_seen": tx.timestamp, "last_seen": tx.timestamp}
        edge = edges[key]
        edge["amount"] = round(edge["amount"] + tx.amount, 6)
        edge["count"] += 1
        edge["first_seen"] = min(edge["first_seen"], tx.timestamp)
        edge["last_seen"] = max(edge["last_seen"], tx.timestamp)
        adjacency[source].add(target)
        adjacency[target].add(source)

    for address, features in nodes.items():
        features.fast_forward_ratio = fast_out[address] / max(1, features.out_count)
        smaller = min(features.in_amount, features.out_amount)
        larger = max(features.in_amount, features.out_amount, 1e-9)
        features.relay_ratio = smaller / larger

    queue: deque[tuple[str, int]] = deque()
    for seed in {item.lower() for item in seed_addresses}:
        if seed in nodes:
            nodes[seed].seed_hops = 0
            queue.append((seed, 0))
    while queue:
        address, hops = queue.popleft()
        if hops >= 3:
            continue
        for neighbor in adjacency.get(address, set()):
            candidate = hops + 1
            current = nodes[neighbor].seed_hops
            if current is None or candidate < current:
                nodes[neighbor].seed_hops = candidate
                queue.append((neighbor, candidate))
    return TemporalGraph(ordered, nodes, edges, dict(adjacency))

