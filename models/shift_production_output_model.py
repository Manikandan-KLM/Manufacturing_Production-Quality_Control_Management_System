from datetime import datetime

from sqlalchemy import (
    Integer,
    Float,
    Date,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class ShiftProductionOutput(Base):

    __tablename__ = "shift_production_outputs"

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

    production_batch_id: Mapped[int] = mapped_column(
        ForeignKey("production_batches.id"),
        nullable=False,
        index=True
    )

    work_date: Mapped[datetime] = mapped_column(
        Date,
        nullable=False,
        index=True
    )

    planned_quantity: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    produced_quantity: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0
    )

    rejected_quantity: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )