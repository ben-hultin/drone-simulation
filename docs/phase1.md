# Phase 1

Exit criteria from the phased plan:

1. `pytest` runs the square mission against `FakeGateway` and asserts waypoint success, disarm, and optional ULog metrics.
2. Opt-in live run: set `PX4_AUTOPILOT_DIR`, start SITL, then `python missions/square_flight_runner.py`.
3. Scenario file: `scenarios/square_5m.yaml` (world field reserved for Phase 4 launcher wiring).

SITL pytest fixture: `missions/conftest.py` — tests request `sitl_stack` only when `RUN_LIVE_SITL=1`.