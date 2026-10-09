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


class QualityParameter(Base):

    __tablename__ = "quality_parameters"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    inspection_id: Mapped[int] = mapped_column(
        ForeignKey("quality_inspections.id"),
        nullable=False,
        index=True
    )

    parameter_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    unit: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    expected_value: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    actual_value: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    result: Mapped[str] = mapped_column(
        Enum(
            "Pass",
            "Fail",
            name="parameter_result"
        ),
        nullable=False
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )