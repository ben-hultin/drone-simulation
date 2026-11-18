"""Live MAVSDK gateway factory (lazy import; optional at static test time)."""

from services.mavsdk_live_gateway import MavsdkLiveGateway
from services.mavsdk_protocol import VehicleGateway
from services.mavsdk_url_util import validate_connection_url


def create_live_gateway(connection_url: str, *, allow_remote: bool = False) -> VehicleGateway:
    """Build a validated MAVSDK gateway when mavsdk is installed."""
    validated = validate_connection_url(connection_url, allow_remote=allow_remote)
    return MavsdkLiveGateway(validated, allow_remote=allow_remote)