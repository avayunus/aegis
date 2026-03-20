"""Asset endpoints — query and control individual vehicles/drones."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_assets():
    """Return all assets across all active missions."""
    # TODO: Phase 1 — pull from simulation engine state
    return {
        "assets": [
            {
                "id": "drone-01",
                "type": "quadrotor",
                "callsign": "HAWK-1",
                "status": "en_route",
                "battery_pct": 82.0,
                "position": {"x": 234.5, "y": 561.2},
                "heading_deg": 45.0,
                "speed_mps": 12.3,
                "mission_id": "mission-001",
            }
        ]
    }


@router.get("/{asset_id}")
async def get_asset(asset_id: str):
    """Return full telemetry snapshot for a single asset."""
    # TODO: Phase 1 — pull from simulation engine
    return {
        "id": asset_id,
        "type": "quadrotor",
        "callsign": "HAWK-1",
        "status": "en_route",
        "battery_pct": 82.0,
        "position": {"x": 234.5, "y": 561.2},
        "heading_deg": 45.0,
        "speed_mps": 12.3,
        "mission_id": "mission-001",
        "waypoints_completed": 2,
        "waypoints_total": 6,
        "last_updated": "2026-03-20T10:05:00Z",
    }
