"""Mission endpoints — scenario loading, live mission state, simulation control.

Phase 1: real scenario management and simulation control endpoints.
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


def _get_engine():
    from aegis.state import get_engine
    return get_engine()


class LoadScenarioRequest(BaseModel):
    filename: str  # e.g., "search-and-rescue.json"


@router.get("/")
async def list_missions():
    """Return current mission state and available scenarios."""
    from aegis.simulation.scenarios import list_scenarios
    engine = _get_engine()

    return {
        "current_mission": {
            "id": engine.mission_id,
            "name": engine.mission_name,
            "tick": engine.tick_count,
            "paused": engine.paused,
            "elapsed_seconds": (
                round((__import__("datetime").datetime.now(__import__("datetime").timezone.utc)
                       - engine.started_at).total_seconds(), 1)
                if engine.started_at else 0
            ),
            "asset_count": len(engine.get_all_vehicles()),
            "summary": engine.world.get_mission_summary(),
        },
        "available_scenarios": list_scenarios(),
    }


@router.get("/state")
async def get_mission_state():
    """Return the full current mission state (same as WebSocket frame, but via REST)."""
    engine = _get_engine()
    return engine.get_state_snapshot()


@router.post("/load")
async def load_scenario(req: LoadScenarioRequest):
    """Load a new scenario, replacing the current mission.

    Resets the simulation, loads vehicles from the JSON file,
    and starts the clock.
    """
    from aegis.simulation.scenarios import load_scenario_from_file
    engine = _get_engine()

    # Reset simulation state
    was_running = engine.running
    engine.reset()

    try:
        meta = load_scenario_from_file(engine, req.filename)
    except FileNotFoundError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"Failed to load scenario: {e}"}

    # Update mission metadata
    engine.mission_id = meta["id"]
    engine.mission_name = meta["name"]

    # Restart if it was running
    if was_running and not engine.running:
        import datetime as dt
        engine.started_at = dt.datetime.now(dt.timezone.utc)
        engine.running = True
        import asyncio
        engine._task = asyncio.create_task(engine._loop())

    return {
        "status": "loaded",
        "mission_id": meta["id"],
        "mission_name": meta["name"],
        "asset_count": meta["asset_count"],
        "description": meta["description"],
    }


@router.post("/pause")
async def pause_simulation():
    """Pause the simulation."""
    engine = _get_engine()
    engine.pause()
    return {"status": "paused"}


@router.post("/resume")
async def resume_simulation():
    """Resume the simulation."""
    engine = _get_engine()
    engine.resume()
    return {"status": "resumed"}


@router.post("/reset")
async def reset_simulation():
    """Reset and reload the default scenario."""
    from aegis.simulation.scenarios import load_default_scenario
    engine = _get_engine()
    engine.reset()
    meta = load_default_scenario(engine)
    engine.mission_id = meta["id"]
    engine.mission_name = meta["name"]
    import datetime as dt
    engine.started_at = dt.datetime.now(dt.timezone.utc)
    engine.running = True
    import asyncio
    engine._task = asyncio.create_task(engine._loop())
    return {"status": "reset", "mission": meta}
