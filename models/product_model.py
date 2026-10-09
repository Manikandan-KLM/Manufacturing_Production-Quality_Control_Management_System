from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    Float,
    DateTime,
    Enum,
    Text
)

from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class Product(Base):

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    product_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )

    product_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    sku: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False
    )

    unit_of_measurement: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        Enum(
            "Active",
            "Inactive",
            "Discontinued",
            name="product_status"
        ),
        nullable=False,
        default="Active",
        index=True
    )

    standard_production_time: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    production_time_unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="minutes"
    )

    description: Mapped[str | None] = mapped_column(
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