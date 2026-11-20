"""Build MAVSDK offboard position messages without importing mavsdk at module load."""


def build_position_ned_yaw(
    north_m: float,
    east_m: float,
    down_m: float,
    yaw_deg: float,
):
    try:
        from mavsdk_grpc.offboard import PositionNedYaw

        return PositionNedYaw(north_m, east_m, down_m, yaw_deg)
    except ImportError:
        from dataclasses import dataclass

        @dataclass
        class _PositionNedYaw:
            north_m: float
            east_m: float
            down_m: float
            yaw_deg: float

        return _PositionNedYaw(north_m, east_m, down_m, yaw_deg)