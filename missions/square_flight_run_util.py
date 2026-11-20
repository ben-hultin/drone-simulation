"""Orchestration helpers to keep SquareFlightMission.run under size limits."""

import time

from dao.scenario.scenario_types import FlightScenario
from missions.square_flight_types import SquareFlightResult, SquareFlightStatus
from missions.square_flight_util import waypoints_for_scenario
from services.mavsdk_service import MavsdkService


async def run_preflight(
    mavsdk: MavsdkService,
    scenario: FlightScenario,
    *,
    connect_timeout_s: float,
    deadline: float,
) -> SquareFlightResult | None:
    if not await mavsdk.connect_or_fail(timeout_s=connect_timeout_s):
        return _fail(SquareFlightStatus.CONNECT_FAILED, "connection_timeout", 0)
    if not await mavsdk.verify_health_or_fail():
        return _fail(SquareFlightStatus.ARM_FAILED, "unhealthy", 0)
    if time.monotonic() > deadline:
        return _fail(SquareFlightStatus.TIMEOUT, "scenario_time_limit", 0)
    if not await mavsdk.arm_or_fail():
        return _fail(SquareFlightStatus.ARM_FAILED, "arm_command_failed", 0)
    return None


async def run_takeoff(
    mavsdk: MavsdkService,
    scenario: FlightScenario,
) -> SquareFlightResult | None:
    spawn = scenario.spawn
    target_alt = scenario.goal.altitude_m + spawn.alt_m
    tol = scenario.pass_criteria.waypoint_tolerance_m
    if not await mavsdk.takeoff_or_fail(target_alt, tolerance_m=tol):
        return _fail(SquareFlightStatus.TAKEOFF_FAILED, "takeoff_failed", 0)
    if spawn.north_m != 0.0 or spawn.east_m != 0.0:
        if not await mavsdk.goto_or_fail(
            spawn.north_m,
            spawn.east_m,
            target_alt,
            tolerance_m=tol,
            timeout_s=30.0,
        ):
            return _fail(SquareFlightStatus.TAKEOFF_FAILED, "spawn_hold_failed", 0)
    return None


async def run_waypoint_loop(
    mavsdk: MavsdkService,
    scenario: FlightScenario,
    deadline: float,
) -> tuple[int, SquareFlightResult | None]:
    tolerance = scenario.pass_criteria.waypoint_tolerance_m
    reached = 0
    for north, east, alt_m in waypoints_for_scenario(scenario):
        if time.monotonic() > deadline:
            return reached, _fail(SquareFlightStatus.TIMEOUT, "scenario_time_limit", reached)
        leg_timeout = min(60.0, max(0.1, deadline - time.monotonic()))
        ok = await mavsdk.goto_or_fail(
            north,
            east,
            alt_m,
            tolerance_m=tolerance,
            timeout_s=leg_timeout,
        )
        if not ok:
            return reached, _fail(SquareFlightStatus.WAYPOINT_FAILED, "waypoint_timeout", reached)
        if await mavsdk.read_failsafe():
            return reached, _fail(SquareFlightStatus.FAILSAFE, "failsafe_during_mission", reached)
        reached += 1
    return reached, None


def _fail(status: SquareFlightStatus, reason: str, reached: int) -> SquareFlightResult:
    return SquareFlightResult(
        status=status,
        reason=reason,
        waypoints_reached=reached,
        ulg_saved=False,
        metrics_recorded=False,
    )