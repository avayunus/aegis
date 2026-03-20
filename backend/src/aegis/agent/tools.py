"""Tool definitions for the OpenClaw agent — Phase 3.

Each tool is a function the AI agent can invoke. Tools are the
boundary between "AI reasoning" and "system execution." Every tool
call goes through the policy engine before running.

Tool categories:
  - query_*    : Read-only data retrieval (low risk)
  - assign_*   : State changes to assets (medium risk)
  - command_*  : Mission-level commands (high risk)
  - generate_* : Report/summary generation (low risk)
"""

# Tool definitions will be structured as OpenClaw-compatible
# tool schemas when Phase 3 is implemented.

TOOL_DEFINITIONS = [
    {
        "name": "query_asset_status",
        "description": "Get the current status of a specific asset or all assets",
        "risk_level": "low",
        "parameters": {
            "asset_id": {"type": "string", "description": "Asset ID, or 'all'"},
        },
    },
    {
        "name": "query_mission_progress",
        "description": "Get overall mission progress and statistics",
        "risk_level": "low",
        "parameters": {},
    },
    {
        "name": "assign_waypoints",
        "description": "Assign new waypoints to a specific asset",
        "risk_level": "medium",
        "parameters": {
            "asset_id": {"type": "string"},
            "waypoints": {"type": "array", "items": {"type": "object"}},
        },
    },
    {
        "name": "command_rtb",
        "description": "Command an asset to return to base",
        "risk_level": "high",
        "parameters": {
            "asset_id": {"type": "string"},
        },
    },
    {
        "name": "command_rtb_all",
        "description": "Command ALL assets to return to base immediately",
        "risk_level": "high",
        "parameters": {},
    },
    {
        "name": "generate_mission_summary",
        "description": "Generate a text summary of current mission state",
        "risk_level": "low",
        "parameters": {},
    },
    {
        "name": "generate_asset_report",
        "description": "Generate a detailed report for a specific asset",
        "risk_level": "low",
        "parameters": {
            "asset_id": {"type": "string"},
        },
    },
]
