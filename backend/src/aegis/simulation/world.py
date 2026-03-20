"""World State — the complete state of the simulated environment.

Holds all vehicles, alerts, and mission metadata. The SimulationEngine
mutates this state every tick, and the telemetry WebSocket reads from it.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone

from aegis.simulation.vehicle import Vehicle


@dataclass
class Alert:
    """An event surfaced to the operator."""

    id: str
    vehicle_id: str
    alert_type: str
    severity: str  # "info" | "warning" | "critical"
    message: str
    timestamp: str
    acknowledged: bool = False


@dataclass
class WorldState:
    """Complete state of the simulated world."""

    width: float
    height: float
    vehicles: dict[str, Vehicle] = field(default_factory=dict)
    alerts: list[Alert] = field(default_factory=list)
    _alert_counter: int = field(default=0, repr=False)

    def add_alert(
        self,
        vehicle_id: str,
        alert_type: str,
        severity: str,
        message: str,
    ) -> Alert:
        """Create and store an alert.

        Deduplicates: won't create the same alert_type for the same vehicle
        if one already exists within the last 30 seconds.
        """
        # Simple deduplication
        now = datetime.now(timezone.utc)
        for existing in reversed(self.alerts[-20:]):
            if (
                existing.vehicle_id == vehicle_id
                and existing.alert_type == alert_type
                and not existing.acknowledged
            ):
                return existing  # Already have this alert active

        self._alert_counter += 1
        alert = Alert(
            id=f"alert-{self._alert_counter:04d}",
            vehicle_id=vehicle_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            timestamp=now.isoformat(),
        )
        self.alerts.append(alert)
        return alert

    def get_recent_alerts(self, limit: int = 20) -> list[dict]:
        """Return the most recent alerts as serializable dicts."""
        recent = self.alerts[-limit:] if self.alerts else []
        return [
            {
                "id": a.id,
                "vehicle_id": a.vehicle_id,
                "type": a.alert_type,
                "severity": a.severity,
                "message": a.message,
                "timestamp": a.timestamp,
                "acknowledged": a.acknowledged,
            }
            for a in reversed(recent)
        ]

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Mark an alert as acknowledged by the operator."""
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                return True
        return False

    def get_mission_summary(self) -> dict:
        """Return a high-level summary of current mission state."""
        total = len(self.vehicles)
        active = sum(
            1
            for v in self.vehicles.values()
            if v.status.value in ("en_route", "loitering", "rtb")
        )
        idle = sum(1 for v in self.vehicles.values() if v.status.value == "idle")
        alerts_active = sum(1 for a in self.alerts if not a.acknowledged)

        avg_battery = 0.0
        if total > 0:
            avg_battery = sum(v.battery_pct for v in self.vehicles.values()) / total

        return {
            "total_assets": total,
            "active_assets": active,
            "idle_assets": idle,
            "avg_battery_pct": round(avg_battery, 1),
            "active_alerts": alerts_active,
        }
