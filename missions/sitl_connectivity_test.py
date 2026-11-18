"""Integration tests for SITL connectivity mission."""

import asyncio
from pathlib import Path

import pytest

from dao.mission_log.connectivity_log_dao import ConnectivityLogDao
from missions.sitl_connectivity import SitlConnectivityCheck
from missions.sitl_connectivity_types import SitlConnectivityStatus
from services.fake_gateway import FakeGateway
from services.mavsdk_protocol import VehicleHealth
from services.mavsdk_service import MavsdkService


@pytest.fixture
def log_dir(tmp_path: Path) -> Path:
    return tmp_path / "runs"


def test_mission_fails_when_not_connected(log_dir: Path) -> None:
    gateway = FakeGateway(connects=False)
    mission = SitlConnectivityCheck(
        MavsdkService(gateway),
        log_dao=ConnectivityLogDao(log_dir=log_dir),
    )
    result = asyncio.run(mission.run(connect_timeout_s=0.1))
    assert result.status == SitlConnectivityStatus.UNREACHABLE
    assert result.logged is True


def test_mission_refuses_arm_when_unhealthy(log_dir: Path) -> None:
    bad = VehicleHealth(
        is_armable=False,
        is_global_position_ok=True,
        is_home_position_ok=True,
        is_local_position_ok=True,
    )
    gateway = FakeGateway(health=bad)
    mission = SitlConnectivityCheck(
        MavsdkService(gateway),
        log_dao=ConnectivityLogDao(log_dir=log_dir),
    )
    result = asyncio.run(mission.run(connect_timeout_s=1.0))
    assert result.status == SitlConnectivityStatus.UNHEALTHY
    assert result.reason == "vehicle_not_armable"
    assert gateway.arm_called is False


def test_mission_ready_when_connected_and_healthy(log_dir: Path) -> None:
    gateway = FakeGateway()
    mission = SitlConnectivityCheck(
        MavsdkService(gateway),
        log_dao=ConnectivityLogDao(log_dir=log_dir),
    )
    result = asyncio.run(mission.run(connect_timeout_s=1.0))
    assert result.status == SitlConnectivityStatus.READY
    assert result.arm_refused is False
    assert result.reason == "arm_eligible"
    assert gateway.arm_called is False