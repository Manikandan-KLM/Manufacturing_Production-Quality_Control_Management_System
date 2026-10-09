from datetime import date, datetime

from sqlalchemy import (
    Integer,
    String,
    Date,
    DateTime,
    Enum,
    ForeignKey
)

from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class MaintenanceSchedule(Base):

    __tablename__ = "maintenance_schedules"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    schedule_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )

    machine_id: Mapped[int] = mapped_column(
        ForeignKey("machines.id"),
        nullable=False,
        index=True
    )

    maintenance_type: Mapped[str] = mapped_column(
        Enum(
            "Preventive",
            "Breakdown",
            name="maintenance_schedule_type"
        ),
        nullable=False
    )

    frequency_days: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    last_maintenance_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    next_due_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        index=True
    )

    status: Mapped[str] = mapped_column(
        Enum(
            "Active",
            "Inactive",
            "Completed",
            name="maintenance_schedule_status"
        ),
        nullable=False,
        default="Active"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )