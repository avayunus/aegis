"""AEGIS configuration — loaded from environment variables and .env file."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings.

    Values are read from environment variables or a .env file in the backend/ directory.
    """

    # ── App ──────────────────────────────────────────
    app_name: str = "AEGIS"
    app_version: str = "0.1.0"
    debug: bool = True

    # ── Server ───────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000

    # ── Database ─────────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///./aegis.db"

    # ── Simulation ───────────────────────────────────
    sim_tick_rate_hz: float = 2.0  # Simulation updates per second
    sim_world_width: float = 1000.0  # World width in meters
    sim_world_height: float = 1000.0  # World height in meters

    # ── OpenClaw (added in Phase 3) ──────────────────
    openclaw_gateway_url: str = "ws://127.0.0.1:18789"
    openclaw_enabled: bool = False

    model_config = {"env_file": ".env", "env_prefix": "AEGIS_"}


settings = Settings()
