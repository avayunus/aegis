"""Simulation Engine — drives the 2D tactical world.

This is a discrete-time simulation that runs in a background asyncio task.
Every tick it:
1. Updates all vehicle positions based on their current waypoint targets
2. Drains battery based on speed and time
3. Checks for anomalies (low battery, route deviation, comms loss)
4. Emits the full world state to the telemetry WebSocket

Phase 1 additions:
- Reset capability (reload scenarios without restarting)
- Pause/resume
- Command execution against live vehicles
- Mission ID tracking
- Elapsed time tracking
"""

import asyncio
import time
from datetime import datetime, timezone

from aegis.config import settings
from aegis.simulation.world import WorldState
from aegis.simulation.vehicle import Vehicle, VehicleStatus, Waypoint


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
        self.paused: bool = False
        self.mission_id: str | None = None
        self.mission_name: str = ""
        self.started_at: datetime | None = None
        self._task: asyncio.Task | None = None

    def reset(self) -> None:
        """Clear all vehicles, alerts, and reset tick counter.

        Call this before loading a new scenario.
        """
        self.world = WorldState(
            width=settings.sim_world_width,
            height=settings.sim_world_height,
        )
        self.tick_count = 0
        self.paused = False
        self.mission_id = None
        self.mission_name = ""
        self.started_at = None
        print("[SimEngine] Reset complete")

    async def start(self) -> None:
        """Start the simulation loop as a background task."""
        if self.running:
            return
        self.running = True
        self.started_at = datetime.now(timezone.utc)
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

    def pause(self) -> None:
        """Pause the simulation (vehicles stop moving, ticks still broadcast)."""
        self.paused = True
        print("[SimEngine] Paused")

    def resume(self) -> None:
        """Resume a paused simulation."""
        self.paused = False
        print("[SimEngine] Resumed")

    async def _loop(self) -> None:
        """Main simulation loop — runs at configured tick rate."""
        while self.running:
            tick_start = time.monotonic()

            # Advance the simulation by one tick (unless paused)
            if not self.paused:
                self._step()

            # Always broadcast state (even when paused — operator still sees current state)
            state = self.get_state_snapshot()
            from aegis.api.telemetry import broadcast_state
            await broadcast_state(state)

            # Sleep for remainder of tick interval
            elapsed = time.monotonic() - tick_start
            sleep_time = max(0, self.tick_interval - elapsed)
            await asyncio.sleep(sleep_time)

    def _step(self) -> None:
        """Advance simulation by one tick."""
        self.tick_count += 1
        dt = self.tick_interval

        for vehicle in self.world.vehicles.values():
            if vehicle.status in (VehicleStatus.DESTROYED, VehicleStatus.OFFLINE):
                continue

            # Store previous position for deviation check
            prev_x, prev_y = vehicle.x, vehicle.y

            # Move toward current waypoint target
            vehicle.update(dt)

            # Drain battery
            vehicle.drain_battery(dt)

            # ── Anomaly checks ───────────────────────────
            # Low battery warning (15-5%)
            if (5.0 < vehicle.battery_pct <= 15.0
                    and vehicle.status not in (VehicleStatus.RTB, VehicleStatus.LOW_BATTERY)):
                vehicle.status = VehicleStatus.LOW_BATTERY
                self.world.add_alert(
                    vehicle_id=vehicle.id,
                    alert_type="low_battery",
                    severity="warning",
                    message=f"{vehicle.callsign} battery at {vehicle.battery_pct:.0f}%",
                )

            # Battery critical (<5%) — auto-RTB
            if vehicle.battery_pct <= 5.0 and vehicle.status != VehicleStatus.CRITICAL:
                vehicle.status = VehicleStatus.CRITICAL
                vehicle.command_rtb()
                self.world.add_alert(
                    vehicle_id=vehicle.id,
                    alert_type="battery_critical",
                    severity="critical",
                    message=(
                        f"{vehicle.callsign} battery CRITICAL ({vehicle.battery_pct:.0f}%) "
                        f"— AUTO RTB initiated"
                    ),
                )

            # Battery dead
            if vehicle.battery_pct <= 0.0:
                vehicle.status = VehicleStatus.OFFLINE
                vehicle.speed_mps = 0.0
                self.world.add_alert(
                    vehicle_id=vehicle.id,
                    alert_type="battery_dead",
                    severity="critical",
                    message=f"{vehicle.callsign} battery DEPLETED — asset offline",
                )

    def get_state_snapshot(self) -> dict:
        """Return the full simulation state as a serializable dict."""
        elapsed = 0.0
        if self.started_at:
            elapsed = (datetime.now(timezone.utc) - self.started_at).total_seconds()

        return {
            "tick": self.tick_count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "paused": self.paused,
            "elapsed_seconds": round(elapsed, 1),
            "mission_id": self.mission_id,
            "mission_name": self.mission_name,
            "world": {
                "width": self.world.width,
                "height": self.world.height,
            },
            "assets": [v.to_dict() for v in self.world.vehicles.values()],
            "alerts": self.world.get_recent_alerts(limit=20),
            "mission": self.world.get_mission_summary(),
        }

    # ── Vehicle management ────────────────────────────
    def add_vehicle(self, vehicle: Vehicle) -> None:
        """Add a vehicle to the simulation."""
        self.world.vehicles[vehicle.id] = vehicle

    def get_vehicle(self, vehicle_id: str) -> Vehicle | None:
        """Look up a vehicle by ID."""
        return self.world.vehicles.get(vehicle_id)

    def find_vehicle_by_callsign(self, callsign: str) -> Vehicle | None:
        """Look up a vehicle by callsign (case-insensitive)."""
        callsign_upper = callsign.upper().strip()
        for v in self.world.vehicles.values():
            if v.callsign.upper() == callsign_upper:
                return v
        return None

    def get_all_vehicles(self) -> list[Vehicle]:
        """Return all vehicles."""
        return list(self.world.vehicles.values())

    # ── Command execution ─────────────────────────────
    def exec_rtb(self, vehicle_id: str) -> dict:
        """Command a specific vehicle to return to base."""
        v = self.get_vehicle(vehicle_id)
        if not v:
            return {"success": False, "error": f"Vehicle {vehicle_id} not found"}
        v.command_rtb()
        self.world.add_alert(
            vehicle_id=v.id,
            alert_type="command_executed",
            severity="info",
            message=f"{v.callsign} commanded to return to base",
        )
        return {"success": True, "message": f"{v.callsign} returning to base"}

    def exec_rtb_all(self) -> dict:
        """Command ALL vehicles to return to base."""
        count = 0
        for v in self.world.vehicles.values():
            if v.status not in (VehicleStatus.DESTROYED, VehicleStatus.OFFLINE):
                v.command_rtb()
                count += 1
        self.world.add_alert(
            vehicle_id="all",
            alert_type="command_executed",
            severity="warning",
            message=f"ALL assets ({count}) commanded to return to base",
        )
        return {"success": True, "message": f"{count} assets returning to base"}

    def exec_assign_waypoints(self, vehicle_id: str, waypoints: list[dict]) -> dict:
        """Assign new waypoints to a vehicle."""
        v = self.get_vehicle(vehicle_id)
        if not v:
            return {"success": False, "error": f"Vehicle {vehicle_id} not found"}
        wps = [
            Waypoint(x=float(wp["x"]), y=float(wp["y"]), label=wp.get("label", ""))
            for wp in waypoints
        ]
        v.assign_waypoints(wps)
        self.world.add_alert(
            vehicle_id=v.id,
            alert_type="command_executed",
            severity="info",
            message=f"{v.callsign} assigned {len(wps)} new waypoints",
        )
        return {"success": True, "message": f"{v.callsign} assigned {len(wps)} waypoints"}

    def exec_hold_position(self, vehicle_id: str) -> dict:
        """Command a vehicle to hold/loiter at current position."""
        v = self.get_vehicle(vehicle_id)
        if not v:
            return {"success": False, "error": f"Vehicle {vehicle_id} not found"}
        v.waypoints.clear()
        v.status = VehicleStatus.LOITERING
        v.speed_mps = 0.0
        self.world.add_alert(
            vehicle_id=v.id,
            alert_type="command_executed",
            severity="info",
            message=f"{v.callsign} holding position at ({v.x:.0f}, {v.y:.0f})",
        )
        return {"success": True, "message": f"{v.callsign} holding position"}
