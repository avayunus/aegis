"""Event handlers — respond to detected anomalies. Phase 6.

When the anomaly detector surfaces an event, handlers determine
what system actions to take (e.g., auto-RTB on critical battery,
notify operator, log to audit trail).
"""


async def handle_low_battery(vehicle_id: str, battery_pct: float) -> None:
    """Handle a low-battery alert."""
    # TODO Phase 6: Log to audit trail, surface in UI
    pass


async def handle_battery_critical(vehicle_id: str, battery_pct: float) -> None:
    """Handle a critical battery — may trigger auto-RTB."""
    # TODO Phase 6: Auto-RTB if policy allows, log decision
    pass


async def handle_conflict_warning(vehicle_id_1: str, vehicle_id_2: str, distance: float) -> None:
    """Handle two assets in dangerously close proximity."""
    # TODO Phase 6: Alert operator, suggest reroute
    pass
