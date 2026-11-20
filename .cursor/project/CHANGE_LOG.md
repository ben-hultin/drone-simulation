## 2026-11-19 — Phase 1 square flight harness

**Behavior:** Square waypoint mission (arm, 5 m takeoff, 5 m square, land, disarm) with YAML scenario, ULog metrics DAO, SITL launcher fixture, and 52 passing pytest tests; harness loop iteration 3, Live Flight SKIPPED (no SITL).

**Files:** missions/square_flight*.py, scenarios/, dao/scenario/, dao/flight_log/, services/mavsdk_service.py, services/sitl_launcher_service.py, docs/phase1.md

## 2026-11-17 — Phase 0 harness scaffolding

**Behavior:** Added Phase 0 layout, `./harness-loop.sh`, MAVSDK connect timeout + arm guard (no arm on check path), toolchain probe, and live runner stub; harness loop iteration 4, Live Flight SKIPPED (no SITL).

**Files:** `.cursorrules`, `harness-loop.sh`, `pyproject.toml`, `missions/`, `services/`, `dao/`, `docs/phase0.md`, `worlds/`, `models/`, `ros2_ws/`