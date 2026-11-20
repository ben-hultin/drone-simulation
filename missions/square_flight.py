"""Phase 1 square waypoint mission via MAVSDK service."""

import asyncio
import time
from pathlib import Path

from dao.flight_log.ulg_metrics_dao import UlgMetricsDao
from dao.flight_log.ulg_reader_protocol import UlgReader
from dao.scenario.scenario_types import FlightScenario
from missions.square_flight_run_util import run_preflight, run_takeoff, run_waypoint_loop
from missions.square_flight_types import SquareFlightResult, SquareFlightStatus
from services.mavsdk_service import MavsdkService

DEFAULT_CONNECT_TIMEOUT_S = 10.0


class SquareFlightMission:
    """Connect, arm, takeoff, fly square, land, disarm with explicit timeouts."""

    def __init__(
        self,
        mavsdk_service: MavsdkService,
        scenario: FlightScenario,
        *,
        ulg_dao: UlgMetricsDao | None = None,
        ulg_reader: UlgReader | None = None,
        connect_timeout_s: float = DEFAULT_CONNECT_TIMEOUT_S,
    ) -> None:
        self._mavsdk = mavsdk_service
        self._scenario = scenario
        self._ulg_dao = ulg_dao or UlgMetricsDao()
        self._ulg_reader = ulg_reader
        self._connect_timeout_s = connect_timeout_s

    async def run(self, connect_timeout_s: float | None = None) -> SquareFlightResult:
        deadline = time.monotonic() + self._scenario.time_limit_s
        timeout = connect_timeout_s if connect_timeout_s is not None else self._connect_timeout_s
        inflight = False
        reached = 0
        try:
            pre = await run_preflight(
                self._mavsdk,
                self._scenario,
                connect_timeout_s=timeout,
                deadline=deadline,
            )
            if pre is not None:
                return pre
            inflight = True
            takeoff = await run_takeoff(self._mavsdk, self._scenario)
            if takeoff is not None:
                return takeoff
            reached, loop_fail = await run_waypoint_loop(self._mavsdk, self._scenario, deadline)
            if loop_fail is not None:
                return loop_fail
            success = await self._finish_success(reached)
            if success.status == SquareFlightStatus.SUCCESS:
                inflight = False
            return success
        finally:
            if inflight:
                await self._mavsdk.abort_inflight_failsafe()

    async def _finish_success(self, reached: int) -> SquareFlightResult:
        if not await self._mavsdk.land_or_fail():
            return _result(SquareFlightStatus.LAND_FAILED, "land_failed", reached)
        if not await self._mavsdk.wait_landed_or_fail():
            return _result(SquareFlightStatus.LAND_FAILED, "land_confirm_timeout", reached)
        if self._scenario.pass_criteria.require_disarmed:
            if not await self._mavsdk.disarm_or_fail():
                return _result(SquareFlightStatus.DISARM_FAILED, "disarm_failed", reached)
        no_fs = self._scenario.pass_criteria.require_no_failsafe
        if no_fs and await self._mavsdk.read_failsafe():
            return _result(SquareFlightStatus.FAILSAFE, "failsafe_at_end", reached)
        ulg_saved, metrics_recorded = await self._persist_ulg()
        return SquareFlightResult(
            status=SquareFlightStatus.SUCCESS,
            reason="completed",
            waypoints_reached=reached,
            ulg_saved=ulg_saved,
            metrics_recorded=metrics_recorded,
        )

    async def _persist_ulg(self) -> tuple[bool, bool]:
        if self._ulg_reader is None:
            return False, False
        raw = await self._mavsdk.copy_ulg_path()
        if raw is None:
            return False, False
        path = Path(raw)
        if not path.is_file():
            return False, False
        await asyncio.to_thread(self._ulg_dao.save_run, raw, self._ulg_reader)
        return True, True


def _result(status: SquareFlightStatus, reason: str, reached: int) -> SquareFlightResult:
    return SquareFlightResult(
        status=status,
        reason=reason,
        waypoints_reached=reached,
        ulg_saved=False,
        metrics_recorded=False,
    )