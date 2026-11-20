"""Re-exports for fake gateway tests."""

from services.nav_position_util import distance_to_waypoint, position_at_waypoint

__all__ = ["distance_to_waypoint", "position_at_waypoint"]