"""Telemetry service — manages telemetry data pipeline."""


class TelemetryService:
    """Records and retrieves telemetry snapshots for replay."""

    async def record_snapshot(self, mission_id: str, state: dict) -> None:
        """Record a telemetry snapshot for later replay."""
        # TODO Phase 5: Write to telemetry_snapshots table
        pass

    async def get_replay_frames(
        self, mission_id: str, start_tick: int = 0, end_tick: int | None = None
    ) -> list[dict]:
        """Retrieve recorded frames for mission replay."""
        # TODO Phase 5: Query from telemetry_snapshots
        return []
