"""Policy rules — risk classification and deny-list definitions.

These rules are the core of AEGIS's safety model. They determine
what the AI agent and operator can do without approval.
"""

# Tools that are always blocked, no matter what
DENY_LIST = {
    "disable_safety",
    "disable_monitoring",
    "disable_alerts",
    "destroy_asset",
    "override_policy",
    "raw_command",
    "delete_audit_log",
    "modify_audit_log",
}

# Risk classification by tool name prefix
RISK_MAP = {
    "query_": "low",
    "get_": "low",
    "list_": "low",
    "generate_": "low",
    "summary_": "low",
    "assign_": "medium",
    "reroute_": "medium",
    "set_speed_": "medium",
    "set_altitude_": "medium",
    "command_rtb": "high",
    "command_rtb_all": "high",
    "abort_mission": "high",
    "emergency_": "high",
}


def classify_risk(tool_name: str) -> str:
    """Classify a tool call's risk level.

    Args:
        tool_name: The name of the tool being invoked.

    Returns:
        Risk level: "low", "medium", "high", or "unknown".
    """
    # Exact match first
    if tool_name in RISK_MAP:
        return RISK_MAP[tool_name]

    # Prefix match
    for prefix, level in RISK_MAP.items():
        if tool_name.startswith(prefix):
            return level

    return "unknown"


def is_blocked(tool_name: str) -> bool:
    """Check if a tool is on the deny-list.

    Blocked tools can never be executed, regardless of who requests them.
    """
    return tool_name in DENY_LIST
