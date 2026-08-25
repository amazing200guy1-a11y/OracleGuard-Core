---

### 2. `oracle_bridge.py`

```python
"""
OracleGuard-Core — Multi-Source Price Oracle (Python 3.12)

Fetches three independent price feeds concurrently, computes pairwise
relative deviation, and fails closed when any feed diverges beyond the
configured threshold (default 0.10 %).
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import httpx

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger("oracleguard")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_DEVIATION_THRESHOLD: float = 0.001   # 0.10 %
REQUEST_TIMEOUT: float = 2.5

# Mock feed endpoints (replace with real Reuters / Bloomberg / Coinbase URLs)
FEED_ENDPOINTS: Dict[str, str] = {
    "reuters":   "https://httpbin.org/json",   # placeholder
    "bloomberg": "https://httpbin.org/json",
    "coinbase":  "https://httpbin.org/json",
}


# ---------------------------------------------------------------------------
# Domain types
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class FeedPrice:
    source: str
    mid: float


@dataclass(frozen=True, slots=True)
class OracleResult:
    prices: Dict[str, float]
    max_deviation: float
    reference_mid: float
    is_valid: bool


class ManipulationDetected(Exception):
    """Raised when cross-feed deviation exceeds the hard threshold."""

    def __init__(self, max_deviation: float, prices: Dict[str, float]) -> None:
        self.max_deviation = max_deviation
        self.prices = prices
        super().__init__(
            f"Manipulation / flash-crash detected: max deviation "
            f"{max_deviation:.4%} ≥ threshold. Prices={prices}"
        )


class FeedError(Exception):
    """Raised on network, timeout or parse failures."""


# ---------------------------------------------------------------------------
# Core engine
# ---------------------------------------------------------------------------

class OracleBridge:
    """
    High-concurrency multi-source price oracle.

    - Uses one shared httpx.AsyncClient for connection reuse.
    - Fans out all feed requests with asyncio.gather.
    - Computes maximum pairwise relative deviation.
    - Raises ManipulationDetected when the threshold is breached.
    """

    def __init__(
        self,
        endpoints: Optional[Dict[str, str]] = None,
        deviation_threshold: float = DEFAULT_DEVIATION_THRESHOLD,
        timeout: float = REQUEST_TIMEOUT,
    ) -> None:
        self.endpoints = endpoints or FEED_ENDPOINTS
        self.threshold = deviation_threshold
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "OracleBridge":
        self._client = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, *exc: object) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _fetch_one(self, name: str, url: str) -> FeedPrice:
        """Fetch a single feed. In production this parses real JSON schemas."""
        assert self._client is not None
        try:
            resp = await self._client.get(url)
            resp.raise_for_status()
            # Mock extraction — real feeds would pull bid/ask or last price
            data = resp.json()
            # Simulate a realistic mid from whatever payload we receive
            # (httpbin returns a slideshow object; we synthesise a stable number)
            base = 1.0850
            # Deterministic tiny offset per source so clean runs stay under threshold
            offset = {"reuters": 0.0, "bloomberg": 0.00002, "coinbase": -0.00001}.get(name, 0.0)
            mid = base + offset
            return FeedPrice(source=name, mid=mid)
        except (httpx.HTTPError, ValueError, KeyError) as exc:
            raise FeedError(f"Feed '{name}' failed: {exc}") from exp

    @staticmethod
    def _max_pairwise_deviation(prices: Sequence[float]) -> float:
        """Return the largest relative difference between any pair."""
        if len(prices) < 2:
            return 0.0
        max_dev = 0.0
        for i, a in enumerate(prices):
            for b in prices[i + 1 :]:
                if a == 0.0 and b == 0.0:
                    continue
                ref = max(abs(a), abs(b))
                dev = abs(a - b) / ref
                if dev > max_dev:
                    max_dev = dev
        return max_dev

    async def evaluate(self) -> OracleResult:
        """
        Concurrently fetch all feeds, compute deviation, and validate.

        Raises
        ------
        FeedError
            On network / parse failure of any feed.
        ManipulationDetected
            When max pairwise deviation ≥ threshold.
        """
        assert self._client is not None

        tasks = [
            self._fetch_one(name, url)
            for name, url in self.endpoints.items()
        ]
        results: List[FeedPrice] = await asyncio.gather(*tasks)

        price_map = {r.source: r.mid for r in results}
        mids = list(price_map.values())
        max_dev = self._max_pairwise_deviation(mids)
        reference = sum(mids) / len(mids)

        logger.info(
            "oracle tick | prices=%s | max_dev=%.4f | threshold=%.4f",
            price_map,
            max_dev,
            self.threshold,
        )

        if max_dev >= self.threshold:
            raise ManipulationDetected(max_dev, price_map)

        return OracleResult(
            prices=price_map,
            max_deviation=max_dev,
            reference_mid=reference,
            is_valid=True,
        )


# ---------------------------------------------------------------------------
# Demo entry-point
# ---------------------------------------------------------------------------

async def main() -> None:
    async with OracleBridge() as oracle:
        try:
            result = await oracle.evaluate()
            print("VALIDATED:", result)
        except ManipulationDetected as exc:
            print("HALT:", exc)
        except FeedError as exc:
            print("FEED FAILURE:", exc)


if __name__ == "__main__":
    asyncio.run(main())
