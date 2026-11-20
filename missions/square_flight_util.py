"""Helpers for square flight mission and scenario wiring."""

from dao.scenario.scenario_types import FlightScenario


def square_waypoints(side_m: float, altitude_m: float) -> list[tuple[float, float, float]]:
    return [
        (side_m, 0.0, altitude_m),
        (side_m, side_m, altitude_m),
        (0.0, side_m, altitude_m),
        (0.0, 0.0, altitude_m),
    ]


def waypoints_for_scenario(scenario: FlightScenario) -> list[tuple[float, float, float]]:
    if scenario.goal.pattern != "square":
        raise ValueError("unsupported_goal_pattern")
    base = square_waypoints(scenario.goal.side_m, scenario.goal.altitude_m)
    spawn = scenario.spawn
    return [(n + spawn.north_m, e + spawn.east_m, alt) for n, e, alt in base]