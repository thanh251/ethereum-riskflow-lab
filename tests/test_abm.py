from __future__ import annotations

import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from riskflow.abm import SimulationConfig, simulate
from riskflow.graph import build_graph
from riskflow.risk import score_graph


class AbmTests(unittest.TestCase):
    def test_seed_is_reproducible(self):
        cfg = SimulationConfig(agents=60, steps=8, seed=42)
        first, labels_a = simulate(cfg)
        second, labels_b = simulate(cfg)
        self.assertEqual(first, second)
        self.assertEqual(labels_a, labels_b)

    def test_simulation_produces_alerts(self):
        transfers, _ = simulate(SimulationConfig(agents=120, steps=16, seed=7))
        graph = build_graph(transfers)
        alerts = score_graph(graph.nodes.values())
        self.assertTrue(transfers)
        self.assertTrue(alerts)
        self.assertGreaterEqual(max(alert.score for alert in alerts), 40)


if __name__ == "__main__":
    unittest.main()

