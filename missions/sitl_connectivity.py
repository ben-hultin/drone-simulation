"""Phase 0 SITL connectivity check mission (connect + health; no arm command)."""

from dao.mission_log.connectivity_log_dao import ConnectivityLogDao
from missions.sitl_connectivity_types import SitlConnectivityResult, SitlConnectivityStatus
from missions.sitl_connectivity_util import result_payload, status_from_arm_guard
from services.mavsdk_service import MavsdkService


class SitlConnectivityCheck:
    """Connect to SITL and evaluate arm guard without sending arm."""

    def __init__(
        self,
        mavsdk_service: MavsdkService,
        log_dao: ConnectivityLogDao | None = None,
    ) -> None:
        self._mavsdk = mavsdk_service
        self._log_dao = log_dao or ConnectivityLogDao()

    async def run(self, connect_timeout_s: float) -> SitlConnectivityResult:
        connected = await self._mavsdk.connect_or_fail(timeout_s=connect_timeout_s)
        if not connected:
            return self._persist(
                self._build_result(
                    SitlConnectivityStatus.UNREACHABLE,
                    arm_refused=True,
                    reason="connection_timeout",
                )
            )

        guard = await self._mavsdk.evaluate_arm_guard()
        status = status_from_arm_guard(guard)
        return self._persist(
            self._build_result(
                status,
                arm_refused=guard.refused,
                reason=guard.reason,
            )
        )

    def _build_result(
        self,
        status: SitlConnectivityStatus,
        *,
        arm_refused: bool,
        reason: str,
    ) -> SitlConnectivityResult:
        return SitlConnectivityResult(
            status=status,
            endpoint=self._mavsdk.connection_url,
            arm_refused=arm_refused,
            reason=reason,
            logged=False,
        )

    def _persist(self, result: SitlConnectivityResult) -> SitlConnectivityResult:
        self._log_dao.append(result_payload(result))
        return SitlConnectivityResult(
            status=result.status,
            endpoint=result.endpoint,
            arm_refused=result.arm_refused,
            reason=result.reason,
            logged=True,
        )