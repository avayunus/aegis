"""Tool schemas for Claude function calling.

These are the tools the AI agent can invoke. Each tool maps to
a real action in the simulation engine. The policy engine checks
every tool call before execution.
"""

# Claude API tool format
TOOL_SCHEMAS = [
    {
        "name": "query_asset_status",
        "description": "Get the current detailed status of a specific asset by callsign. Returns position, battery, speed, heading, status, and waypoint progress.",
        "input_schema": {
            "type": "object",
            "properties": {
                "callsign": {
                    "type": "string",
                    "description": "The callsign of the asset, e.g. 'HAWK-1', 'BADGER-1'"
                }
            },
            "required": ["callsign"]
        },
    },
    {
        "name": "command_rtb",
        "description": "Command a specific asset to return to its base/home position. This is a HIGH-RISK action that should only be used when necessary (low battery, mission complete, operator request).",
        "input_schema": {
            "type": "object",
            "properties": {
                "callsign": {
                    "type": "string",
                    "description": "The callsign of the asset to recall"
                },
                "reason": {
                    "type": "string",
                    "description": "Brief justification for the RTB command"
                }
            },
            "required": ["callsign", "reason"]
        },
    },
    {
        "name": "command_rtb_all",
        "description": "Command ALL assets to return to base immediately. This is a CRITICAL action — only use for mission abort or emergency situations.",
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {
                    "type": "string",
                    "description": "Justification for recalling all assets"
                }
            },
            "required": ["reason"]
        },
    },
    {
        "name": "hold_position",
        "description": "Command an asset to stop moving and hold/loiter at its current position. Useful for investigation, waiting for instructions, or conserving battery.",
        "input_schema": {
            "type": "object",
            "properties": {
                "callsign": {
                    "type": "string",
                    "description": "The callsign of the asset to hold"
                },
                "reason": {
                    "type": "string",
                    "description": "Why the asset should hold position"
                }
            },
            "required": ["callsign"]
        },
    },
    {
        "name": "generate_sitrep",
        "description": "Generate a situation report (SITREP) summarizing the current mission state, asset positions, battery levels, alerts, and recommendations.",
        "input_schema": {
            "type": "object",
            "properties": {},
        },
    },
]

# Map tool names to risk levels for policy engine
TOOL_RISK_MAP = {
    "query_asset_status": "low",
    "generate_sitrep": "low",
    "hold_position": "medium",
    "command_rtb": "high",
    "command_rtb_all": "high",
}
