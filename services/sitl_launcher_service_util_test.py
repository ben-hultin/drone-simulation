"""Hermetic tests for SITL launcher stop logic."""

from unittest.mock import MagicMock

from services.sitl_launcher_service import SitlLauncherService


def test_stop_terminates_child() -> None:
    launcher = SitlLauncherService()
    proc = MagicMock()
    proc.wait.return_value = 0
    launcher._process = proc
    launcher.stop()
    proc.send_signal.assert_called_once()
    assert launcher._process is None