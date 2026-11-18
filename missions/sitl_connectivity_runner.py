"""Live SITL connectivity runner (requires mavsdk + running PX4 SITL)."""

import asyncio

from missions.sitl_connectivity import SitlConnectivityCheck
from services.mavsdk_live_util import create_live_gateway
from services.mavsdk_service import DEFAULT_MAVSDK_URL, MavsdkService


async def run_live_sitl_connectivity(connect_timeout_s: float = 10.0) -> None:
    """Connect using validated live gateway wiring."""
    gateway = create_live_gateway(DEFAULT_MAVSDK_URL)
    try:
        mission = SitlConnectivityCheck(MavsdkService(gateway, DEFAULT_MAVSDK_URL))
        result = await mission.run(connect_timeout_s=connect_timeout_s)
        print(result)
    finally:
        await gateway.close()


def main() -> None:
    asyncio.run(run_live_sitl_connectivity())


if __name__ == "__main__":
    main()