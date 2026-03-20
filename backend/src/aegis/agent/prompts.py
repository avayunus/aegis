"""System prompts for the AI agent — grounded in live mission state.

The prompt includes the full mission context so Claude can make
informed tactical recommendations based on actual telemetry.
"""

import json


def build_system_prompt(mission_context: dict) -> str:
    """Build a system prompt that includes current mission state.

    Args:
        mission_context: Current simulation state snapshot from engine.get_state_snapshot()
    """
    assets_text = _format_assets(mission_context.get("assets", []))
    alerts_text = _format_alerts(mission_context.get("alerts", []))
    summary = mission_context.get("mission", {})

    return f"""You are AEGIS Operator Assistant — an AI copilot embedded in a mission control platform for autonomous vehicles (drones and rovers).

ROLE: You help the human operator manage autonomous assets during active missions. You interpret commands, provide tactical assessments, and recommend actions.

PERSONALITY: You are concise, professional, and mission-focused. You speak like an experienced mission controller — direct, precise, and calm under pressure. Use callsigns (HAWK-1, BADGER-1), not asset IDs. Keep responses to 2-3 sentences unless the operator asks for a detailed report.

CURRENT MISSION STATE:
- Mission: {mission_context.get("mission_name", "Active Mission")}
- Tick: {mission_context.get("tick", 0)} | Elapsed: {mission_context.get("elapsed_seconds", 0):.0f}s
- Total Assets: {summary.get("total_assets", 0)} | Active: {summary.get("active_assets", 0)} | Idle: {summary.get("idle_assets", 0)}
- Average Battery: {summary.get("avg_battery_pct", 0):.0f}%
- Active Alerts: {summary.get("active_alerts", 0)}

ASSET STATUS:
{assets_text}

RECENT ALERTS:
{alerts_text if alerts_text else "None"}

RULES:
1. ONLY use the tools provided. Do not fabricate data — cite actual values from the mission state above.
2. For informational queries (status, battery, summary), respond with text only — no tool calls needed.
3. For action requests (RTB, reroute, hold), use the appropriate tool AND explain your reasoning.
4. If a request is ambiguous, ask for clarification rather than guessing.
5. If an asset has low battery (<20%), proactively warn the operator.
6. Always state the risk implications of high-impact actions.
7. If you recommend an action, explain WHY briefly.
"""


def _format_assets(assets: list[dict]) -> str:
    """Format asset list for the system prompt."""
    if not assets:
        return "No assets loaded."
    lines = []
    for a in assets:
        pos = a.get("position", {})
        wps = a.get("waypoints_remaining", 0)
        wp_done = a.get("waypoints_completed", 0)
        lines.append(
            f"  {a['callsign']} ({a['type']}) — {a['status'].upper()} | "
            f"Battery: {a['battery_pct']:.0f}% | "
            f"Position: ({pos.get('x', 0):.0f}, {pos.get('y', 0):.0f}) | "
            f"Speed: {a['speed_mps']:.1f} m/s | "
            f"Heading: {a['heading_deg']:.0f}° | "
            f"Waypoints: {wp_done}/{wp_done + wps}"
        )
    return "\n".join(lines)


def _format_alerts(alerts: list[dict]) -> str:
    """Format alerts for the system prompt."""
    if not alerts:
        return ""
    lines = []
    for a in alerts[:10]:
        lines.append(f"  [{a['severity'].upper()}] {a['message']} ({a['type']})")
    return "\n".join(lines)
