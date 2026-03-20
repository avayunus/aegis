"""AI Agent Orchestrator — uses Claude API for intelligent command interpretation.

This is the brain of AEGIS. It takes natural-language operator commands,
grounds them in the current mission state, and returns structured actions
with tactical reasoning.

Falls back to pattern matching if no API key is configured.
"""

import json
import httpx

from aegis.config import settings
from aegis.agent.prompts import build_system_prompt
from aegis.agent.tools import TOOL_SCHEMAS


class AgentOrchestrator:
    """Bridges operator commands to Claude for intelligent interpretation."""

    def __init__(self):
        self.api_key = settings.anthropic_api_key
        self.model = "claude-sonnet-4-20250514"
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.max_tokens = 1024

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    async def interpret(self, text: str, mission_context: dict) -> dict:
        """Send operator command + mission state to Claude for interpretation.

        Args:
            text: Natural-language command from the operator.
            mission_context: Current simulation state snapshot.

        Returns:
            {
                "response": "Tactical text response for the operator",
                "actions": [{"tool": "...", "params": {...}}],
                "risk_level": "low|medium|high",
                "reasoning": "Why this action was chosen"
            }
        """
        if not self.enabled:
            return self._fallback(text)

        system_prompt = build_system_prompt(mission_context)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    self.api_url,
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "max_tokens": self.max_tokens,
                        "system": system_prompt,
                        "tools": TOOL_SCHEMAS,
                        "messages": [
                            {"role": "user", "content": text}
                        ],
                    },
                )
                resp.raise_for_status()
                data = resp.json()

            return self._parse_response(data)

        except httpx.HTTPStatusError as e:
            return {
                "response": f"AI agent error ({e.response.status_code}). Using fallback.",
                "actions": [],
                "risk_level": "low",
                "reasoning": f"API error: {e.response.status_code}",
                "fallback": True,
            }
        except Exception as e:
            return {
                "response": f"AI agent unavailable: {str(e)[:100]}. Using fallback.",
                "actions": [],
                "risk_level": "low",
                "reasoning": f"Error: {str(e)[:100]}",
                "fallback": True,
            }

    def _parse_response(self, data: dict) -> dict:
        """Parse the Claude API response into structured output."""
        content = data.get("content", [])
        text_parts = []
        actions = []

        for block in content:
            if block["type"] == "text":
                text_parts.append(block["text"])
            elif block["type"] == "tool_use":
                actions.append({
                    "tool": block["name"],
                    "params": block["input"],
                    "tool_use_id": block["id"],
                })

        response_text = "\n".join(text_parts) if text_parts else ""

        # Determine risk level from actions
        risk = "low"
        for a in actions:
            tool = a["tool"]
            if tool in ("command_rtb_all", "abort_mission", "emergency_land"):
                risk = "high"
            elif tool in ("command_rtb", "assign_waypoints", "hold_position") and risk != "high":
                risk = "medium"

        return {
            "response": response_text,
            "actions": actions,
            "risk_level": risk,
            "reasoning": response_text[:200] if response_text else "Tool call executed",
            "stop_reason": data.get("stop_reason", ""),
        }

    def _fallback(self, text: str) -> dict:
        """Fallback when no API key is set."""
        return {
            "response": "",
            "actions": [],
            "risk_level": "low",
            "reasoning": "AI agent not configured — using pattern matching",
            "fallback": True,
        }
