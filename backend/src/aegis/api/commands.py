"""Command endpoints — AI-powered operator command processing.

Flow:
1. Operator types command
2. If AI agent is enabled (API key set): Claude interprets with full mission context
3. If AI returns tool calls: execute them through policy engine
4. If AI is not enabled: fall back to pattern matching
5. All commands and responses are logged
"""

import re
from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

from aegis.policy.classifier import classify_command_text
from aegis.agent.orchestrator import AgentOrchestrator

router = APIRouter()

_command_log: list[dict] = []
_cmd_counter = 0
_pending_approvals: dict[str, dict] = {}
_agent = AgentOrchestrator()


def _get_engine():
    from aegis.state import get_engine
    return get_engine()


class CommandRequest(BaseModel):
    text: str
    mission_id: str | None = None


@router.post("/")
async def submit_command(req: CommandRequest):
    """Accept an operator command, interpret via AI or pattern matching, and execute."""
    global _cmd_counter
    _cmd_counter += 1
    cmd_id = f"cmd-{_cmd_counter:04d}"
    now = datetime.now(timezone.utc).isoformat()
    engine = _get_engine()
    text = req.text.strip()

    # ── Step 1: Policy pre-check on raw text ─────
    text_risk = classify_command_text(text)
    if text_risk == "blocked":
        entry = _log_command(cmd_id, text, "blocked", "blocked",
                             "Command blocked by policy engine", [], now)
        return entry

    # ── Step 2: AI interpretation (or fallback) ──
    if _agent.enabled:
        # Get full mission context for the AI
        context = engine.get_state_snapshot()
        ai_result = await _agent.interpret(text, context)

        if ai_result.get("fallback"):
            # AI failed, use pattern matching
            return await _process_with_patterns(cmd_id, text, now, engine)

        return await _process_ai_result(cmd_id, text, now, engine, ai_result)
    else:
        return await _process_with_patterns(cmd_id, text, now, engine)


async def _process_ai_result(cmd_id, text, now, engine, ai_result) -> dict:
    """Process the AI agent's interpretation and tool calls."""
    response_text = ai_result.get("response", "")
    actions = ai_result.get("actions", [])
    risk = ai_result.get("risk_level", "low")

    # If high risk, queue for approval
    if risk == "high":
        _pending_approvals[cmd_id] = {
            "intent": response_text,
            "actions": actions,
            "text": text,
            "ai_response": response_text,
        }
        entry = _log_command(cmd_id, text, risk, "pending_approval",
                             response_text, [], now)
        entry["requires_approval"] = True
        entry["result_summary"] = response_text or "High-risk action requires approval"
        entry["ai_response"] = response_text
        return entry

    # Execute tool calls
    results = _execute_ai_tools(actions, engine)
    executed_msgs = [r.get("message", "") for r in results if r.get("success")]

    # Combine AI response text with execution results
    summary_parts = []
    if response_text:
        summary_parts.append(response_text)
    if executed_msgs:
        summary_parts.append("Executed: " + "; ".join(executed_msgs))

    summary = " | ".join(summary_parts) if summary_parts else "Command processed"

    entry = _log_command(cmd_id, text, risk, "executed", response_text, results, now)
    entry["result_summary"] = summary
    entry["ai_response"] = response_text
    return entry


def _execute_ai_tools(actions: list[dict], engine) -> list[dict]:
    """Execute tool calls returned by the AI agent."""
    results = []
    for action in actions:
        tool = action.get("tool", "")
        params = action.get("params", {})

        if tool == "command_rtb":
            callsign = params.get("callsign", "")
            v = engine.find_vehicle_by_callsign(callsign)
            if v:
                result = engine.exec_rtb(v.id)
                results.append(result)
            else:
                results.append({"success": False, "message": f"Asset {callsign} not found"})

        elif tool == "command_rtb_all":
            results.append(engine.exec_rtb_all())

        elif tool == "hold_position":
            callsign = params.get("callsign", "")
            v = engine.find_vehicle_by_callsign(callsign)
            if v:
                result = engine.exec_hold_position(v.id)
                results.append(result)
            else:
                results.append({"success": False, "message": f"Asset {callsign} not found"})

        elif tool == "query_asset_status":
            callsign = params.get("callsign", "")
            v = engine.find_vehicle_by_callsign(callsign)
            if v:
                results.append({
                    "success": True,
                    "message": (
                        f"{v.callsign}: {v.status.value.upper()} | "
                        f"BAT: {v.battery_pct:.0f}% | POS: ({v.x:.0f}, {v.y:.0f}) | "
                        f"SPD: {v.speed_mps:.1f} m/s | HDG: {v.heading_deg:.0f}°"
                    ),
                })

        elif tool == "generate_sitrep":
            summary = engine.world.get_mission_summary()
            vehicles = engine.get_all_vehicles()
            lines = []
            for v in vehicles:
                lines.append(
                    f"{v.callsign}: {v.status.value.upper()} | BAT: {v.battery_pct:.0f}%"
                )
            results.append({
                "success": True,
                "message": (
                    f"SITREP — {summary['active_assets']}/{summary['total_assets']} active | "
                    f"Avg BAT: {summary['avg_battery_pct']:.0f}% | "
                    f"Alerts: {summary['active_alerts']} | " +
                    " | ".join(lines)
                ),
            })

    return results


# ═══════════════════════════════════════════════════════════
# PATTERN MATCHING FALLBACK (used when no API key is set)
# ═══════════════════════════════════════════════════════════

async def _process_with_patterns(cmd_id, text, now, engine) -> dict:
    """Fallback: interpret command with regex patterns."""
    text_lower = text.lower().strip()
    vehicles = engine.get_all_vehicles()
    risk = classify_command_text(text)

    intent, actions = _interpret_patterns(text_lower, engine, vehicles)

    if risk == "high":
        _pending_approvals[cmd_id] = {"intent": intent, "actions": actions, "text": text}
        entry = _log_command(cmd_id, text, risk, "pending_approval", intent, [], now)
        entry["requires_approval"] = True
        entry["result_summary"] = f"HIGH RISK — {intent}. Awaiting operator approval."
        return entry

    results = _execute_pattern_actions(actions, engine)
    summary = "; ".join(r.get("message", "") for r in results) if results else intent

    entry = _log_command(cmd_id, text, risk, "executed", intent, results, now)
    entry["result_summary"] = summary
    return entry


def _interpret_patterns(text_lower, engine, vehicles):
    """Pattern-matching command interpreter (fallback)."""
    # Status queries
    if any(kw in text_lower for kw in ["status", "how are", "what is", "show me", "report"]):
        for v in vehicles:
            if v.callsign.lower() in text_lower or v.id in text_lower:
                return (f"Status query for {v.callsign}", [{"action": "query_status", "vehicle_id": v.id}])
        return ("Mission status query", [{"action": "query_mission"}])

    # RTB single
    rtb_match = re.search(r"(?:return|send|rtb|recall)\s+(\S+)\s+(?:to\s+)?(?:base|home|rtb)", text_lower)
    if rtb_match:
        cs = rtb_match.group(1).upper()
        v = engine.find_vehicle_by_callsign(cs)
        if v:
            return (f"Return {v.callsign} to base", [{"action": "rtb", "vehicle_id": v.id}])

    # RTB all
    if any(kw in text_lower for kw in ["return all", "rtb all", "recall all", "all back", "everyone back"]):
        return ("Return ALL assets to base", [{"action": "rtb_all"}])

    # Hold
    hold_match = re.search(r"(?:hold|stop|halt|freeze|loiter)\s+(\S+)", text_lower)
    if hold_match:
        cs = hold_match.group(1).upper()
        v = engine.find_vehicle_by_callsign(cs)
        if v:
            return (f"Hold {v.callsign}", [{"action": "hold", "vehicle_id": v.id}])

    # Pause/resume
    if any(kw in text_lower for kw in ["pause sim", "pause mission"]):
        return ("Pause simulation", [{"action": "pause"}])
    if any(kw in text_lower for kw in ["resume sim", "resume mission", "unpause"]):
        return ("Resume simulation", [{"action": "resume"}])

    # Battery
    if "battery" in text_lower or "power" in text_lower:
        for v in vehicles:
            if v.callsign.lower() in text_lower:
                return (f"Battery query for {v.callsign}", [{"action": "query_battery", "vehicle_id": v.id}])
        return ("Battery report", [{"action": "query_all_battery"}])

    # Summary
    if any(kw in text_lower for kw in ["summary", "overview", "sitrep", "brief"]):
        return ("Mission summary", [{"action": "query_mission"}])

    return (f"Unrecognized command: {text_lower}", [{"action": "unknown", "raw_text": text_lower}])


def _execute_pattern_actions(actions, engine):
    """Execute pattern-matched actions."""
    results = []
    for action in actions:
        act = action.get("action", "")
        if act == "rtb":
            results.append(engine.exec_rtb(action["vehicle_id"]))
        elif act == "rtb_all":
            results.append(engine.exec_rtb_all())
        elif act == "hold":
            results.append(engine.exec_hold_position(action["vehicle_id"]))
        elif act == "pause":
            engine.pause()
            results.append({"success": True, "message": "Simulation paused"})
        elif act == "resume":
            engine.resume()
            results.append({"success": True, "message": "Simulation resumed"})
        elif act == "query_status":
            v = engine.get_vehicle(action["vehicle_id"])
            if v:
                results.append({"success": True, "message": (
                    f"{v.callsign}: {v.status.value.upper()} | BAT: {v.battery_pct:.0f}% | "
                    f"POS: ({v.x:.0f}, {v.y:.0f}) | SPD: {v.speed_mps:.1f} m/s | HDG: {v.heading_deg:.0f}°"
                )})
        elif act == "query_battery":
            v = engine.get_vehicle(action["vehicle_id"])
            if v:
                results.append({"success": True, "message": f"{v.callsign} battery: {v.battery_pct:.1f}%"})
        elif act == "query_all_battery":
            lines = [f"{v.callsign}: {v.battery_pct:.0f}%" for v in engine.get_all_vehicles()]
            results.append({"success": True, "message": "Battery: " + " | ".join(lines)})
        elif act == "query_mission":
            s = engine.world.get_mission_summary()
            active = [v.callsign for v in engine.get_all_vehicles() if v.status.value in ("en_route", "loitering", "rtb")]
            results.append({"success": True, "message": (
                f"Mission: {engine.mission_name or 'Active'} | "
                f"Assets: {s['active_assets']}/{s['total_assets']} active | "
                f"Avg BAT: {s['avg_battery_pct']:.0f}% | Alerts: {s['active_alerts']} | "
                f"Active: {', '.join(active) or 'none'}"
            )})
        elif act == "unknown":
            results.append({"success": False, "message": (
                "Command not recognized. Try: 'status of HAWK-1', 'return HAWK-2 to base', "
                "'hold HAWK-3', 'battery report', 'mission summary'"
            )})
    return results


# ═══════════════════════════════════════════════════════════
# APPROVAL & HISTORY
# ═══════════════════════════════════════════════════════════

@router.get("/history")
async def command_history(limit: int = 50):
    return {"commands": _command_log[-limit:][::-1], "total": len(_command_log)}


@router.get("/pending")
async def pending_approvals():
    return {"pending": list(_pending_approvals.keys())}


@router.post("/{command_id}/approve")
async def approve_command(command_id: str):
    if command_id not in _pending_approvals:
        return {"error": f"No pending command {command_id}"}
    pending = _pending_approvals.pop(command_id)
    engine = _get_engine()

    # Check if AI actions or pattern actions
    if any("tool" in a for a in pending.get("actions", [])):
        results = _execute_ai_tools(pending["actions"], engine)
    else:
        results = _execute_pattern_actions(pending["actions"], engine)

    summary = "; ".join(r.get("message", "") for r in results)
    for entry in _command_log:
        if entry["command_id"] == command_id:
            entry["status"] = "approved_and_executed"
            entry["result_summary"] = summary
    return {"command_id": command_id, "status": "approved_and_executed", "result_summary": summary, "actions": results}


@router.post("/{command_id}/reject")
async def reject_command(command_id: str):
    if command_id in _pending_approvals:
        _pending_approvals.pop(command_id)
    for entry in _command_log:
        if entry["command_id"] == command_id:
            entry["status"] = "rejected"
            entry["result_summary"] = "Rejected by operator"
    return {"command_id": command_id, "status": "rejected"}


def _log_command(cmd_id, text, risk, status, intent, actions, timestamp) -> dict:
    entry = {
        "command_id": cmd_id, "raw_text": text, "risk_level": risk,
        "status": status, "interpreted_intent": intent, "actions": actions,
        "result_summary": None, "requires_approval": False,
        "ai_response": None, "timestamp": timestamp,
    }
    _command_log.append(entry)
    return entry
