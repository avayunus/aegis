"""Mission endpoints — CRUD operations for missions."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_missions():
    """Return all missions (active and completed)."""
    # TODO: Phase 1 — query from database
    return {
        "missions": [
            {
                "id": "mission-001",
                "name": "Alpha Sweep",
                "status": "active",
                "type": "search_and_rescue",
                "created_at": "2026-03-20T10:00:00Z",
                "asset_count": 3,
            }
        ]
    }


@router.get("/{mission_id}")
async def get_mission(mission_id: str):
    """Return detailed state for a single mission."""
    # TODO: Phase 1 — query from database + simulation state
    return {
        "id": mission_id,
        "name": "Alpha Sweep",
        "status": "active",
        "type": "search_and_rescue",
        "assets": [],
        "waypoints": [],
        "events": [],
        "progress_pct": 0.0,
    }


@router.post("/")
async def create_mission(name: str = "Untitled Mission", mission_type: str = "patrol"):
    """Create a new mission and initialize simulation assets."""
    # TODO: Phase 1 — create in DB, spawn in simulation
    return {
        "id": "mission-002",
        "name": name,
        "status": "planning",
        "type": mission_type,
    }
