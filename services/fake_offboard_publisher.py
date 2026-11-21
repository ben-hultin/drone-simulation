"""Test double for offboard setpoint publishing."""

from services.offboard_command_protocol import OffboardSetpoint


class FakeOffboardPublisher:
    def __init__(self, *, fail_enable: bool = False) -> None:
        self._fail_enable = fail_enable
        self.enabled = False
        self.setpoints: list[OffboardSetpoint] = []
        self.disable_called = False

    async def enable_offboard(self) -> None:
        if self._fail_enable:
            raise RuntimeError("offboard_rejected")
        self.enabled = True

    async def publish_setpoint(self, setpoint: OffboardSetpoint) -> None:
        if not self.enabled:
            raise RuntimeError("offboard_not_enabled")
        self.setpoints.append(setpoint)

    async def disable_offboard(self) -> None:
        self.enabled = False
        self.disable_called = True