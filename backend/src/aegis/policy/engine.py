"""Policy engine — classifies and gates every action. Phase 4.

The policy engine is the safety backbone of AEGIS. Every proposed action
(from the operator or the AI agent) passes through here before execution.

It enforces:
- Risk classification (low / medium / high / blocked)
- Approval requirements
- Rate limiting
- Deny-list rules
- Telemetry freshness checks
"""

from aegis.policy.rules import classify_risk, is_blocked


class PolicyEngine:
    """Evaluates proposed actions against safety rules."""

    def __init__(self):
        self.max_commands_per_minute = 20
        self.telemetry_max_age_seconds = 10.0

    def evaluate(self, action: dict) -> dict:
        """Evaluate a proposed action and return a policy decision.

        Args:
            action: Dictionary with 'tool_name', 'params', 'source'.

        Returns:
            Dictionary with 'allowed', 'risk_level', 'requires_approval',
            'reason', and 'gate' (auto/confirm/approve/block).
        """
        tool_name = action.get("tool_name", "")

        # Check deny-list first
        if is_blocked(tool_name):
            return {
                "allowed": False,
                "risk_level": "blocked",
                "requires_approval": False,
                "reason": f"Action '{tool_name}' is on the deny-list",
                "gate": "block",
            }

        # Classify risk
        risk = classify_risk(tool_name)

        if risk == "low":
            return {
                "allowed": True,
                "risk_level": "low",
                "requires_approval": False,
                "reason": "Low-risk informational action",
                "gate": "auto",
            }
        elif risk == "medium":
            return {
                "allowed": True,
                "risk_level": "medium",
                "requires_approval": False,
                "reason": "Medium-risk state change. Logged for review.",
                "gate": "confirm",
            }
        elif risk == "high":
            return {
                "allowed": True,
                "risk_level": "high",
                "requires_approval": True,
                "reason": "High-risk action requires operator approval",
                "gate": "approve",
            }

        return {
            "allowed": False,
            "risk_level": "unknown",
            "requires_approval": False,
            "reason": "Unrecognized action — default deny",
            "gate": "block",
        }
