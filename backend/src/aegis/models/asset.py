"""Asset model — persistent record of an autonomous vehicle."""

from datetime import datetime, timezone

from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from aegis.models import Base


class Asset(Base):
    """An autonomous vehicle that participated in a mission.

    Telemetry snapshots are stored separately; this table holds the
    asset definition and final-state metadata.
    """

    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    callsign: Mapped[str] = mapped_column(String(32))
    vehicle_type: Mapped[str] = mapped_column(String(32))  # quadrotor, ground_rover, fixed_wing
    mission_id: Mapped[str] = mapped_column(String(64), ForeignKey("missions.id"))
    home_x: Mapped[float] = mapped_column(Float, default=0.0)
    home_y: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
