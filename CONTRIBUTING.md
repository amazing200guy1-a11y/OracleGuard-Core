# Contributing to OracleGuard-Core

## Setup
```bash
git clone https://github.com/amazing200guy1-a11y/OracleGuard-Core
cd OracleGuard-Core
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -v
```

## Architecture
- `oracle_bridge.py` — validates broker prices against independent feed
- Anomaly detection uses a sliding 60-second VWAP window
- Outputs structured alerts to stdout (JSON lines format)

## Detection Thresholds
| Signal | Threshold | Action |
|---|---|---|
| Spread deviation | > 3.5x ATR | ALERT |
| Price lag | > 150ms | WARN |
| B-Book fingerprint | Pattern match | BLOCK |
