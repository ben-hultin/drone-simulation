"""Tests for SITL launcher configuration."""

from pathlib import Path

from services.sitl_launcher_service import SitlLauncherConfig, SitlLauncherService


def test_launcher_requires_toolchain() -> None:
    config = SitlLauncherConfig(px4_autopilot_dir=Path("/nonexistent"))
    launcher = SitlLauncherService(config)
    assert launcher.can_launch is False
    assert launcher.start() is False