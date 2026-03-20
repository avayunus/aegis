"""Command model — every operator command and the system's response.

This is core to the auditability promise. Every natural-language instruction
the operator types, what the AI interpreted, what tools were invoked, and
what the outcome was — all stored here.
"""

from datetime import datetime, timezone

from sqlalchemy import String, Float, DateTime, Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from aegis.models import Base


class Command(Base):
    """A single operator command and its lifecycle."""

    __tablename__ = "commands"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    mission_id: Mapped[str] = mapped_column(String(64), ForeignKey("missions.id"))
    raw_text: Mapped[str] = mapped_column(Text)  # Exactly what the operator typed
    interpreted_intent: Mapped[str | None] = mapped_column(String(256), nullable=True)
    risk_level: Mapped[str] = mapped_column(String(16), default="low")  # low, medium, high, blocked
    status: Mapped[str] = mapped_column(String(32), default="pending")
    # pending -> approved -> executed -> completed / failed
    # pending -> rejected
    # pending -> blocked
    tools_invoked: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list
    result_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    requires_approval: Mapped[bool] = mapped_column(default=False)
    approved_by: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    executed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
