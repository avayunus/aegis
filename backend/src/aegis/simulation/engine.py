"""Simulation Engine — drives the 2D tactical world.

This is a discrete-time simulation that runs in a background asyncio task.
Every tick it:
1. Updates all vehicle positions based on their current waypoint targets
2. Drains battery based on speed and time
3. Checks for anomalies (low battery, route deviation, comms loss)
4. Emits the full world state to the telemetry WebSocket

The simulation is intentionally simple but architecturally serious.
It's a 2D top-down world measured in meters. Vehicles are points with
heading, speed, and battery. Waypoints are (x, y) coordinates.
"""

import asyncio
import time
from datetime import datetime, timezone

from aegis.config import settings
from aegis.simulation.world import WorldState
from aegis.simulation.vehicle import Vehicle, VehicleStatus


class SimulationEngine:
    """Manages the simulation loop and world state."""

    def __init__(self):
        self.world = WorldState(
            width=settings.sim_world_width,
            height=settings.sim_world_height,
        )
        self.tick_interval = 1.0 / settings.sim_tick_rate_hz
        self.tick_count: int = 0
        self.running: bool = False
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        """Start the simulation loop as a background task."""
        if self.running:
            return
        self.running = True
        self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        """Gracefully stop the simulation."""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _loop(self) -> None:
        """Main simulation loop — runs at configured tick rate."""
        while self.running:
            tick_start = time.monotonic()

            # Advance the simulation by one tick
            self._step()

            # Broadcast state to all WebSocket clients
            state = self.get_state_snapshot()
            from aegis.api.telemetry import broadcast_state
            await broadcast_state(state)

            # Sleep for remainder of tick interval
            elapsed = time.monotonic() - tick_start
            sleep_time = max(0, self.tick_interval - elapsed)
            await asyncio.sleep(sleep_time)

    def _step(self) -> None:
        """Advance simulation by one tick.

        Updates vehicle positions, drains battery, checks for events.
        """
        self.tick_count += 1
        dt = self.tick_interval  # Delta time in seconds

        for vehicle in self.world.vehicles.values():
            if vehicle.status == VehicleStatus.DESTROYED:
                continue

            # Move toward current waypoint target
            vehicle.update(dt)

            # Drain battery
            vehicle.drain_battery(dt)

            # Check for low battery
            if vehicle.battery_pct <= 15.0 and vehicle.status != VehicleStatus.RTB:
                vehicle.status = VehicleStatus.LOW_BATTERY
                self.world.add_alert(
                    vehicle_id=vehicle.id,
                    alert_type="low_battery",
                    severity="warning",
                    message=f"{vehicle.callsign} battery at {vehicle.battery_pct:.0f}%",
                )

            # Check for battery critical
            if vehicle.battery_pct <= 5.0:
                vehicle.status = VehicleStatus.CRITICAL
                self.world.add_alert(
                    vehicle_id=vehicle.id,
                    alert_type="battery_critical",
                    severity="critical",
                    message=f"{vehicle.callsign} battery CRITICAL at {vehicle.battery_pct:.0f}%",
                )

    def get_state_snapshot(self) -> dict:
        """Return the full simulation state as a serializable dict.

        This is what gets sent over the WebSocket every tick.
        """
        return {
            "tick": self.tick_count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "world": {
                "width": self.world.width,
                "height": self.world.height,
            },
            "assets": [v.to_dict() for v in self.world.vehicles.values()],
            "alerts": self.world.get_recent_alerts(limit=20),
            "mission": self.world.get_mission_summary(),
        }

    def add_vehicle(self, vehicle: Vehicle) -> None:
        """Add a vehicle to the simulation."""
        self.world.vehicles[vehicle.id] = vehicle

    def get_vehicle(self, vehicle_id: str) -> Vehicle | None:
        """Look up a vehicle by ID."""
        return self.world.vehicles.get(vehicle_id)
