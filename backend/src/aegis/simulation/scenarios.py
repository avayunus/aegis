"""Scenario definitions — predefined missions for demos and testing.

Each scenario function sets up the world with vehicles and waypoints.
Call one from the startup lifespan or from a demo API endpoint.
"""

from aegis.simulation.engine import SimulationEngine
from aegis.simulation.vehicle import Vehicle, VehicleType, Waypoint


def load_search_and_rescue(engine: SimulationEngine) -> None:
    """Search-and-rescue scenario: 3 drones sweep a grid pattern.

    Scenario:
        A distress signal was received from a 500x500m zone in the northeast
        quadrant. Three drones are dispatched from base (0, 0) to sweep
        the area in parallel lanes.
    """
    # Drone 1 — West lane
    d1 = Vehicle(
        id="drone-01",
        callsign="HAWK-1",
        vehicle_type=VehicleType.QUADROTOR,
        x=50.0, y=50.0,
        home_x=50.0, home_y=50.0,
        max_speed_mps=12.0,
        battery_drain_rate=0.3,
    )
    d1.assign_waypoints([
        Waypoint(x=200.0, y=500.0, label="WP-A1"),
        Waypoint(x=200.0, y=700.0, label="WP-A2"),
        Waypoint(x=200.0, y=900.0, label="WP-A3"),
        Waypoint(x=50.0, y=50.0, label="HOME"),
    ])

    # Drone 2 — Center lane
    d2 = Vehicle(
        id="drone-02",
        callsign="HAWK-2",
        vehicle_type=VehicleType.QUADROTOR,
        x=50.0, y=100.0,
        home_x=50.0, home_y=100.0,
        max_speed_mps=12.0,
        battery_drain_rate=0.3,
    )
    d2.assign_waypoints([
        Waypoint(x=500.0, y=500.0, label="WP-B1"),
        Waypoint(x=500.0, y=700.0, label="WP-B2"),
        Waypoint(x=500.0, y=900.0, label="WP-B3"),
        Waypoint(x=50.0, y=100.0, label="HOME"),
    ])

    # Drone 3 — East lane
    d3 = Vehicle(
        id="drone-03",
        callsign="HAWK-3",
        vehicle_type=VehicleType.QUADROTOR,
        x=100.0, y=50.0,
        home_x=100.0, home_y=50.0,
        max_speed_mps=12.0,
        battery_drain_rate=0.3,
    )
    d3.assign_waypoints([
        Waypoint(x=800.0, y=500.0, label="WP-C1"),
        Waypoint(x=800.0, y=700.0, label="WP-C2"),
        Waypoint(x=800.0, y=900.0, label="WP-C3"),
        Waypoint(x=100.0, y=50.0, label="HOME"),
    ])

    engine.add_vehicle(d1)
    engine.add_vehicle(d2)
    engine.add_vehicle(d3)

    print("[Scenario] Loaded: Search & Rescue — 3 drones, grid sweep pattern")


def load_perimeter_patrol(engine: SimulationEngine) -> None:
    """Perimeter patrol scenario: 2 drones + 1 ground rover patrol a boundary.

    Scenario:
        A 800x800m facility perimeter needs continuous monitoring.
        Two drones patrol the air boundary while a ground rover
        follows the fence line.
    """
    # Air patrol — clockwise
    d1 = Vehicle(
        id="drone-04",
        callsign="SENTRY-1",
        vehicle_type=VehicleType.QUADROTOR,
        x=100.0, y=100.0,
        home_x=100.0, home_y=100.0,
        max_speed_mps=10.0,
        battery_drain_rate=0.25,
    )
    d1.assign_waypoints([
        Waypoint(x=900.0, y=100.0, label="NE-Corner"),
        Waypoint(x=900.0, y=900.0, label="SE-Corner"),
        Waypoint(x=100.0, y=900.0, label="SW-Corner"),
        Waypoint(x=100.0, y=100.0, label="NW-Corner"),
    ])

    # Air patrol — counter-clockwise
    d2 = Vehicle(
        id="drone-05",
        callsign="SENTRY-2",
        vehicle_type=VehicleType.QUADROTOR,
        x=100.0, y=900.0,
        home_x=100.0, home_y=100.0,
        max_speed_mps=10.0,
        battery_drain_rate=0.25,
    )
    d2.assign_waypoints([
        Waypoint(x=100.0, y=100.0, label="NW-Corner"),
        Waypoint(x=900.0, y=100.0, label="NE-Corner"),
        Waypoint(x=900.0, y=900.0, label="SE-Corner"),
        Waypoint(x=100.0, y=900.0, label="SW-Corner"),
    ])

    # Ground rover — fence line
    rover = Vehicle(
        id="rover-01",
        callsign="GROUND-1",
        vehicle_type=VehicleType.GROUND_ROVER,
        x=100.0, y=100.0,
        home_x=100.0, home_y=100.0,
        max_speed_mps=3.0,
        battery_drain_rate=0.15,
    )
    rover.assign_waypoints([
        Waypoint(x=500.0, y=100.0, label="N-Mid"),
        Waypoint(x=900.0, y=100.0, label="NE-Corner"),
        Waypoint(x=900.0, y=500.0, label="E-Mid"),
        Waypoint(x=900.0, y=900.0, label="SE-Corner"),
    ])

    engine.add_vehicle(d1)
    engine.add_vehicle(d2)
    engine.add_vehicle(rover)

    print("[Scenario] Loaded: Perimeter Patrol — 2 drones + 1 rover")
