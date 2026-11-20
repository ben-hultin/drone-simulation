"""Failure-path integration tests for square flight."""

import asyncio
from pathlib import Path
from unittest.mock import patch

from dao.scenario.scenario_dao import ScenarioDao
from missions.square_flight import SquareFlightMission
from missions.square_flight_types import SquareFlightStatus
from services.fake_gateway import FakeGateway
from services.mavsdk_service import MavsdkService


def _scenario():
    root = Path(__file__).resolve().parents[1]
    return ScenarioDao().load(root / "scenarios" / "square_5m.yaml")


def test_connect_failure() -> None:
    mission = SquareFlightMission(
        MavsdkService(FakeGateway(connects=False)),
        _scenario(),
    )
    result = asyncio.run(mission.run(connect_timeout_s=0.1))
    assert result.status == SquareFlightStatus.CONNECT_FAILED


class NoArmGateway(FakeGateway):
    async def arm(self) -> None:
        raise TimeoutError("arm_rejected")


def test_scenario_timeout_aborts_inflight() -> None:
    gateway = FakeGateway()
    mission = SquareFlightMission(MavsdkService(gateway), _scenario())
    tick = [0.0, 0.0, 0.0, 999.0]

    def fake_monotonic() -> float:
        if tick:
            return tick.pop(0)
        return 999.0

    with patch("missions.square_flight.time.monotonic", side_effect=fake_monotonic):
        result = asyncio.run(mission.run())
    assert result.status == SquareFlightStatus.TIMEOUT


def test_abort_inflight_after_partial_mission() -> None:
    gateway = FakeGateway()
    service = MavsdkService(gateway)

    async def run_and_abort() -> None:
        await service.connect_or_fail()
        await service.arm_or_fail()
        await service.takeoff_or_fail(5.0, tolerance_m=1.0)
        await service.abort_inflight_failsafe()

    asyncio.run(run_and_abort())
    assert gateway.land_called or gateway.rtl_called