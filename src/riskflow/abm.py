from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import random
from typing import Iterable

from .models import Transfer


AGENT_TYPES = ("normal", "payment", "disperse", "consolidate", "relay", "adaptive")


def address_for(seed: int, index: int) -> str:
    digest = sha256(f"riskflow:{seed}:{index}".encode()).hexdigest()
    return "0x" + digest[-40:]


@dataclass
class Agent:
    address: str
    kind: str
    balance: float


@dataclass(frozen=True)
class SimulationConfig:
    agents: int = 300
    steps: int = 24
    seed: int = 20261021
    start_timestamp: int = 1_770_000_000
    step_seconds: int = 300
    adaptive_intensity: float = 0.55


def make_agents(config: SimulationConfig) -> list[Agent]:
    rng = random.Random(config.seed)
    weights = [0.68, 0.12, 0.06, 0.05, 0.05, 0.04]
    kinds = rng.choices(AGENT_TYPES, weights=weights, k=config.agents)
    # Guarantee all scenario types exist in small runs.
    for index, kind in enumerate(AGENT_TYPES):
        if index < len(kinds):
            kinds[index] = kind
    return [
        Agent(address_for(config.seed, index), kind, rng.uniform(4_000, 20_000))
        for index, kind in enumerate(kinds)
    ]


def simulate(config: SimulationConfig | None = None) -> tuple[list[Transfer], dict[str, str]]:
    cfg = config or SimulationConfig()
    rng = random.Random(cfg.seed)
    agents = make_agents(cfg)
    # Ground truth is assigned only when an agent actually participates in a
    # generated risk scenario; a risky role that never acts is not a positive.
    labels = {agent.address: "normal" for agent in agents}
    by_kind: dict[str, list[Agent]] = {kind: [] for kind in AGENT_TYPES}
    for agent in agents:
        by_kind[agent.kind].append(agent)

    transfers: list[Transfer] = []
    counter = 0

    def emit(source: Agent, target: Agent, amount: float, timestamp: int, label: str) -> None:
        nonlocal counter
        amount = round(min(amount, max(0.0, source.balance)), 6)
        if amount <= 0 or source.address == target.address:
            return
        source.balance -= amount
        target.balance += amount
        digest = sha256(f"{cfg.seed}:{counter}:{source.address}:{target.address}".encode()).hexdigest()
        transfers.append(Transfer(
            tx_hash="0x" + digest,
            log_index=0,
            block_number=counter // 8,
            timestamp=timestamp,
            from_address=source.address,
            to_address=target.address,
            amount=amount,
            source="abm",
            scenario_label=label,
        ))
        counter += 1

    for step in range(cfg.steps):
        ts = cfg.start_timestamp + step * cfg.step_seconds
        active = rng.sample(agents, k=max(2, int(len(agents) * 0.08)))
        for agent in active:
            if agent.kind == "normal" and rng.random() < 0.35:
                emit(agent, rng.choice(agents), rng.uniform(20, 450), ts + rng.randrange(cfg.step_seconds), "normal")
            elif agent.kind == "payment" and step % 6 == 0:
                for target in rng.sample(agents, k=min(6, len(agents))):
                    emit(agent, target, rng.uniform(15, 120), ts + rng.randrange(90), "legitimate_fanout")
            elif agent.kind == "disperse" and step % 8 == 1:
                labels[agent.address] = "disperse"
                for target in rng.sample(agents, k=min(9, len(agents))):
                    emit(agent, target, rng.uniform(90, 260), ts + rng.randrange(120), "risk_fanout")
            elif agent.kind == "consolidate" and step % 8 == 3:
                labels[agent.address] = "consolidate"
                for source in rng.sample(agents, k=min(9, len(agents))):
                    emit(source, agent, rng.uniform(70, 220), ts + rng.randrange(120), "risk_fanin")
            elif agent.kind in {"relay", "adaptive"} and rng.random() < 0.70:
                target = rng.choice(agents)
                base = rng.uniform(120, 550)
                if agent.kind == "adaptive":
                    base *= max(0.15, 1.0 - cfg.adaptive_intensity)
                    delay = int(cfg.step_seconds * cfg.adaptive_intensity)
                else:
                    delay = rng.randrange(60)
                emit(agent, target, base, ts + delay, f"risk_{agent.kind}")

        # Explicit fan-out -> fast relay -> fan-in patterns create controlled
        # positive examples while legitimate payment fan-out remains a hard negative.
        if step in {4, 12, 20}:
            origins = (by_kind["disperse"] or agents)[:2]
            relays = (by_kind["relay"] + by_kind["adaptive"] or agents)[:6]
            sink = (by_kind["consolidate"] or agents)[step % len(by_kind["consolidate"] or agents)]
            labels[sink.address] = "consolidate"
            for origin in origins:
                labels[origin.address] = "disperse"
                for relay in relays:
                    labels[relay.address] = relay.kind if relay.kind in {"relay", "adaptive"} else "relay"
                    amount = rng.uniform(150, 310)
                    emit(origin, relay, amount, ts + rng.randrange(20), "risk_fanout")
                    emit(relay, sink, amount * 0.985, ts + 45 + rng.randrange(20), "risk_fast_relay")

    return sorted(transfers, key=lambda item: (item.timestamp, item.tx_hash)), labels


def risk_ground_truth(labels: dict[str, str]) -> set[str]:
    return {address for address, kind in labels.items() if kind in {"disperse", "consolidate", "relay", "adaptive"}}

