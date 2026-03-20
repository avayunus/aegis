"""Asset endpoints — returns LIVE data from the simulation engine.

Phase 1: no more stubs. Every response comes from actual simulation state.
"""

from fastapi import APIRouter

router = APIRouter()


def _get_engine():

    from aegis.state import get_engine
    return get_engine()


@router.get("/")
async def list_assets():
    """Return all assets with their current live state."""
    engine = _get_engine()
    vehicles = engine.get_all_vehicles()
    return {
        "count": len(vehicles),
        "assets": [v.to_dict() for v in vehicles],
    }


@router.get("/{asset_id}")
async def get_asset(asset_id: str):
    """Return detailed live telemetry for a single asset."""
    engine = _get_engine()
    v = engine.get_vehicle(asset_id)
    if not v:
        # Try by callsign
        v = engine.find_vehicle_by_callsign(asset_id)
    if not v:
        return {"error": f"Asset '{asset_id}' not found"}, 404

    data = v.to_dict()
    # Add extra detail for single-asset view
    data["home"] = {"x": v.home_x, "y": v.home_y}
    data["max_speed_mps"] = v.max_speed_mps
    data["battery_drain_rate"] = v.battery_drain_rate
    return data


@router.post("/{asset_id}/rtb")
async def command_asset_rtb(asset_id: str):
    """Command a specific asset to return to base."""
    engine = _get_engine()
    result = engine.exec_rtb(asset_id)
    return result


@router.post("/{asset_id}/hold")
async def command_asset_hold(asset_id: str):
    """Command a specific asset to hold position."""
    engine = _get_engine()
    result = engine.exec_hold_position(asset_id)
    return result
