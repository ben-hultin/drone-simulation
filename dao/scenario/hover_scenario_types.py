"""Types for Phase 2 hover + depth scenarios."""

from dataclasses import dataclass


@dataclass(frozen=True)
class HoverSpawn:
    north_m: float
    east_m: float
    alt_m: float


@dataclass(frozen=True)
class HoverConfig:
    altitude_m: float
    duration_s: float
    position_tolerance_m: float


@dataclass(frozen=True)
class PerceptionLimits:
    max_pose_age_s: float
    max_depth_age_s: float


@dataclass(frozen=True)
class HoverPassCriteria:
    require_disarmed: bool
    require_no_failsafe: bool
    require_pose: bool
    require_depth_frame: bool


@dataclass(frozen=True)
class HoverScenario:
    name: str
    world: str
    model: str
    spawn: HoverSpawn
    hover: HoverConfig
    time_limit_s: float
    pass_criteria: HoverPassCriteria
    perception: PerceptionLimits