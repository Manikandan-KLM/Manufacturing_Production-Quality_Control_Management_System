from datetime import date, datetime

from sqlalchemy import (
    Integer,
    String,
    Float,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Text
)

from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class Maintenance(Base):

    __tablename__ = "maintenances"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    maintenance_number: Mapped[str] = mapped_column(
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
            name="maintenance_type"
        ),
        nullable=False,
        index=True
    )

    maintenance_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    technician_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True
    )

    status: Mapped[str] = mapped_column(
        Enum(
            "Scheduled",
            "In Progress",
            "Completed",
            "Cancelled",
            name="maintenance_status"
        ),
        nullable=False,
        default="Scheduled",
        index=True
    )

    labor_cost: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0
    )

    spare_parts_cost: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0
    )

    total_cost: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
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