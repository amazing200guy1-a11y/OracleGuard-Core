# Changelog

## [1.1.0] — 2026-09-23
### Added
- Shared `conftest.py` with reusable fixtures.
- `pytest.ini` with `asyncio_mode = auto`.
- Fixed markdown code-fence syntax error in `oracle_bridge.py`.
- MIT license applied.

## [1.0.0] — 2026-09-20
### Added
- Multi-source concurrent price oracle using `asyncio.gather`.
- Pairwise relative deviation detection with configurable 0.10% threshold.
- `ManipulationDetected` and `FeedError` typed exceptions.
- Fail-closed design: timeouts treated as integrity failures.