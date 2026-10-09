from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    Float,
    DateTime,
    Enum,
    ForeignKey
)

from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class ProductionLine(Base):

    __tablename__ = "production_lines"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    line_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )

    line_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    production_capacity: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    capacity_unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="units/day"
    )

    plant_id: Mapped[int] = mapped_column(
        ForeignKey("plants.id"),
        nullable=False,
        index=True
    )

    status: Mapped[str] = mapped_column(
        Enum(
            "Active",
            "Maintenance",
            "Inactive",
            "Temporarily Closed",
            name="production_line_status"
        ),
        nullable=False,
        default="Active"
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