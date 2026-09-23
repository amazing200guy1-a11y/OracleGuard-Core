"""Shared pytest fixtures for OracleGuard-Core test suite."""
import pytest
from unittest.mock import AsyncMock, patch
from oracle_bridge import OracleBridge, FeedPrice


@pytest.fixture()
def oracle() -> OracleBridge:
    """Return a fresh OracleBridge instance for each test."""
    return OracleBridge()


def make_feed(price: float, source: str = "mock") -> FeedPrice:
    return FeedPrice(price=price, source=source)