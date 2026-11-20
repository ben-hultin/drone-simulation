"""Integration tests for square flight mission."""

import asyncio
from pathlib import Path

from dao.flight_log.ulg_metrics_dao import UlgMetricsDao
from dao.scenario.scenario_dao import ScenarioDao
from missions.square_flight import SquareFlightMission
from missions.square_flight_types import SquareFlightStatus
from services.fake_gateway import FakeGateway
from services.fake_ulg_parser import FakeUlgReader
from services.mavsdk_service import MavsdkService


def _scenario():
    root = Path(__file__).resolve().parents[1]
    return ScenarioDao().load(root / "scenarios" / "square_5m.yaml")


def test_square_flight_success_with_fake_gateway(tmp_path: Path) -> None:
    ulg = tmp_path / "session.ulg"
    ulg.write_bytes(b"PX4ULog")
    gateway = FakeGateway(connects=True, ulg_path=ulg)
    service = MavsdkService(gateway)
    reader = FakeUlgReader()
    mission = SquareFlightMission(
        service,
        _scenario(),
        ulg_dao=UlgMetricsDao(log_dir=tmp_path),
        ulg_reader=reader,
    )
    result = asyncio.run(mission.run(connect_timeout_s=1.0))
    assert result.status == SquareFlightStatus.SUCCESS
    assert result.waypoints_reached == 4
    assert result.ulg_saved is True
    assert result.metrics_recorded is True
    assert gateway.arm_called is True
    assert gateway.land_called is True
    assert gateway.disarm_called is True
    assert len(gateway.goto_calls) == 4


def test_square_flight_fails_on_failsafe(tmp_path: Path) -> None:
    gateway = FakeGateway(connects=True, failsafe=True)
    service = MavsdkService(gateway)
    mission = SquareFlightMission(service, _scenario(), ulg_dao=UlgMetricsDao(log_dir=tmp_path))
    result = asyncio.run(mission.run(connect_timeout_s=1.0))
    assert result.status == SquareFlightStatus.FAILSAFE