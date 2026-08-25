"""
OracleGuard-Core — Test suite

Simulates a broker price-manipulation attack (artificial candle deviation)
and verifies that the oracle detects it and raises ManipulationDetected,
forcing an immediate system halt.
"""

from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, patch

from oracle_bridge import (
    FeedPrice,
    ManipulationDetected,
    OracleBridge,
    OracleResult,
    FeedError,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_feed(name: str, mid: float) -> FeedPrice:
    return FeedPrice(source=name, mid=mid)


# ---------------------------------------------------------------------------
# Pure logic tests
# ---------------------------------------------------------------------------

def test_max_pairwise_deviation_clean() -> None:
    prices = [1.0850, 1.0851, 1.0849]
    dev = OracleBridge._max_pairwise_deviation(prices)
    assert dev < 0.001


def test_max_pairwise_deviation_attack() -> None:
    # One feed prints a massive artificial candle
    prices = [1.0850, 1.0851, 1.1200]   # \~3.2 % divergence
    dev = OracleBridge._max_pairwise_deviation(prices)
    assert dev > 0.03


# ---------------------------------------------------------------------------
# Async integration tests (mocked network)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_clean_feeds_pass() -> None:
    """All three feeds agree → is_valid=True, no exception."""
    mock_results = [
        make_feed("reuters", 1.08500),
        make_feed("bloomberg", 1.08505),
        make_feed("coinbase", 1.08497),
    ]

    with patch.object(OracleBridge, "_fetch_one", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = mock_results

        async with OracleBridge(deviation_threshold=0.001) as oracle:
            result = await oracle.evaluate()

        assert isinstance(result, OracleResult)
        assert result.is_valid is True
        assert result.max_deviation < 0.001
        assert mock_fetch.await_count == 3


@pytest.mark.asyncio
async def test_manipulation_attack_triggers_halt() -> None:
    """
    Simulate a classic manipulation / flash-crash candle on one feed.
    The oracle must raise ManipulationDetected so the caller can halt.
    """
    mock_results = [
        make_feed("reuters", 1.08500),
        make_feed("bloomberg", 1.08510),
        make_feed("coinbase", 1.15000),   # artificial +6 % spike
    ]

    with patch.object(OracleBridge, "_fetch_one", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = mock_results

        async with OracleBridge(deviation_threshold=0.001) as oracle:
            with pytest.raises(ManipulationDetected) as exc_info:
                await oracle.evaluate()

        err = exc_info.value
        assert err.max_deviation >= 0.001
        assert "coinbase" in err.prices
        assert mock_fetch.await_count == 3


@pytest.mark.asyncio
async def test_single_feed_failure_raises_feed_error() -> None:
    """Network / parse failure on any feed must surface as FeedError."""
    async def boom(name: str, url: str):
        if name == "bloomberg":
            raise FeedError("bloomberg timeout")
        return make_feed(name, 1.0850)

    with patch.object(OracleBridge, "_fetch_one", side_effect=boom):
        async with OracleBridge() as oracle:
            with pytest.raises(FeedError):
                await oracle.evaluate()


@pytest.mark.asyncio
async def test_threshold_boundary() -> None:
    """Deviation just under the threshold must still pass."""
    # 0.09 % divergence
    mock_results = [
        make_feed("reuters", 1.08500),
        make_feed("bloomberg", 1.08500 * 1.0009),
        make_feed("coinbase", 1.08500),
    ]

    with patch.object(OracleBridge, "_fetch_one", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.side_effect = mock_results

        async with OracleBridge(deviation_threshold=0.001) as oracle:
            result = await oracle.evaluate()

        assert result.is_valid is True
        assert result.max_deviation < 0.001
