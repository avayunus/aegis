"""Mission service — business logic for mission lifecycle."""


class MissionService:
    """Handles mission creation, state transitions, and queries."""

    async def create_mission(self, name: str, mission_type: str) -> dict:
        """Create a new mission and persist to database."""
        # TODO Phase 1: Write to missions table
        pass

    async def get_mission(self, mission_id: str) -> dict | None:
        """Retrieve a mission by ID."""
        # TODO Phase 1: Query from database
        pass

    async def list_missions(self) -> list[dict]:
        """List all missions."""
        # TODO Phase 1: Query from database
        return []
