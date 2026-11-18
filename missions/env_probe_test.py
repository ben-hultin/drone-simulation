"""Tests for mission toolchain probe facade."""

import pytest

from missions.env_probe import probe_toolchain
from services.toolchain_service import ToolchainReport


def test_probe_returns_all_flags(monkeypatch: pytest.MonkeyPatch) -> None:
    paths = {"px4": "/bin/px4", "gz": "/bin/gz", "ros2": "/bin/ros2"}

    def fake_which(name: str) -> str | None:
        return paths.get(name)

    monkeypatch.setattr("services.toolchain_service._which", fake_which)
    report = probe_toolchain()
    assert report.px4_on_path is True
    assert report.ready_for_sitl is True


def test_probe_missing_tools() -> None:
    report = ToolchainReport(px4_on_path=False, gazebo_on_path=False, ros2_on_path=False)
    assert report.ready_for_sitl is False