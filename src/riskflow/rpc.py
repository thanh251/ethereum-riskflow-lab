from __future__ import annotations

import json
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .config import TRANSFER_TOPIC, USDC_MAINNET
from .models import Transfer


class RpcError(RuntimeError):
    pass


class EthereumRpc:
    def __init__(self, url: str, timeout: int = 45, retries: int = 3):
        self.url = url
        self.timeout = timeout
        self.retries = retries
        self._request_id = 0

    def call(self, method: str, params: list) -> object:
        self._request_id += 1
        payload = json.dumps(
            {"jsonrpc": "2.0", "id": self._request_id, "method": method, "params": params}
        ).encode("utf-8")
        request = Request(
            self.url,
            data=payload,
            headers={"Content-Type": "application/json", "User-Agent": "Ethereum-RiskFlow-Lab/0.1"},
            method="POST",
        )
        last_error: Exception | None = None
        for attempt in range(self.retries):
            try:
                with urlopen(request, timeout=self.timeout) as response:
                    body = json.loads(response.read().decode("utf-8"))
                if "error" in body:
                    raise RpcError(f"{method}: {body['error']}")
                return body.get("result")
            except (HTTPError, URLError, TimeoutError, RpcError) as exc:
                last_error = exc
                if attempt + 1 < self.retries:
                    time.sleep(1.5 * (attempt + 1))
        raise RpcError(f"RPC request failed after {self.retries} attempts: {last_error}")

    def block_number(self) -> int:
        return int(str(self.call("eth_blockNumber", [])), 16)

    def block(self, block_number: int) -> dict:
        result = self.call("eth_getBlockByNumber", [hex(block_number), False])
        if not isinstance(result, dict):
            raise RpcError(f"Block {block_number} was not returned")
        return result

    def logs(self, from_block: int, to_block: int) -> list[dict]:
        result = self.call(
            "eth_getLogs",
            [{
                "fromBlock": hex(from_block),
                "toBlock": hex(to_block),
                "address": USDC_MAINNET,
                "topics": [TRANSFER_TOPIC],
            }],
        )
        if not isinstance(result, list):
            raise RpcError("eth_getLogs returned an unexpected response")
        return result


def topic_address(topic: str) -> str:
    value = topic.lower().removeprefix("0x")
    if len(value) != 64:
        raise ValueError(f"Invalid indexed address topic: {topic}")
    return "0x" + value[-40:]


def parse_usdc_log(log: dict, timestamp: int) -> Transfer:
    topics = log.get("topics", [])
    if len(topics) < 3:
        raise ValueError("Transfer log is missing indexed addresses")
    return Transfer(
        tx_hash=str(log["transactionHash"]).lower(),
        log_index=int(str(log["logIndex"]), 16),
        block_number=int(str(log["blockNumber"]), 16),
        timestamp=timestamp,
        from_address=topic_address(str(topics[1])),
        to_address=topic_address(str(topics[2])),
        amount=int(str(log.get("data", "0x0")), 16) / 1_000_000,
        source="mainnet",
    )


def fetch_usdc_transfers(
    rpc: EthereumRpc,
    from_block: int,
    to_block: int,
    chunk_size: int = 20,
) -> list[Transfer]:
    if from_block > to_block:
        raise ValueError("from_block must be <= to_block")
    transfers: list[Transfer] = []
    timestamps: dict[int, int] = {}
    seen: set[tuple[str, int]] = set()
    start = from_block
    while start <= to_block:
        end = min(start + chunk_size - 1, to_block)
        for log in rpc.logs(start, end):
            block_number = int(str(log["blockNumber"]), 16)
            if block_number not in timestamps:
                timestamps[block_number] = int(str(rpc.block(block_number)["timestamp"]), 16)
            transfer = parse_usdc_log(log, timestamps[block_number])
            key = (transfer.tx_hash, transfer.log_index)
            if key not in seen:
                seen.add(key)
                transfers.append(transfer)
        start = end + 1
    return sorted(transfers, key=lambda item: (item.block_number, item.log_index))

