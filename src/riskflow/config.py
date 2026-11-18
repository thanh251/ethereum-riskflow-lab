from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
USDC_MAINNET = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"


def load_dotenv(path: Path | None = None) -> None:
    env_path = path or PROJECT_ROOT / ".env"
    if not env_path.exists():
        return
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


@dataclass(frozen=True)
class Settings:
    mainnet_rpc_url: str
    confirmations: int = 12
    blocks: int = 120
    rpc_block_chunk: int = 20
    dashboard_host: str = "127.0.0.1"
    dashboard_port: int = 8080
    seed_addresses: tuple[str, ...] = ()

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        seeds = tuple(
            item.strip().lower()
            for item in os.getenv("SEED_ADDRESSES", "").split(",")
            if item.strip()
        )
        return cls(
            mainnet_rpc_url=os.getenv("MAINNET_RPC_URL", "https://ethereum-rpc.publicnode.com"),
            confirmations=int(os.getenv("MAINNET_CONFIRMATIONS", "12")),
            blocks=int(os.getenv("MAINNET_BLOCKS", "120")),
            rpc_block_chunk=max(1, int(os.getenv("RPC_BLOCK_CHUNK", "20"))),
            dashboard_host=os.getenv("DASHBOARD_HOST", "127.0.0.1"),
            dashboard_port=int(os.getenv("DASHBOARD_PORT", "8080")),
            seed_addresses=seeds,
        )


for directory in (RAW_DIR, PROCESSED_DIR):
    directory.mkdir(parents=True, exist_ok=True)

