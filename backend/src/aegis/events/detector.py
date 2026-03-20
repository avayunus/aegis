"""Anomaly detector — monitors simulation state for events. Phase 6.

Checks every simulation tick for anomalous conditions and generates
alerts that surface in the operator console.

Detection categories:
- Low battery (warning at 20%, critical at 5%)
- Route deviation (asset drifting from planned path)
- Communication loss (simulated signal dropout)
- Sensor anomaly (simulated sensor failure)
- Asset conflict (two assets too close together)
- Mission delay (asset not progressing toward waypoint)
"""

from aegis.simulation.vehicle import Vehicle, VehicleStatus


class AnomalyDetector:
    """Scans world state for anomalies each simulation tick."""

    def __init__(self):
        self.conflict_radius = 30.0  # meters — minimum safe separation
        self.stall_threshold_seconds = 30.0

    def check_vehicle(self, vehicle: Vehicle) -> list[dict]:
        """Check a single vehicle for anomalous conditions.

        Returns a list of alert dicts (may be empty).
        """
        alerts = []

        # Low battery
        if 5.0 < vehicle.battery_pct <= 20.0:
            alerts.append({
                "vehicle_id": vehicle.id,
                "alert_type": "low_battery",
                "severity": "warning",
                "message": f"{vehicle.callsign} battery at {vehicle.battery_pct:.0f}%",
            })

        # Critical battery
        if vehicle.battery_pct <= 5.0:
            alerts.append({
                "vehicle_id": vehicle.id,
                "alert_type": "battery_critical",
                "severity": "critical",
                "message": f"{vehicle.callsign} battery CRITICAL ({vehicle.battery_pct:.0f}%)",
            })

        return alerts

    def check_conflicts(self, vehicles: list[Vehicle]) -> list[dict]:
        """Check for assets that are dangerously close to each other."""
        alerts = []
        for i, v1 in enumerate(vehicles):
            for v2 in vehicles[i + 1:]:
                dx = v1.x - v2.x
                dy = v1.y - v2.y
                dist = (dx * dx + dy * dy) ** 0.5
                if dist < self.conflict_radius:
                    alerts.append({
                        "vehicle_id": v1.id,
                        "alert_type": "conflict_warning",
                        "severity": "warning",
                        "message": (
                            f"{v1.callsign} and {v2.callsign} within "
                            f"{dist:.0f}m — collision risk"
                        ),
                    })
        return alerts
