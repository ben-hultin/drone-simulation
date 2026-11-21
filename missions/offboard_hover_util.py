"""Helpers for perception freshness and hover setpoints."""

import time

from dao.scenario.hover_scenario_types import HoverScenario
from services.offboard_command_protocol import OffboardPublisher, OffboardSetpoint
from services.perception_protocol import DepthFrame, DepthSource, PoseSample, PoseSource


def pose_is_fresh(pose: PoseSample, *, max_age_s: float, now: float | None = None) -> bool:
    clock = now if now is not None else time.monotonic()
    return (clock - pose.stamp_monotonic_s) <= max_age_s


def depth_is_fresh(frame: DepthFrame, *, max_age_s: float, now: float | None = None) -> bool:
    clock = now if now is not None else time.monotonic()
    return (clock - frame.stamp_monotonic_s) <= max_age_s


async def await_fresh_pose(
    source: PoseSource,
    scenario: HoverScenario,
) -> PoseSample | None:
    pose = await source.latest_pose()
    if pose is None:
        return None
    if not pose_is_fresh(pose, max_age_s=scenario.perception.max_pose_age_s):
        return None
    return pose


async def await_fresh_depth(
    source: DepthSource,
    scenario: HoverScenario,
) -> DepthFrame | None:
    frame = await source.latest_depth()
    if frame is None:
        return None
    if not depth_is_fresh(frame, max_age_s=scenario.perception.max_depth_age_s):
        return None
    return frame


async def warm_up_offboard(
    publisher: OffboardPublisher,
    scenario: HoverScenario,
    *,
    iterations: int = 3,
) -> None:
    for _ in range(iterations):
        await publish_hover_hold(publisher, scenario)


async def publish_hover_hold(
    publisher: OffboardPublisher,
    scenario: HoverScenario,
) -> OffboardSetpoint:
    target_alt = scenario.hover.altitude_m + scenario.spawn.alt_m
    sp = OffboardSetpoint(
        north_m=scenario.spawn.north_m,
        east_m=scenario.spawn.east_m,
        alt_m=target_alt,
    )
    await publisher.publish_setpoint(sp)
    return sp