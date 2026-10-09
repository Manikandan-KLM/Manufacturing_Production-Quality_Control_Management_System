from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    Float,
    DateTime,
    Enum,
    Text,
    ForeignKey
)

from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class Plant(Base):
    __tablename__ = "plants"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    plant_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )

    plant_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    address: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    state: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="India"
    )

    production_capacity: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0
    )

    capacity_unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="units/day"
    )

    status: Mapped[str] = mapped_column(
        Enum(
            "Active",
            "Maintenance",
            "Temporarily Closed",
            "Inactive",
            name="plant_status"
        ),
        nullable=False,
        default="Active"
    )

    manager_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
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