from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Text
)

from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class QualityInspection(Base):

    __tablename__ = "quality_inspections"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    inspection_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )

    inspection_type: Mapped[str] = mapped_column(
        Enum(
            "Incoming Material Inspection",
            "In-Process Inspection",
            "Final Product Inspection",
            name="inspection_type"
        ),
        nullable=False,
        index=True
    )

    production_batch_id: Mapped[int] = mapped_column(
        ForeignKey("production_batches.id"),
        nullable=False,
        index=True
    )

    inspector_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    inspection_date: Mapped[datetime] = mapped_column(
        Date,
        nullable=False,
        index=True
    )

    overall_result: Mapped[str] = mapped_column(
        Enum(
            "Pending",
            "Pass",
            "Fail",
            name="quality_result"
        ),
        nullable=False,
        default="Pending"
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
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