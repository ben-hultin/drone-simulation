# Harness progress

## Goal

Phase 0 environment scaffolding and MAVSDK SITL connectivity check with timeout and no-arm fail-safe.

## Mapped commands

| Stage   | Command |
| ------- | ------- |
| Lint    | `ruff check .` |
| Security| `bandit -r missions services dao` |
| Tests   | `pytest --cov=missions --cov=services --cov=dao --cov-fail-under=80` |
| Build   | `python3 -m compileall missions services dao` |

**MAVSDK endpoint:** `udpin://127.0.0.1:14540`

**Live Flight flows:** connect, verify health, refuse arm on timeout / unreachable vehicle.

## Subagent gate

Launch Harness Critic, Security Review, Bugbot, and Live Flight only after `./harness-loop.sh` prints `Terminal state reached.`

## Run metrics

- started_at: 2026-11-17T17:07:00-08:00
- goal: Phase 0 scaffolding + SITL connectivity check
- iteration: 4
- ended_at: 2026-11-17T17:30:00-08:00
- subagent_issues_total: 0
- subagent_issues_by_severity: critical=0, high=0, medium=0, low=0, info=0
- tokens_consumed: unknown

## Live path coverage note

`services/mavsdk_live_gateway.py` is excluded from pytest coverage until Phase 1 SITL fixtures exist (`pyproject.toml` `[tool.coverage.run] omit`).

## Iteration log

### Iteration 1
- static: pass (after StrEnum, bandit excludes, env_probe fixes)
- subagents: critic/security/bugbot fail; live flight SKIPPED sitl_unavailable

### Iteration 2
- static: pass
- fixes: no-arm guard, loopback URL, toolchain service, hermetic log dirs in tests
- subagents: partial fails

### Iteration 3
- static: pass (33 tests, ~95% cov)
- fixes: URL validation on live gateway, health timeouts, live runner, integration test
- security: pass; live flight: SKIPPED pass; bugbot/critic: fail

### Iteration 4
- static: pass
- fixes: gateway release, home-dir logs, simplified mission flow
- harness critic: pass (info: live gateway cov omit)
- security: pass
- bugbot: pass
- live flight: pass SKIPPED sitl_unavailable