from datetime import datetime

from sqlalchemy import (
    Integer,
    Date,
    DateTime,
    Boolean,
    ForeignKey,
    UniqueConstraint
)

from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class ShiftWorker(Base):

    __tablename__ = "shift_workers"

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

    worker_id: Mapped[int] = mapped_column(
        ForeignKey("workers.id"),
        nullable=False,
        index=True
    )

    work_date: Mapped[datetime] = mapped_column(
        Date,
        nullable=False,
        index=True
    )

    assigned_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint(
            "shift_id",
            "worker_id",
            "work_date",
            name="uq_shift_worker_date"
        ),
    )