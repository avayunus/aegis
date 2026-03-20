"""Main API router — aggregates all endpoint modules."""

from fastapi import APIRouter

from aegis.api.health import router as health_router
from aegis.api.missions import router as missions_router
from aegis.api.assets import router as assets_router
from aegis.api.commands import router as commands_router
from aegis.api.telemetry import router as telemetry_router

api_router = APIRouter()

api_router.include_router(health_router, tags=["health"])
api_router.include_router(missions_router, prefix="/missions", tags=["missions"])
api_router.include_router(assets_router, prefix="/assets", tags=["assets"])
api_router.include_router(commands_router, prefix="/commands", tags=["commands"])
api_router.include_router(telemetry_router, prefix="/telemetry", tags=["telemetry"])
