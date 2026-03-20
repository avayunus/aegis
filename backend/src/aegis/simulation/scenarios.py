"""Scenario loader — reads scenario configs from JSON files.

Phase 1 upgrade: instead of hardcoded Python functions, scenarios are
loaded from JSON files in the /scenarios directory. This makes it easy
to create new demos, share them, and version-control them.
"""

import json
from pathlib import Path

from aegis.simulation.engine import SimulationEngine
from aegis.simulation.vehicle import Vehicle, VehicleType, Waypoint

# Map JSON vehicle types to enum values
_VEHICLE_TYPE_MAP = {
    "quadrotor": VehicleType.QUADROTOR,
    "fixed_wing": VehicleType.FIXED_WING,
    "ground_rover": VehicleType.GROUND_ROVER,
    "ground_vehicle": VehicleType.GROUND_ROVER,
}

# Default scenario search path
SCENARIOS_DIR = Path(__file__).resolve().parents[4] / "scenarios"


def list_scenarios() -> list[dict]:
    """Return metadata for all available scenario files."""
    results = []
    if not SCENARIOS_DIR.exists():
        return results
    for f in sorted(SCENARIOS_DIR.glob("*.json")):
        try:
            data = json.loads(f.read_text())
            results.append({
                "id": data.get("id", f.stem),
                "name": data.get("name", f.stem),
                "description": data.get("description", ""),
                "mission_type": data.get("mission_type", "unknown"),
                "asset_count": len(data.get("assets", [])),
                "filename": f.name,
            })
        except (json.JSONDecodeError, KeyError):
            continue
    return results


def load_scenario_from_file(engine: SimulationEngine, filename: str) -> dict:
    """Load a scenario from a JSON file and populate the simulation engine.

    Args:
        engine: The simulation engine to populate.
        filename: Name of the JSON file (e.g., 'search-and-rescue.json').

    Returns:
        The parsed scenario metadata dict.

    Raises:
        FileNotFoundError: If the scenario file doesn't exist.
        ValueError: If the JSON is malformed.
    """
    filepath = SCENARIOS_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Scenario file not found: {filepath}")

    data = json.loads(filepath.read_text())

    # Update world size if specified
    if "world" in data:
        engine.world.width = data["world"].get("width", engine.world.width)
        engine.world.height = data["world"].get("height", engine.world.height)

    # Load each asset
    for asset_def in data.get("assets", []):
        vtype = _VEHICLE_TYPE_MAP.get(asset_def["vehicle_type"], VehicleType.QUADROTOR)

        vehicle = Vehicle(
            id=asset_def["id"],
            callsign=asset_def["callsign"],
            vehicle_type=vtype,
            x=float(asset_def.get("start_x", 0)),
            y=float(asset_def.get("start_y", 0)),
            home_x=float(asset_def.get("home_x", 0)),
            home_y=float(asset_def.get("home_y", 0)),
            max_speed_mps=float(asset_def.get("max_speed_mps", 10.0)),
            battery_pct=float(asset_def.get("battery_pct", 100.0)),
            battery_drain_rate=float(asset_def.get("battery_drain_rate", 0.3)),
        )

        waypoints = [
            Waypoint(
                x=float(wp["x"]),
                y=float(wp["y"]),
                label=wp.get("label", ""),
            )
            for wp in asset_def.get("waypoints", [])
        ]
        if waypoints:
            vehicle.assign_waypoints(waypoints)

        engine.add_vehicle(vehicle)

    asset_count = len(data.get("assets", []))
    name = data.get("name", filename)
    print(f"[Scenario] Loaded: {name} — {asset_count} assets")

    return {
        "id": data.get("id", filename.replace(".json", "")),
        "name": name,
        "description": data.get("description", ""),
        "mission_type": data.get("mission_type", "unknown"),
        "asset_count": asset_count,
    }


def load_default_scenario(engine: SimulationEngine) -> dict:
    """Load the default demo scenario (search-and-rescue)."""
    return load_scenario_from_file(engine, "search-and-rescue.json")
