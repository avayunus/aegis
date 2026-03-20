"""Tests for the JSON scenario loader."""

from aegis.simulation.engine import SimulationEngine
from aegis.simulation.scenarios import list_scenarios, load_scenario_from_file, SCENARIOS_DIR


def test_scenarios_directory_exists():
    """Scenario directory should exist and contain JSON files."""
    assert SCENARIOS_DIR.exists()
    jsons = list(SCENARIOS_DIR.glob("*.json"))
    assert len(jsons) >= 2  # search-and-rescue + perimeter-patrol


def test_list_scenarios():
    """list_scenarios should return metadata for all JSON files."""
    scenarios = list_scenarios()
    assert len(scenarios) >= 2
    names = [s["id"] for s in scenarios]
    assert "search-and-rescue" in names
    assert "perimeter-patrol" in names


def test_load_search_and_rescue():
    """Loading SAR scenario should create 3 vehicles."""
    engine = SimulationEngine()
    meta = load_scenario_from_file(engine, "search-and-rescue.json")
    assert meta["id"] == "search-and-rescue"
    assert meta["asset_count"] == 4  # 3 drones + 1 rover
    assert len(engine.get_all_vehicles()) == 4


def test_load_perimeter_patrol():
    """Loading patrol scenario should create 3 vehicles."""
    engine = SimulationEngine()
    meta = load_scenario_from_file(engine, "perimeter-patrol.json")
    assert meta["id"] == "perimeter-patrol"
    assert meta["asset_count"] == 3
    assert len(engine.get_all_vehicles()) == 3


def test_loaded_vehicles_have_waypoints():
    """Vehicles loaded from JSON should have their waypoints assigned."""
    engine = SimulationEngine()
    load_scenario_from_file(engine, "search-and-rescue.json")
    for v in engine.get_all_vehicles():
        assert len(v.waypoints) > 0, f"{v.callsign} has no waypoints"
