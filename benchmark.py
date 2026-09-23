"""
Benchmark: concurrent vs sequential feed fetch latency.
Run with: python benchmark.py
"""
import asyncio
import time
from unittest.mock import AsyncMock, patch
from oracle_bridge import OracleBridge, FeedPrice


async def run_concurrent(n: int) -> float:
    oracle = OracleBridge()
    price = FeedPrice(price=1.0850, source="bench")
    with patch.object(oracle, "_fetch_feed", new=AsyncMock(return_value=price)):
        t0 = time.perf_counter()
        for _ in range(n):
            await oracle.evaluate()
        return (time.perf_counter() - t0) * 1000


if __name__ == "__main__":
    for n in (10, 50, 100):
        ms = asyncio.run(run_concurrent(n))
        print(f"{n:4d} evaluations | {ms:8.2f} ms total | {ms/n:.2f} ms/call")