# Harness progress

## Goal

Phase 1 scripted square flight: connect, arm, takeoff 5 m, square waypoints, land, disarm; YAML scenario; ULog metrics; SITL fixture when toolchain available.

## Mapped commands

| Stage   | Command |
| ------- | ------- |
| Lint    | `ruff check .` |
| Security| `bandit -r missions services dao` |
| Tests   | `pytest --cov=missions --cov=services --cov=dao --cov-fail-under=80` |
| Build   | `python3 -m compileall missions services dao` |

**MAVSDK endpoint:** `udpin://127.0.0.1:14540`

**Live Flight flows:** connect, arm, takeoff 5 m, square waypoints, land, disarm, fail-safe on timeout.

## Subagent gate

Launch Harness Critic, Security Review, Bugbot, and Live Flight only after `./harness-loop.sh` prints `Terminal state reached.`

## Run metrics

- started_at: 2026-11-19T11:05:00-08:00
- ended_at: 2026-11-19T11:35:00-08:00
- goal: Phase 1 scripted square flight + YAML scenario + ULog
- iteration: 3
- subagent_issues_total: 0
- subagent_issues_by_severity: critical=0, high=0, medium=0, low=0, info=0
- tokens_consumed: unknown

## Iteration log

### Iteration 1
- static: pass (51 tests)
- subagents: critic fail; security pass; bugbot fail; live SKIPPED sitl_unavailable

### Iteration 2
- static: pass (53 tests)
- fixes: offboard API, mission refactor, spawn offset, ulg path, abort finally
- subagents: critic fail (2 medium); security pass; bugbot fail (2 medium); live SKIPPED

### Iteration 3
- static: pass (52 passed, 1 skipped)
- fixes: stop offboard before RTL; inflight cleared only on SUCCESS
- subagents: critic pass; security pass; bugbot pass; live flight SKIPPED sitl_unavailable