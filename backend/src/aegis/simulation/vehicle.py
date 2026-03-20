"""Vehicle model — represents a single autonomous asset in the simulation.

Each vehicle has:
- Position (x, y) in meters
- Heading in degrees (0 = north, 90 = east)
- Speed in meters per second
- Battery percentage (drains over time)
- A waypoint queue it navigates through
- A status enum tracking its operational state
"""

import math
from enum import Enum
from dataclasses import dataclass, field


class VehicleType(str, Enum):
    QUADROTOR = "quadrotor"
    FIXED_WING = "fixed_wing"
    GROUND_ROVER = "ground_rover"


class VehicleStatus(str, Enum):
    IDLE = "idle"
    EN_ROUTE = "en_route"
    LOITERING = "loitering"  # Hovering / holding position
    RTB = "rtb"  # Return to base
    LOW_BATTERY = "low_battery"
    CRITICAL = "critical"
    OFFLINE = "offline"
    DESTROYED = "destroyed"
    MISSION_COMPLETE = "mission_complete"


@dataclass
class Waypoint:
    """A target position in the world."""

    x: float
    y: float
    label: str = ""
    loiter_seconds: float = 0.0  # Time to hold at this point


@dataclass
class Vehicle:
    """A single autonomous vehicle in the simulation.

    The vehicle navigates through a queue of waypoints. When it arrives
    at a waypoint (within `arrival_radius`), it pops the waypoint and
    moves to the next. When the queue is empty, it enters IDLE or
    MISSION_COMPLETE status.
    """

    id: str
    callsign: str
    vehicle_type: VehicleType
    x: float = 0.0
    y: float = 0.0
    heading_deg: float = 0.0
    speed_mps: float = 0.0  # Current speed
    max_speed_mps: float = 15.0
    battery_pct: float = 100.0
    battery_drain_rate: float = 0.5  # % per second while moving
    status: VehicleStatus = VehicleStatus.IDLE
    waypoints: list[Waypoint] = field(default_factory=list)
    waypoints_completed: int = 0
    arrival_radius: float = 5.0  # meters — "close enough" to waypoint
    home_x: float = 0.0  # Base position for RTB
    home_y: float = 0.0

    def update(self, dt: float) -> None:
        """Advance the vehicle by one time step.

        Args:
            dt: Time delta in seconds.
        """
        if self.status in (VehicleStatus.IDLE, VehicleStatus.MISSION_COMPLETE,
                           VehicleStatus.OFFLINE, VehicleStatus.DESTROYED):
            self.speed_mps = 0.0
            return

        # Determine target position
        target = self._get_target()
        if target is None:
            self.status = VehicleStatus.MISSION_COMPLETE
            self.speed_mps = 0.0
            return

        # Calculate direction to target
        dx = target.x - self.x
        dy = target.y - self.y
        dist = math.sqrt(dx * dx + dy * dy)

        # Check if we've arrived
        if dist <= self.arrival_radius:
            self._arrive_at_waypoint()
            return

        # Steer toward target
        self.heading_deg = math.degrees(math.atan2(dx, dy)) % 360

        # Move at max speed (simple model — no acceleration curve)
        self.speed_mps = min(self.max_speed_mps, dist / dt)
        move_dist = self.speed_mps * dt

        # Update position
        angle_rad = math.radians(self.heading_deg)
        self.x += math.sin(angle_rad) * move_dist
        self.y += math.cos(angle_rad) * move_dist

    def drain_battery(self, dt: float) -> None:
        """Reduce battery based on movement and time.

        Battery drains faster when moving, slower when idle.
        """
        if self.speed_mps > 0:
            drain = self.battery_drain_rate * dt
        else:
            drain = self.battery_drain_rate * 0.1 * dt  # Idle drain

        self.battery_pct = max(0.0, self.battery_pct - drain)

    def assign_waypoints(self, waypoints: list[Waypoint]) -> None:
        """Replace the current waypoint queue and start moving."""
        self.waypoints = list(waypoints)
        self.waypoints_completed = 0
        if self.waypoints:
            self.status = VehicleStatus.EN_ROUTE

    def command_rtb(self) -> None:
        """Command the vehicle to return to base."""
        self.waypoints = [Waypoint(x=self.home_x, y=self.home_y, label="HOME")]
        self.status = VehicleStatus.RTB

    def _get_target(self) -> Waypoint | None:
        """Return the current waypoint target, or None if queue is empty."""
        if self.waypoints:
            return self.waypoints[0]
        return None

    def _arrive_at_waypoint(self) -> None:
        """Handle arrival at the current waypoint."""
        if self.waypoints:
            arrived = self.waypoints.pop(0)
            self.waypoints_completed += 1
            self.x = arrived.x
            self.y = arrived.y

        if not self.waypoints:
            if self.status == VehicleStatus.RTB:
                self.status = VehicleStatus.IDLE
            else:
                self.status = VehicleStatus.MISSION_COMPLETE

    def to_dict(self) -> dict:
        """Serialize to a dictionary for API/WebSocket transmission."""
        return {
            "id": self.id,
            "callsign": self.callsign,
            "type": self.vehicle_type.value,
            "status": self.status.value,
            "position": {"x": round(self.x, 1), "y": round(self.y, 1)},
            "heading_deg": round(self.heading_deg, 1),
            "speed_mps": round(self.speed_mps, 1),
            "battery_pct": round(self.battery_pct, 1),
            "waypoints_completed": self.waypoints_completed,
            "waypoints_remaining": len(self.waypoints),
            "waypoints": [
                {"x": round(wp.x, 1), "y": round(wp.y, 1), "label": wp.label}
                for wp in self.waypoints
            ],
        }
