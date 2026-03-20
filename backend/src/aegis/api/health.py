"""Health check endpoint — verifies the backend is alive and simulation is running."""

from fastapi import APIRouter

from aegis.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Return system health status.

    Used by monitoring, the frontend connection indicator, and Docker health checks.
    """
    return {
        "status": "operational",
        "service": settings.app_name,
        "version": settings.app_version,
        "simulation": {
            "tick_rate_hz": settings.sim_tick_rate_hz,
            "world_size": [settings.sim_world_width, settings.sim_world_height],
        },
    }
