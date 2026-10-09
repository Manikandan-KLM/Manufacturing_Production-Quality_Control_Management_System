from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    Float,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class ProductionBatch(Base):

    __tablename__ = "production_batches"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    batch_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )

    production_order_id: Mapped[int] = mapped_column(
        ForeignKey("production_orders.id"),
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

    start_time: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    end_time: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    production_line_id: Mapped[int] = mapped_column(
        ForeignKey("production_lines.id"),
        nullable=False,
        index=True
    )

    machine_id: Mapped[int] = mapped_column(
        ForeignKey("machines.id"),
        nullable=False,
        index=True
    )

    supervisor_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True
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