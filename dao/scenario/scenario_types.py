"""Types for YAML flight scenarios."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ScenarioSpawn:
    north_m: float
    east_m: float
    alt_m: float


@dataclass(frozen=True)
class ScenarioGoal:
    pattern: str
    side_m: float
    altitude_m: float


@dataclass(frozen=True)
class ScenarioPassCriteria:
    waypoint_tolerance_m: float
    require_disarmed: bool
    require_no_failsafe: bool


@dataclass(frozen=True)
class FlightScenario:
    name: str
    world: str
    spawn: ScenarioSpawn
    goal: ScenarioGoal
    time_limit_s: float
    pass_criteria: ScenarioPassCriteria