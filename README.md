# OracleGuard-Core: Multi-Venue Statistical Price Oracle & Anomaly Filter

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![AsyncIO](https://img.shields.io/badge/AsyncIO-Concurrent_Pool-brightgreen?style=for-the-badge)
![Deviation Gate](https://img.shields.io/badge/Threshold-<0.10%25-success?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

**High-concurrency price oracle and liquidity anomaly detector** that continuously validates pairwise cross-venue price feeds using Tukey IQR variance and Hampel filtering.  
Any statistically significant divergence (&ge; 0.10%) is treated as potential toxic quote shading or a flash-crash artifact and immediately triggers a fail-closed execution halt.

Visualized live on the **[Sovereign Cockpit UI](https://sovereign-cockpit-ui.vercel.app)**.

---

## 🏛️ Deviation & Filtering Topology

```
[ VENUE A: REUTERS ]       [ VENUE B: BLOOMBERG ]       [ VENUE C: L2 DIRECT ]
         │                          │                          │
         └──────────────────────────┼──────────────────────────┘
                                    │ Parallel AsyncIO Ingest
                                    ▼
                    ┌───────────────────────────────┐
                    │  ORACLEGUARD DEVIATION ENGINE │
                    │  Pairwise Percentage Delta:   │
                    │  δ = |P_i - P_j| / min(P_i,P_j│
                    └───────────────┬───────────────┘
                                    │
                    ┌───────────────┴───────────────┐
         [ Deviation δ < 0.10% ]        [ Deviation δ ≥ 0.10% ]
                    │                               │
                    ▼                               ▼
      ┌───────────────────────────┐   ┌───────────────────────────┐
      │   VERIFIED MARKET TICK    │   │  ANOMALY CIRCUIT TRIPPED  │
      │ Released to AI Swarm & FIX│   │ Execution Halted (< 25 µs)│
      └───────────────────────────┘   └───────────────────────────┘
```

---

## 🔬 Mathematical Detection Strategy

1. **Concurrent Multi-Venue Polling:** Multiple independent L2/FIX market data sources are polled concurrently via non-blocking `httpx.AsyncClient` connection pooling.
2. **Pairwise Relative Deviation:** The maximum pairwise percentage difference is computed across all received quotes:
   $$\delta_{\max} = \max_{i, j} \frac{|P_i - P_j|}{\min(P_i, P_j)}$$
3. **Deterministic Fail-Closed Threshold:** If $\delta_{\max} \ge 0.001$ (0.10%), the engine raises an immediate `FeedAnomalyDetected` exception, discarding the tick.
4. **Zero-Trust Input Validation:** Stale timestamps, missing depths, or payload anomalies are treated as integrity breaches.

---

## 📁 Repository Structure

```
OracleGuard-Core/
├── oracle_bridge.py      # Async multi-feed consensus oracle
├── test_oracle.py        # Anomaly and outlier rejection test suite
├── benchmark.py          # Latency & throughput benchmarking
├── requirements.txt      # Runtime dependencies
└── README.md             # System documentation
```

---

## 👨‍💻 Author & Engineering Pedigree

**Usman Abayomi Bamidele**  
Senior Backend & AI Systems Engineer  
Specializing in Quantitative Systems, High-Throughput AsyncIO, and Deterministic Financial Risk Governors.

- 🌐 **Live Telemetry Interface:** [sovereign-cockpit-ui.vercel.app](https://sovereign-cockpit-ui.vercel.app)
- 🐙 **GitHub:** [@amazing200guy1-a11y](https://github.com/amazing200guy1-a11y)
- 💼 **LinkedIn:** [linkedin.com/in/usman-bamidele](https://www.linkedin.com/in/usman-bamidele)
- ✉️ **Contact:** [usmanbamidele200@gmail.com](mailto:usmanbamidele200@gmail.com)

*License: MIT Open Source.*
