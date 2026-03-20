"""Tests for the policy engine rules and classification."""

from aegis.policy.rules import classify_risk, is_blocked
from aegis.policy.classifier import classify_command_text


def test_query_tools_are_low_risk():
    """Read-only query tools should always be low risk."""
    assert classify_risk("query_asset_status") == "low"
    assert classify_risk("query_mission_progress") == "low"
    assert classify_risk("get_alerts") == "low"
    assert classify_risk("list_assets") == "low"
    assert classify_risk("generate_mission_summary") == "low"


def test_state_change_tools_are_medium_risk():
    """Tools that modify asset state should be medium risk."""
    assert classify_risk("assign_waypoints") == "medium"
    assert classify_risk("reroute_asset") == "medium"
    assert classify_risk("set_speed_limit") == "medium"


def test_critical_tools_are_high_risk():
    """Mission-critical commands should require approval."""
    assert classify_risk("command_rtb") == "high"
    assert classify_risk("command_rtb_all") == "high"
    assert classify_risk("abort_mission") == "high"
    assert classify_risk("emergency_land") == "high"


def test_deny_list_blocks_dangerous_tools():
    """Deny-listed tools should always be blocked."""
    assert is_blocked("disable_safety") is True
    assert is_blocked("destroy_asset") is True
    assert is_blocked("override_policy") is True
    assert is_blocked("delete_audit_log") is True
    assert is_blocked("modify_audit_log") is True


def test_safe_tools_not_blocked():
    """Normal tools should not be on the deny-list."""
    assert is_blocked("query_asset_status") is False
    assert is_blocked("assign_waypoints") is False
    assert is_blocked("command_rtb") is False


def test_nl_classifier_detects_high_risk():
    """Natural-language classifier should catch high-risk commands."""
    assert classify_command_text("return all assets to base") == "high"
    assert classify_command_text("RTB everything") == "high"
    assert classify_command_text("abort the mission") == "high"


def test_nl_classifier_detects_blocked():
    """Natural-language classifier should catch blocked commands."""
    assert classify_command_text("disable safety monitoring") == "blocked"
    assert classify_command_text("destroy drone-01") == "blocked"


def test_nl_classifier_allows_queries():
    """Simple questions should be classified as low risk."""
    assert classify_command_text("what is hawk-1's battery?") == "low"
    assert classify_command_text("show me mission progress") == "low"
    assert classify_command_text("how many assets are active?") == "low"
