"""Asset service — business logic for autonomous vehicles."""


class AssetService:
    """Handles asset queries and commands."""

    async def get_asset(self, asset_id: str) -> dict | None:
        """Retrieve an asset's current state."""
        # TODO Phase 1: Query simulation engine
        pass

    async def list_assets(self, mission_id: str | None = None) -> list[dict]:
        """List all assets, optionally filtered by mission."""
        # TODO Phase 1: Query simulation engine
        return []
