"""Shared application state — singleton references accessible from any module.

This avoids circular imports and uvicorn --reload issues by providing
a single place to store and retrieve the simulation engine instance.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from aegis.simulation.engine import SimulationEngine

_engine: "SimulationEngine | None" = None


def set_engine(engine: "SimulationEngine") -> None:
    """Register the simulation engine (called once at startup)."""
    global _engine
    _engine = engine


def get_engine() -> "SimulationEngine":
    """Get the simulation engine. Raises if not yet initialized."""
    if _engine is None:
        raise RuntimeError("Simulation engine not initialized")
    return _engine
