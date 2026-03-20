"""Tests for the SimulationEngine Phase 1 features."""

from aegis.simulation.engine import SimulationEngine
from aegis.simulation.vehicle import Vehicle, VehicleType, VehicleStatus, Waypoint


def _make_engine_with_drone() -> tuple[SimulationEngine, Vehicle]:
    """Helper: create an engine with one drone."""
    engine = SimulationEngine()
    v = Vehicle(
        id="drone-test",
        callsign="TEST-1",
        vehicle_type=VehicleType.QUADROTOR,
        x=100.0, y=100.0,
        home_x=0.0, home_y=0.0,
        max_speed_mps=10.0,
    )
    v.assign_waypoints([Waypoint(x=500.0, y=500.0, label="WP1")])
    engine.add_vehicle(v)
    return engine, v


def test_find_by_callsign():
    """find_vehicle_by_callsign should work case-insensitively."""
    engine, v = _make_engine_with_drone()
    assert engine.find_vehicle_by_callsign("TEST-1") is v
    assert engine.find_vehicle_by_callsign("test-1") is v
    assert engine.find_vehicle_by_callsign("NOPE") is None


def test_exec_rtb():
    """exec_rtb should set the vehicle to RTB status."""
    engine, v = _make_engine_with_drone()
    result = engine.exec_rtb("drone-test")
    assert result["success"] is True
    assert v.status == VehicleStatus.RTB


def test_exec_rtb_unknown():
    """exec_rtb on unknown vehicle should return error."""
    engine = SimulationEngine()
    result = engine.exec_rtb("nonexistent")
    assert result["success"] is False


def test_exec_hold():
    """exec_hold_position should stop the vehicle."""
    engine, v = _make_engine_with_drone()
    result = engine.exec_hold_position("drone-test")
    assert result["success"] is True
    assert v.status == VehicleStatus.LOITERING
    assert len(v.waypoints) == 0


def test_exec_rtb_all():
    """exec_rtb_all should send all vehicles home."""
    engine = SimulationEngine()
    for i in range(3):
        v = Vehicle(
            id=f"d-{i}", callsign=f"D-{i}",
            vehicle_type=VehicleType.QUADROTOR,
            x=float(i * 100), y=float(i * 100),
        )
        v.assign_waypoints([Waypoint(x=999, y=999)])
        engine.add_vehicle(v)

    result = engine.exec_rtb_all()
    assert result["success"] is True
    for v in engine.get_all_vehicles():
        assert v.status == VehicleStatus.RTB


def test_reset():
    """reset() should clear all vehicles and state."""
    engine, _ = _make_engine_with_drone()
    assert len(engine.get_all_vehicles()) == 1
    engine.reset()
    assert len(engine.get_all_vehicles()) == 0
    assert engine.tick_count == 0


def test_pause_resume():
    """pause/resume should toggle the paused flag."""
    engine = SimulationEngine()
    assert engine.paused is False
    engine.pause()
    assert engine.paused is True
    engine.resume()
    assert engine.paused is False
