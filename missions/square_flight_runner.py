"""Live SITL square flight runner (requires mavsdk_grpc + running PX4 SITL)."""

import asyncio
from pathlib import Path

from dao.flight_log.ulg_metrics_dao import UlgMetricsDao
from dao.scenario.scenario_dao import ScenarioDao
from missions.square_flight import SquareFlightMission
from services.mavsdk_live_util import create_live_gateway
from services.mavsdk_service import DEFAULT_MAVSDK_URL, MavsdkService
from services.ulg_parser_service import UlgParserService


async def run_live_square_flight() -> None:
    root = Path(__file__).resolve().parents[1]
    scenario = ScenarioDao().load(root / "scenarios" / "square_5m.yaml")
    gateway = create_live_gateway(DEFAULT_MAVSDK_URL)
    try:
        mission = SquareFlightMission(
            MavsdkService(gateway, DEFAULT_MAVSDK_URL),
            scenario,
            ulg_dao=UlgMetricsDao(),
            ulg_reader=UlgParserService(),
        )
        result = await mission.run()
        print(result)
    finally:
        await gateway.close()


def main() -> None:
    asyncio.run(run_live_square_flight())


if __name__ == "__main__":
    main()