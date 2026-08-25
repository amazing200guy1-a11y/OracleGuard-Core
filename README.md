# OracleGuard-Core: Multi-Source Price Oracle & Anti-Manipulation Engine

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![AsyncIO](https://img.shields.io/badge/AsyncIO-Native-brightgreen?style=for-the-badge)
![Pytest](https://img.shields.io/badge/Pytest-8.x-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)
![Integrity](https://img.shields.io/badge/Data%20Integrity-Fail--Closed-red?style=for-the-badge)

**Independent multi-source price oracle** that continuously cross-checks institutional and exchange feeds.  
Any statistically significant divergence is treated as potential quote manipulation or a flash-crash artefact and immediately triggers a system-wide halt.

Built for quantitative and fintech platforms that cannot afford to trade on a single broker’s potentially skewed quotes.

> Live API credentials and production feed endpoints remain private.  
> This repository is an architectural showcase of data-integrity patterns for elite infrastructure and pipeline roles.

---

## Deviation Matrix
[ FEED A: REUTERS ]   [ FEED B: BLOOMBERG ]   [ FEED C: COINBASE ]
           │                     │                     │
           └─────────────────────┼─────────────────────┘
                                 ▼
                 ┌───────────────────────────────┐
                 │   ORACLEGUARD DEVIATION ENGINE│
                 │  Cross-checks price candles   │
                 └───────────────┬───────────────┘
                                 │
                 ┌───────────────┴───────────────┐
     [ Price Deviation < 0.1% ]      [ Price Deviation ≥ 0.1% ]
                 │                               │
                 ▼                               ▼
   ┌───────────────────────────┐   ┌───────────────────────────┐
   │   VALIDATED SYSTEM PRICE  │   │   BROKER MANIPULATION DET.│
   │  Feeds clean data to swarm│   │  Halts execution instantly│
   └───────────────────────────┘   └───────────────────────────┘
---

## How Manipulation Is Detected

1. **Concurrent fetch** — three independent feeds are queried in parallel via `asyncio.gather`.
2. **Mid-price calculation** — each feed contributes a mid (or last) price.
3. **Relative deviation** — the maximum pairwise percentage difference is computed.
4. **Hard threshold** — if any pair diverges by ≥ 0.10 %, the engine raises a `ManipulationDetected` exception and the caller must halt execution.
5. **Fail-closed** — timeouts, malformed payloads or missing fields are treated as integrity failures.

This design catches classic B-book quote shading, stale feeds and sudden one-sided spikes before they can influence downstream trading logic.

---

## Design Principles

- High-concurrency I/O with a single shared `httpx.AsyncClient`.
- Deterministic, parameterised threshold (default 0.10 %).
- Explicit typed results and structured exceptions.
- Zero silent degradation — every anomaly surfaces as an error.

---

## Quick Start

```bash
pip install -r requirements.txt   # or: pip install httpx pytest pytest-asyncio
python oracle_bridge.py
pytest test_oracle.py -v
Repository Layout
OracleGuard-Core/
├── README.md
├── oracle_bridge.py      # Async multi-feed oracle
└── test_oracle.py        # Manipulation-attack test suite
Attribution
Architected by an Infrastructure & Data Integrity Architect.
This repository demonstrates production-grade anti-manipulation oracle patterns for fintech and quantitative systems.
Protected under proprietary guidelines. All rights reserved.
