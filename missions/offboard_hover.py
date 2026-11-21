"""Phase 2 offboard hover with pose, depth, and point-cloud perception."""

import time

from dao.flight_log.ulg_metrics_dao import UlgMetricsDao
from dao.flight_log.ulg_reader_protocol import UlgReader
from dao.mission_log.rosbag_log_dao import RosbagLogDao
from dao.scenario.hover_scenario_types import HoverScenario
from missions.depth_to_pointcloud import DepthToPointCloudConverter
from missions.offboard_hover_run_util import (
    run_hover_loop,
    run_hover_preflight,
    run_offboard_climb,
)
from missions.offboard_hover_types import OffboardHoverResult, OffboardHoverStatus
from missions.offboard_hover_util import await_fresh_depth, await_fresh_pose
from services.mavsdk_service import MavsdkService
from services.offboard_command_protocol import OffboardPublisher
from services.perception_protocol import DepthSource, PoseSource

DEFAULT_CONNECT_TIMEOUT_S = 10.0


class OffboardHoverMission:
    """Arm, climb/hover via offboard setpoints, land; requires perception inputs."""

    def __init__(
        self,
        mavsdk: MavsdkService,
        scenario: HoverScenario,
        pose_source: PoseSource,
        depth_source: DepthSource,
        offboard: OffboardPublisher,
        *,
        ulg_dao: UlgMetricsDao | None = None,
        ulg_reader: UlgReader | None = None,
        rosbag_dao: RosbagLogDao | None = None,
        converter: DepthToPointCloudConverter | None = None,
        connect_timeout_s: float = DEFAULT_CONNECT_TIMEOUT_S,
    ) -> None:
        self._mavsdk = mavsdk
        self._scenario = scenario
        self._pose = pose_source
        self._depth = depth_source
        self._offboard = offboard
        self._ulg_dao = ulg_dao or UlgMetricsDao()
        self._ulg_reader = ulg_reader
        self._rosbag_dao = rosbag_dao or RosbagLogDao()
        self._converter = converter or DepthToPointCloudConverter()
        self._connect_timeout_s = connect_timeout_s

    async def run(self, connect_timeout_s: float | None = None) -> OffboardHoverResult:
        deadline = time.monotonic() + self._scenario.time_limit_s
        timeout = connect_timeout_s if connect_timeout_s is not None else self._connect_timeout_s
        inflight_active = False
        setpoints = 0
        point_count = 0
        try:
            pre = await run_hover_preflight(self._mavsdk, deadline, connect_timeout_s=timeout)
            if pre is not None:
                return pre
            perception = await self._load_perception()
            if isinstance(perception, OffboardHoverResult):
                return perception
            point_count = perception
            if not await self._mavsdk.arm_or_fail():
                return _fail(OffboardHoverStatus.ARM_FAILED, "arm_failed", point_count)
            inflight_active = True
            if not await self._enable_offboard():
                if not await self._mavsdk.disarm_or_fail():
                    return _fail(
                        OffboardHoverStatus.DISARM_FAILED,
                        "disarm_after_offboard_failed",
                        point_count,
                    )
                inflight_active = False
                return _fail(
                    OffboardHoverStatus.OFFBOARD_FAILED,
                    "offboard_enable_failed",
                    point_count,
                )
            climb = await run_offboard_climb(
                self._mavsdk,
                self._offboard,
                self._scenario,
                deadline,
            )
            if climb is not None:
                return _with_points(climb, point_count, setpoints)
            published, hover_fail = await run_hover_loop(
                self._mavsdk,
                self._offboard,
                self._scenario,
                deadline,
            )
            setpoints = published
            if hover_fail is not None:
                return _with_points(hover_fail, point_count, setpoints)
            land_result = await self._land_and_disarm(point_count, setpoints, deadline)
            if isinstance(land_result, OffboardHoverResult):
                return land_result
            inflight_active = False
        finally:
            if inflight_active:
                await self._offboard.disable_offboard()
                await self._mavsdk.abort_inflight_failsafe()
        ulg_saved, rosbag_recorded = await self._persist_logs()
        return OffboardHoverResult(
            status=OffboardHoverStatus.SUCCESS,
            reason="completed",
            point_count=point_count,
            hover_setpoints_published=setpoints,
            ulg_saved=ulg_saved,
            rosbag_recorded=rosbag_recorded,
        )

    async def _load_perception(self) -> int | OffboardHoverResult:
        if await self._read_pose() is None:
            return _fail(OffboardHoverStatus.POSE_TIMEOUT, "pose_unavailable")
        depth = await self._read_depth()
        if depth is None:
            return _fail(OffboardHoverStatus.DEPTH_TIMEOUT, "depth_unavailable")
        try:
            cloud = self._converter.convert(depth)
        except ValueError as err:
            return _fail(OffboardHoverStatus.DEPTH_TIMEOUT, str(err))
        return len(cloud.points)

    async def _enable_offboard(self) -> bool:
        try:
            await self._offboard.enable_offboard()
        except (TimeoutError, OSError, RuntimeError, ValueError, TypeError):
            return False
        return True

    async def _land_and_disarm(
        self,
        point_count: int,
        setpoints: int,
        deadline: float,
    ) -> bool | OffboardHoverResult:
        if time.monotonic() > deadline:
            return _fail(
                OffboardHoverStatus.TIME_LIMIT,
                "scenario_time_limit",
                point_count,
                setpoints,
            )
        if not await self._mavsdk.land_or_fail(failsafe_if_inflight=False):
            return _fail(OffboardHoverStatus.LAND_FAILED, "land_failed", point_count, setpoints)
        if not await self._mavsdk.wait_landed_or_fail():
            return _fail(
                OffboardHoverStatus.LAND_FAILED,
                "land_confirm_timeout",
                point_count,
                setpoints,
            )
        await self._offboard.disable_offboard()
        crit = self._scenario.pass_criteria
        if crit.require_disarmed and not await self._mavsdk.disarm_or_fail():
            return _fail(OffboardHoverStatus.DISARM_FAILED, "disarm_failed", point_count, setpoints)
        if crit.require_no_failsafe and await self._mavsdk.read_failsafe():
            return _fail(OffboardHoverStatus.FAILSAFE, "failsafe_at_end", point_count, setpoints)
        return False

    async def _read_pose(self):
        crit = self._scenario.pass_criteria
        if not crit.require_pose:
            return await self._pose.latest_pose()
        return await await_fresh_pose(self._pose, self._scenario)

    async def _read_depth(self):
        crit = self._scenario.pass_criteria
        if not crit.require_depth_frame:
            return await self._depth.latest_depth()
        return await await_fresh_depth(self._depth, self._scenario)

    async def _persist_logs(self) -> tuple[bool, bool]:
        ulg_saved = False
        rosbag_recorded = False
        ulg_path = await self._mavsdk.copy_ulg_path()
        if ulg_path and self._ulg_reader is not None:
            self._ulg_dao.save_run(ulg_path, self._ulg_reader)
            ulg_saved = True
        if ulg_saved:
            self._rosbag_dao.record_run(self._scenario.name)
            rosbag_recorded = True
        return ulg_saved, rosbag_recorded


def _fail(
    status: OffboardHoverStatus,
    reason: str,
    point_count: int = 0,
    setpoints: int = 0,
) -> OffboardHoverResult:
    return OffboardHoverResult(
        status=status,
        reason=reason,
        point_count=point_count,
        hover_setpoints_published=setpoints,
    )


def _with_points(
    result: OffboardHoverResult,
    point_count: int,
    setpoints: int,
) -> OffboardHoverResult:
    return OffboardHoverResult(
        status=result.status,
        reason=result.reason,
        point_count=point_count,
        hover_setpoints_published=setpoints,
        ulg_saved=result.ulg_saved,
        rosbag_recorded=result.rosbag_recorded,
    )