"""Tests for offboard hover helpers."""

import asyncio
import time
from pathlib import Path

from dao.scenario.hover_scenario_dao import HoverScenarioDao
from dao.scenario.hover_scenario_types import HoverScenario
from missions.offboard_hover_util import (
    await_fresh_depth,
    await_fresh_pose,
    depth_is_fresh,
    pose_is_fresh,
    publish_hover_hold,
)
from services.fake_offboard_publisher import FakeOffboardPublisher
from services.fake_perception_source import FakeDepthSource, FakePoseSource
from services.perception_protocol import DepthFrame, PoseSample


def _scenario() -> HoverScenario:
    root = Path(__file__).resolve().parents[1]
    return HoverScenarioDao().load(root / "scenarios" / "hover_5m_depth.yaml")


def test_pose_freshness() -> None:
    now = time.monotonic()
    pose = PoseSample(0.0, 0.0, 0.0, now)
    assert pose_is_fresh(pose, max_age_s=1.0, now=now + 0.5)
    assert not pose_is_fresh(pose, max_age_s=0.1, now=now + 0.5)


def test_stale_pose_rejected() -> None:
    scenario = _scenario()
    stale = PoseSample(0.0, 0.0, 0.0, time.monotonic() - 5.0)
    source = FakePoseSource(pose=stale)
    assert asyncio.run(await_fresh_pose(source, scenario)) is None


def test_publish_hover_hold() -> None:
    publisher = FakeOffboardPublisher()
    asyncio.run(publisher.enable_offboard())
    sp = asyncio.run(publish_hover_hold(publisher, _scenario()))
    assert sp.alt_m == 5.0
    assert len(publisher.setpoints) == 1


def test_stale_depth_rejected() -> None:
    scenario = _scenario()
    frame = DepthFrame(2, 2, (1.0, 1.0, 1.0, 1.0), time.monotonic() - 10.0)
    source = FakeDepthSource(frame=frame)
    assert asyncio.run(await_fresh_depth(source, scenario)) is None


def test_depth_freshness() -> None:
    now = time.monotonic()
    frame = DepthFrame(1, 1, (1.0,), now)
    assert depth_is_fresh(frame, max_age_s=1.0, now=now)