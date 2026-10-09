from datetime import datetime

from sqlalchemy import (
    Integer,
    Float,
    Date,
    DateTime,
    Text,
    ForeignKey
)

from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class ShiftMachineUsage(Base):

    __tablename__ = "shift_machine_usage"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    shift_id: Mapped[int] = mapped_column(
        ForeignKey("shifts.id"),
        nullable=False,
        index=True
    )

    machine_id: Mapped[int] = mapped_column(
        ForeignKey("machines.id"),
        nullable=False,
        index=True
    )

    work_date: Mapped[datetime] = mapped_column(
        Date,
        nullable=False,
        index=True
    )

    operating_hours: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0
    )

    idle_hours: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0
    )

    breakdown_hours: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )