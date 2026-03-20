"""Risk classifier — NL-based command risk scoring. Phase 4.

In Phase 4 this will use pattern matching and optional ML to classify
free-text operator commands before they even reach the agent.
For now, risk is determined by the tool_name in rules.py.
"""


def classify_command_text(text: str) -> str:
    """Quick heuristic risk check on raw operator text.

    Returns "low", "medium", "high", or "blocked".
    """
    text_lower = text.lower()

    # Blocked patterns
    blocked_keywords = ["disable", "destroy", "override safety", "delete logs"]
    if any(kw in text_lower for kw in blocked_keywords):
        return "blocked"

    # High risk patterns
    high_keywords = ["return to base", "rtb", "abort", "emergency", "all assets"]
    if any(kw in text_lower for kw in high_keywords):
        return "high"

    # Medium risk patterns
    medium_keywords = ["reroute", "assign", "change waypoint", "redirect", "set speed"]
    if any(kw in text_lower for kw in medium_keywords):
        return "medium"

    return "low"
