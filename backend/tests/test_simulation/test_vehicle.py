"""Tests for the Vehicle simulation model."""

import math
from aegis.simulation.vehicle import Vehicle, VehicleType, VehicleStatus, Waypoint


def test_vehicle_moves_toward_waypoint():
    """Vehicle should move toward its first waypoint when en_route."""
    v = Vehicle(
        id="test-01",
        callsign="TEST-1",
        vehicle_type=VehicleType.QUADROTOR,
        x=0.0,
        y=0.0,
        max_speed_mps=10.0,
    )
    v.assign_waypoints([Waypoint(x=100.0, y=0.0)])
    assert v.status == VehicleStatus.EN_ROUTE

    # Simulate 1 second
    v.update(dt=1.0)
    assert v.x > 0.0  # Should have moved toward x=100
    assert v.speed_mps > 0.0


def test_vehicle_arrives_at_waypoint():
    """Vehicle should mark waypoint complete when within arrival radius."""
    v = Vehicle(
        id="test-02",
        callsign="TEST-2",
        vehicle_type=VehicleType.QUADROTOR,
        x=98.0,
        y=0.0,
        arrival_radius=5.0,
    )
    v.assign_waypoints([Waypoint(x=100.0, y=0.0)])
    v.update(dt=1.0)

    assert v.waypoints_completed == 1
    assert len(v.waypoints) == 0
    assert v.status == VehicleStatus.MISSION_COMPLETE


def test_vehicle_battery_drains():
    """Battery should decrease when the vehicle is moving."""
    v = Vehicle(
        id="test-03",
        callsign="TEST-3",
        vehicle_type=VehicleType.QUADROTOR,
        battery_pct=100.0,
        battery_drain_rate=1.0,
    )
    v.speed_mps = 10.0  # Pretend it's moving
    v.drain_battery(dt=1.0)
    assert v.battery_pct < 100.0


def test_vehicle_rtb():
    """Return-to-base should set waypoint to home and change status."""
    v = Vehicle(
        id="test-04",
        callsign="TEST-4",
        vehicle_type=VehicleType.GROUND_ROVER,
        x=500.0,
        y=500.0,
        home_x=0.0,
        home_y=0.0,
    )
    v.command_rtb()
    assert v.status == VehicleStatus.RTB
    assert len(v.waypoints) == 1
    assert v.waypoints[0].x == 0.0
    assert v.waypoints[0].y == 0.0


def test_vehicle_to_dict():
    """Serialization should produce a clean dictionary."""
    v = Vehicle(
        id="test-05",
        callsign="TEST-5",
        vehicle_type=VehicleType.QUADROTOR,
        x=123.456,
        y=789.012,
        battery_pct=67.89,
    )
    d = v.to_dict()
    assert d["id"] == "test-05"
    assert d["callsign"] == "TEST-5"
    assert d["position"]["x"] == 123.5  # Rounded
    assert d["battery_pct"] == 67.9
