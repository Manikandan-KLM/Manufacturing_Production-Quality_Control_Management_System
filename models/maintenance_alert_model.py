from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    Text
)

from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class MaintenanceAlert(Base):

    __tablename__ = "maintenance_alerts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    machine_id: Mapped[int] = mapped_column(
        ForeignKey("machines.id"),
        nullable=False,
        index=True
    )

    schedule_id: Mapped[int] = mapped_column(
        ForeignKey("maintenance_schedules.id"),
        nullable=False,
        index=True
    )

    alert_message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    due_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    is_read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )