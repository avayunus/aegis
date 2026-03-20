"""AEGIS — Main FastAPI application.

This is the entrypoint for the backend service. It wires together:
- REST API routes (missions, assets, commands, health)
- WebSocket endpoints (telemetry stream)
- Simulation engine lifecycle
- Database initialization
- Scenario loading from JSON files
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aegis.api.router import api_router
from aegis.config import settings
from aegis.simulation.engine import SimulationEngine

# ── Simulation engine (singleton) ───────────────────────
sim_engine = SimulationEngine()

# Register in shared state so all modules access the same instance
from aegis.state import set_engine
set_engine(sim_engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown of long-running services."""
    # Startup
    print(f"[AEGIS] Starting {settings.app_name} v{settings.app_version}")
    print(f"[AEGIS] Simulation tick rate: {settings.sim_tick_rate_hz} Hz")
    print(f"[AEGIS] Database: {settings.database_url}")

    # Initialize the database tables
    from aegis.models import init_db
    await init_db()

    # Load default scenario from JSON
    from aegis.simulation.scenarios import load_default_scenario
    meta = load_default_scenario(sim_engine)
    sim_engine.mission_id = meta["id"]
    sim_engine.mission_name = meta["name"]

    # Start the simulation loop
    await sim_engine.start()
    print("[AEGIS] Simulation engine started")
    print(f"[AEGIS] Mission: {meta['name']} ({meta['asset_count']} assets)")

    yield  # App is running

    # Shutdown
    await sim_engine.stop()
    print("[AEGIS] Simulation engine stopped")
    print("[AEGIS] Shutdown complete")


# ── FastAPI app ─────────────────────────────────────────
app = FastAPI(
    title="AEGIS Mission Control API",
    description="Backend API for the Autonomous Engine for Guided Intelligence & Supervision",
    version=settings.app_version,
    lifespan=lifespan,
)

# ── CORS (allow frontend dev server) ────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount all API routes ────────────────────────────────
app.include_router(api_router, prefix="/api")


# ── Expose sim engine for dependency injection ──────────
def get_sim_engine() -> SimulationEngine:
    """FastAPI dependency: returns the running simulation engine."""
    return sim_engine
