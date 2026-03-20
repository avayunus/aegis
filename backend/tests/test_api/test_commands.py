"""Tests for the command interpreter (Phase 1 pattern matching)."""

import pytest
from httpx import ASGITransport, AsyncClient
from aegis.main import app


@pytest.fixture
async def client():
    # Load a scenario so the sim engine has vehicles
    from aegis.main import sim_engine
    from aegis.simulation.scenarios import load_default_scenario
    from aegis.state import set_engine
    sim_engine.reset()
    load_default_scenario(sim_engine)
    set_engine(sim_engine)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_status_command(client):
    """'status of HAWK-1' should return asset status."""
    r = await client.post("/api/commands/", json={"text": "status of HAWK-1"})
    assert r.status_code == 200
    data = r.json()
    assert data["risk_level"] == "low"
    assert data["status"] == "executed"
    assert "HAWK-1" in data["result_summary"]


@pytest.mark.asyncio
async def test_mission_summary_command(client):
    """'mission summary' should return mission overview."""
    r = await client.post("/api/commands/", json={"text": "mission summary"})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "executed"
    assert "active" in data["result_summary"].lower() or "Assets" in data["result_summary"]


@pytest.mark.asyncio
async def test_battery_command(client):
    """'battery report' should return battery info."""
    r = await client.post("/api/commands/", json={"text": "battery report"})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "executed"
    assert "%" in data["result_summary"]


@pytest.mark.asyncio
async def test_rtb_all_requires_approval(client):
    """'return all to base' should be high-risk and need approval."""
    r = await client.post("/api/commands/", json={"text": "return all assets to base"})
    assert r.status_code == 200
    data = r.json()
    assert data["risk_level"] == "high"
    assert data["requires_approval"] is True


@pytest.mark.asyncio
async def test_blocked_command(client):
    """'disable safety' should be blocked by policy."""
    r = await client.post("/api/commands/", json={"text": "disable safety monitoring"})
    assert r.status_code == 200
    data = r.json()
    assert data["risk_level"] == "blocked"
    assert data["status"] == "blocked"


@pytest.mark.asyncio
async def test_unknown_command(client):
    """Gibberish should return a helpful error."""
    r = await client.post("/api/commands/", json={"text": "xyzzy plugh"})
    assert r.status_code == 200
    data = r.json()
    assert "not recognized" in data["result_summary"].lower() or "unknown" in data["interpreted_intent"].lower()
