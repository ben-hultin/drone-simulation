"""End-to-end wiring: mission + service + DAO with gateway faked at protocol only."""

import asyncio
from pathlib import Path

from dao.mission_log.connectivity_log_dao import ConnectivityLogDao
from missions.sitl_connectivity import SitlConnectivityCheck
from missions.sitl_connectivity_types import SitlConnectivityStatus
from services.fake_gateway import FakeGateway
from services.mavsdk_service import MavsdkService


def test_full_connectivity_stack(tmp_path: Path) -> None:
    gateway = FakeGateway(connects=True)
    service = MavsdkService(gateway)
    dao = ConnectivityLogDao(log_dir=tmp_path)
    mission = SitlConnectivityCheck(service, log_dao=dao)

    result = asyncio.run(mission.run(connect_timeout_s=1.0))

    assert result.status == SitlConnectivityStatus.READY
    assert result.logged is True
    assert gateway.arm_called is False
    assert list(tmp_path.glob("*.json"))