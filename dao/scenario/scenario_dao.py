"""Load flight scenarios from YAML files."""

from pathlib import Path

import yaml

from dao.scenario.scenario_types import (
    FlightScenario,
    ScenarioGoal,
    ScenarioPassCriteria,
    ScenarioSpawn,
)


class ScenarioDao:
    """Reads scenario definitions from disk."""

    def load(self, path: Path) -> FlightScenario:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        spawn = raw["spawn"]
        goal = raw["goal"]
        criteria = raw["pass_criteria"]
        return FlightScenario(
            name=str(raw["name"]),
            world=str(raw.get("world", "")),
            spawn=ScenarioSpawn(
                north_m=float(spawn["north_m"]),
                east_m=float(spawn["east_m"]),
                alt_m=float(spawn["alt_m"]),
            ),
            goal=ScenarioGoal(
                pattern=str(goal["pattern"]),
                side_m=float(goal["side_m"]),
                altitude_m=float(goal["altitude_m"]),
            ),
            time_limit_s=float(raw["time_limit_s"]),
            pass_criteria=ScenarioPassCriteria(
                waypoint_tolerance_m=float(criteria["waypoint_tolerance_m"]),
                require_disarmed=bool(criteria.get("require_disarmed", True)),
                require_no_failsafe=bool(criteria.get("require_no_failsafe", True)),
            ),
        )