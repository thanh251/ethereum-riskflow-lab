from __future__ import annotations

import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from riskflow.rpc import parse_usdc_log, topic_address


class RpcParsingTests(unittest.TestCase):
    def test_topic_address(self):
        address = "1234567890abcdef1234567890abcdef12345678"
        self.assertEqual(topic_address("0x" + "0" * 24 + address), "0x" + address)

    def test_usdc_decimals(self):
        source = "11" * 20
        target = "22" * 20
        log = {
            "transactionHash": "0x" + "ab" * 32,
            "logIndex": "0x2",
            "blockNumber": "0x64",
            "topics": ["0x0", "0x" + "0" * 24 + source, "0x" + "0" * 24 + target],
            "data": hex(1_250_000),
        }
        transfer = parse_usdc_log(log, 1234)
        self.assertEqual(transfer.amount, 1.25)
        self.assertEqual(transfer.log_index, 2)
        self.assertEqual(transfer.block_number, 100)


if __name__ == "__main__":
    unittest.main()

