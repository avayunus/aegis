"""Mission model — a single mission record in the database."""

from datetime import datetime, timezone

from sqlalchemy import String, Float, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from aegis.models import Base


class Mission(Base):
    """Persistent record of a mission.

    The simulation engine holds live state in memory; this table captures
    the mission definition and final outcomes for replay and reporting.
    """

    __tablename__ = "missions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(256))
    mission_type: Mapped[str] = mapped_column(String(64))  # patrol, sar, recon
    status: Mapped[str] = mapped_column(String(32), default="planning")
    asset_count: Mapped[int] = mapped_column(Integer, default=0)
    progress_pct: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scenario_config: Mapped[str | None] = mapped_column(String, nullable=True)  # JSON blob
