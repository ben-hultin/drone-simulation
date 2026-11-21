"""Integration tests for offboard hover mission."""

import asyncio
from pathlib import Path

from dao.flight_log.ulg_metrics_dao import UlgMetricsDao
from dao.mission_log.rosbag_log_dao import RosbagLogDao
from dao.scenario.hover_scenario_dao import HoverScenarioDao
from missions.offboard_hover import OffboardHoverMission
from missions.offboard_hover_types import OffboardHoverStatus
from services.fake_gateway import FakeGateway
from services.fake_offboard_publisher import FakeOffboardPublisher
from services.fake_perception_source import FakeDepthSource, FakePoseSource
from services.fake_ulg_parser import FakeUlgReader
from services.mavsdk_offboard_publisher import MavsdkOffboardPublisher
from services.mavsdk_service import MavsdkService


def _scenario():
    root = Path(__file__).resolve().parents[1]
    return HoverScenarioDao().load(root / "scenarios" / "hover_5m_depth.yaml")


def test_offboard_hover_success(tmp_path: Path) -> None:
    ulg = tmp_path / "session.ulg"
    ulg.write_bytes(b"PX4ULog")
    gateway = FakeGateway(connects=True, ulg_path=ulg)
    mission = OffboardHoverMission(
        MavsdkService(gateway),
        _scenario(),
        FakePoseSource(),
        FakeDepthSource(),
        MavsdkOffboardPublisher(gateway),
        ulg_dao=UlgMetricsDao(log_dir=tmp_path),
        ulg_reader=FakeUlgReader(),
        rosbag_dao=RosbagLogDao(log_dir=tmp_path / "bags"),
    )
    result = asyncio.run(mission.run(connect_timeout_s=1.0))
    assert result.status == OffboardHoverStatus.SUCCESS
    assert result.point_count > 0
    assert result.hover_setpoints_published >= 1
    assert result.rosbag_recorded is True


def test_offboard_hover_fails_without_pose(tmp_path: Path) -> None:
    gateway = FakeGateway(connects=True)
    mission = OffboardHoverMission(
        MavsdkService(gateway),
        _scenario(),
        FakePoseSource(return_none=True),
        FakeDepthSource(),
        FakeOffboardPublisher(),
        rosbag_dao=RosbagLogDao(log_dir=tmp_path / "bags"),
    )
    result = asyncio.run(mission.run(connect_timeout_s=1.0))
    assert result.status == OffboardHoverStatus.POSE_TIMEOUT
    assert gateway.arm_called is False


def test_offboard_hover_fails_without_depth(tmp_path: Path) -> None:
    gateway = FakeGateway(connects=True)
    mission = OffboardHoverMission(
        MavsdkService(gateway),
        _scenario(),
        FakePoseSource(),
        FakeDepthSource(return_none=True),
        FakeOffboardPublisher(),
        rosbag_dao=RosbagLogDao(log_dir=tmp_path / "bags"),
    )
    result = asyncio.run(mission.run(connect_timeout_s=1.0))
    assert result.status == OffboardHoverStatus.DEPTH_TIMEOUT


def test_offboard_hover_offboard_enable_failure(tmp_path: Path) -> None:
    gateway = FakeGateway(connects=True)
    mission = OffboardHoverMission(
        MavsdkService(gateway),
        _scenario(),
        FakePoseSource(),
        FakeDepthSource(),
        FakeOffboardPublisher(fail_enable=True),
        rosbag_dao=RosbagLogDao(log_dir=tmp_path / "bags"),
    )
    result = asyncio.run(mission.run(connect_timeout_s=1.0))
    assert result.status == OffboardHoverStatus.OFFBOARD_FAILED