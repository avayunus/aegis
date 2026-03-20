"""Command endpoints — operator submits natural-language commands here.

Flow:
1. Operator types a command in the console UI
2. POST /api/commands/ receives it
3. Backend classifies risk level via the policy engine
4. Low-risk: auto-execute via OpenClaw tools
5. Medium-risk: queue for confirmation
6. High-risk: require explicit operator approval
7. All commands are logged to the audit trail
"""

from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class CommandRequest(BaseModel):
    """Payload from the operator console."""

    text: str  # Natural-language command
    mission_id: str | None = None  # Optional: scope to a specific mission


class CommandResponse(BaseModel):
    """Response after command is processed or queued."""

    command_id: str
    text: str
    risk_level: str  # "low" | "medium" | "high"
    status: str  # "executed" | "pending_approval" | "blocked"
    interpretation: str  # What the AI understood
    actions: list[dict]  # Actions taken or proposed
    timestamp: str


@router.post("/", response_model=CommandResponse)
async def submit_command(req: CommandRequest):
    """Accept an operator command, classify it, and route it.

    This is the main integration point for the operator console.
    In Phase 3, this will call OpenClaw for interpretation and tool selection.
    In Phase 4, this will pass through the policy engine before execution.
    """
    now = datetime.now(timezone.utc).isoformat()

    # TODO Phase 3: send req.text to OpenClaw for interpretation
    # TODO Phase 4: run policy engine classification

    # Stub response — simulates a low-risk informational query
    return CommandResponse(
        command_id="cmd-001",
        text=req.text,
        risk_level="low",
        status="executed",
        interpretation=f"Operator requested: {req.text}",
        actions=[
            {
                "tool": "query_asset_status",
                "params": {"scope": "all"},
                "result": "3 assets active, all nominal",
            }
        ],
        timestamp=now,
    )


@router.get("/history")
async def command_history(mission_id: str | None = None, limit: int = 50):
    """Return recent command history for audit review."""
    # TODO Phase 1: query from audit log database
    return {
        "commands": [],
        "total": 0,
        "limit": limit,
    }


@router.post("/{command_id}/approve")
async def approve_command(command_id: str):
    """Operator approves a pending high-risk command."""
    # TODO Phase 4: execute the queued action after approval
    return {
        "command_id": command_id,
        "status": "approved",
        "message": "Command approved and executing",
    }


@router.post("/{command_id}/reject")
async def reject_command(command_id: str):
    """Operator rejects a pending command."""
    # TODO Phase 4: mark command as rejected in audit log
    return {
        "command_id": command_id,
        "status": "rejected",
        "message": "Command rejected by operator",
    }
