"""Audit log model — immutable record of every significant system event.

This is the backbone of the safety and accountability story. Every action,
decision, approval, and anomaly gets an entry here. The audit log is
append-only and forms the basis for mission replay and post-mission reports.
"""

from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from aegis.models import Base


class AuditLog(Base):
    """A single audit log entry. Append-only."""

    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    event_type: Mapped[str] = mapped_column(String(64))
    # Event types: command_issued, command_approved, command_rejected,
    # command_executed, command_failed, alert_raised, alert_acknowledged,
    # policy_block, asset_status_change, mission_state_change,
    # agent_tool_call, agent_response, system_error
    severity: Mapped[str] = mapped_column(String(16), default="info")
    source: Mapped[str] = mapped_column(String(64))  # "operator", "agent", "policy", "simulation"
    mission_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    asset_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    command_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    message: Mapped[str] = mapped_column(Text)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON blob for extra context
