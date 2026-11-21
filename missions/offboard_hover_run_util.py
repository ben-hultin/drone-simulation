"""Orchestration helpers for offboard hover (keeps mission class thin)."""

import asyncio
import time

from dao.scenario.hover_scenario_types import HoverScenario
from missions.offboard_hover_position_util import wait_at_position
from missions.offboard_hover_types import OffboardHoverResult, OffboardHoverStatus
from missions.offboard_hover_util import publish_hover_hold, warm_up_offboard
from services.mavsdk_protocol import VehiclePosition
from services.mavsdk_service import MavsdkService
from services.offboard_command_protocol import OffboardPublisher

_HOVER_MISS_LIMIT = 3


async def run_hover_preflight(
    mavsdk: MavsdkService,
    deadline: float,
    *,
    connect_timeout_s: float,
) -> OffboardHoverResult | None:
    if not await mavsdk.connect_or_fail(connect_timeout_s):
        return _fail(OffboardHoverStatus.CONNECT_FAILED, "connect_timeout")
    if not await mavsdk.verify_health_or_fail():
        return _fail(OffboardHoverStatus.HEALTH_FAILED, "health_check_failed")
    if time.monotonic() > deadline:
        return _fail(OffboardHoverStatus.TIME_LIMIT, "scenario_time_limit")
    return None


async def run_offboard_climb(
    mavsdk: MavsdkService,
    offboard: OffboardPublisher,
    scenario: HoverScenario,
    deadline: float,
) -> OffboardHoverResult | None:
    spawn = scenario.spawn
    target_alt = scenario.hover.altitude_m + spawn.alt_m
    tol = scenario.hover.position_tolerance_m
    target = VehiclePosition(spawn.north_m, spawn.east_m, target_alt)
    await warm_up_offboard(offboard, scenario)
    climb_end = time.monotonic() + max(1.0, deadline - time.monotonic())
    while time.monotonic() < climb_end:
        if time.monotonic() > deadline:
            return _fail(OffboardHoverStatus.TIME_LIMIT, "scenario_time_limit")
        if await mavsdk.read_failsafe():
            return _fail(OffboardHoverStatus.FAILSAFE, "failsafe_during_climb")
        await publish_hover_hold(offboard, scenario)
        if await wait_at_position(mavsdk, target, tolerance_m=tol, timeout_s=1.0):
            return None
        await asyncio.sleep(0.1)
    return _fail(OffboardHoverStatus.TAKEOFF_FAILED, "offboard_climb_timeout")


async def run_hover_loop(
    mavsdk: MavsdkService,
    offboard: OffboardPublisher,
    scenario: HoverScenario,
    deadline: float,
) -> tuple[int, OffboardHoverResult | None]:
    hover_end = time.monotonic() + scenario.hover.duration_s
    published = 0
    spawn = scenario.spawn
    alt = scenario.hover.altitude_m + spawn.alt_m
    target = VehiclePosition(spawn.north_m, spawn.east_m, alt)
    tol = scenario.hover.position_tolerance_m
    miss_streak = 0
    while time.monotonic() < hover_end:
        if time.monotonic() > deadline:
            return published, _fail(OffboardHoverStatus.TIME_LIMIT, "scenario_time_limit")
        if await mavsdk.read_failsafe():
            return published, _fail(OffboardHoverStatus.FAILSAFE, "failsafe_during_hover")
        await publish_hover_hold(offboard, scenario)
        published += 1
        if await wait_at_position(mavsdk, target, tolerance_m=tol, timeout_s=1.0):
            miss_streak = 0
        else:
            miss_streak += 1
            if miss_streak >= _HOVER_MISS_LIMIT:
                return published, _fail(OffboardHoverStatus.HOVER_FAILED, "hover_position_lost")
        await asyncio.sleep(0.05)
    return published, None


def _fail(status: OffboardHoverStatus, reason: str) -> OffboardHoverResult:
    return OffboardHoverResult(status=status, reason=reason)