"""pytest fixtures for optional live SITL (never auto-run in default suite)."""

import os

import pytest

from services.sitl_launcher_service import SitlLauncherService
from services.toolchain_service import probe_toolchain


def _sitl_available() -> bool:
    report = probe_toolchain()
    px4_dir = os.environ.get("PX4_AUTOPILOT_DIR", "")
    px4_ready = bool(px4_dir) and os.path.isdir(px4_dir)
    return (report.gazebo_on_path and (report.px4_on_path or px4_ready))


@pytest.fixture(scope="session")
def sitl_stack():
    """Start PX4 SITL + Gazebo when toolchain and PX4_AUTOPILOT_DIR are present."""
    if not _sitl_available():
        pytest.skip("sitl_unavailable")
    launcher = SitlLauncherService()
    if not launcher.start():
        pytest.skip("sitl_unavailable")
    yield launcher
    launcher.stop()