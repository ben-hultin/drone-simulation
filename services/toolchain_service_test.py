"""Tests for toolchain service."""

import pytest

from services.toolchain_service import probe_toolchain


def test_probe_toolchain_flags(monkeypatch: pytest.MonkeyPatch) -> None:
    paths = {"px4": "/bin/px4", "gz": "/bin/gz", "ros2": "/bin/ros2"}

    def fake_which(name: str) -> str | None:
        return paths.get(name)

    monkeypatch.setattr("services.toolchain_service._which", fake_which)
    report = probe_toolchain()
    assert report.ready_for_sitl is True