# Phase 0

Exit criteria from the phased plan:

1. `make px4_sitl gz_x500` flies on the Mac and QGroundControl connects (run from your PX4-Autopilot clone; not in this repo).
2. This repo provides a MAVSDK connectivity mission with explicit connect timeout and **arm guard** (no arm command on the check path).
3. `probe_toolchain()` in `missions/env_probe.py` delegates to `services/toolchain_service.py`.

MAVSDK default endpoint: `udpin://127.0.0.1:14540` (loopback; use `allow_wildcard_bind` only when explicitly required).

**Python:** install `mavsdk-grpc` (gRPC MAVSDK-Python API). Do not use native `mavsdk>=4` — it breaks `System()` used in `services/mavsdk_live_gateway.py`. Legacy pin: `mavsdk>=2.0.0,<4` only if you cannot install `mavsdk-grpc`.