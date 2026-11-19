# drone-simulation

PX4 SITL, Gazebo Harmonic, ROS 2 Jazzy, MAVSDK-Python, and pytest.

## Layout (Phase 0)

- `missions/` — mission orchestration (no direct `mavsdk` imports)
- `services/` — MAVSDK and toolchain clients
- `dao/` — mission logs and persistence
- `worlds/`, `models/`, `ros2_ws/`, `docs/` — scenario assets and future ROS workspace

Phase 0 uses top-level Python packages; ROS 2 autonomy nodes land in `ros2_ws/` in Phase 2.

## Verify

```bash
./harness-loop.sh
pytest
```

Default MAVSDK endpoint: `udpin://127.0.0.1:14540`. Live flight uses **`mavsdk-grpc`** (`pip install -r requirements-dev.txt`).