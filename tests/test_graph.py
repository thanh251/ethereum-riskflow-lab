from __future__ import annotations

import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from riskflow.graph import build_graph
from riskflow.models import Transfer
from riskflow.risk import score_node


def tx(index: int, source: str, target: str, ts: int, amount: float = 100) -> Transfer:
    return Transfer(f"0x{index:064x}", 0, index, ts, source, target, amount, "test")


class GraphTests(unittest.TestCase):
    def test_fan_out_and_fast_forward(self):
        hub = "0x" + "1" * 40
        source = "0x" + "2" * 40
        transfers = [tx(0, source, hub, 100)]
        transfers.extend(tx(i + 1, hub, "0x" + f"{i+3:040x}", 120 + i, 10) for i in range(6))
        graph = build_graph(transfers)
        node = graph.nodes[hub]
        self.assertEqual(len(node.unique_receivers), 6)
        self.assertGreaterEqual(node.fast_forward_ratio, 0.9)
        alert = score_node(node)
        codes = {reason["code"] for reason in alert.reasons}
        self.assertIn("FAN_OUT", codes)
        self.assertIn("FAST_FORWARD", codes)

    def test_seed_hops(self):
        a, b, c = ("0x" + char * 40 for char in "abc")
        graph = build_graph([tx(1, a, b, 1), tx(2, b, c, 2)], [a])
        self.assertEqual(graph.nodes[a].seed_hops, 0)
        self.assertEqual(graph.nodes[b].seed_hops, 1)
        self.assertEqual(graph.nodes[c].seed_hops, 2)


if __name__ == "__main__":
    unittest.main()

