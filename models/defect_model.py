from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    Float,
    DateTime,
    Enum,
    ForeignKey,
    Text
)

from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class Defect(Base):

    __tablename__ = "defects"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    defect_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )

    defect_type: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True
    )

    severity: Mapped[str] = mapped_column(
        Enum(
            "Minor",
            "Major",
            "Critical",
            name="defect_severity"
        ),
        nullable=False,
        index=True
    )

    production_batch_id: Mapped[int] = mapped_column(
        ForeignKey("production_batches.id"),
        nullable=False,
        index=True
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
        index=True
    )

    quality_inspection_id: Mapped[int | None] = mapped_column(
        ForeignKey("quality_inspections.id"),
        nullable=True,
        index=True
    )

    quantity_affected: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    root_cause: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    corrective_action: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    resolution_status: Mapped[str] = mapped_column(
        Enum(
            "Open",
            "In Progress",
            "Resolved",
            "Closed",
            name="defect_resolution_status"
        ),
        nullable=False,
        default="Open",
        index=True
    )

    reported_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    resolved_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
        index=True
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
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