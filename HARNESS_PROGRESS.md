# Harness progress

## Goal

Phase 2 offboard hover: read pose and depth, depth→point cloud, offboard takeoff/hover/land, rosbag metadata alongside ULog; default SITL `gz_x500_depth`.

## Mapped commands

| Stage   | Command |
| ------- | ------- |
| Lint    | `ruff check .` |
| Security| `bandit -r missions services dao -q -c pyproject.toml` |
| Tests   | `pytest --cov=missions --cov=services --cov=dao --cov-fail-under=80` |
| Build   | `python3 -m compileall missions services dao -q` |

**MAVSDK endpoint:** `udpin://127.0.0.1:14540`

## Run metrics

| Metric | Value |
| ------ | ----- |
| Duration | 2026-11-20T06:58:00-08:00 → 2026-11-20T07:15:00-08:00 (~17 min) |
| Tokens consumed | unknown |
| Loop iterations | 5 |
| Subagent issues found | 0 blocking after iteration 5 (critic low=2, info=1) |

## Iteration 5 (terminal)

- static: pass (69 tests, 85% cov)
- Harness Critic: VERDICT pass
- Security Review: VERDICT pass (from iteration 3 review; no Medium+)
- Bugbot: VERDICT pass
- Live Flight: VERDICT pass, SKIPPED sitl_unavailable