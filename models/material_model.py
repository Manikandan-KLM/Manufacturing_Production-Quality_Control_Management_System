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


class Material(Base):

    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    material_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )

    material_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    available_quantity: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0
    )

    minimum_stock_level: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0
    )

    reorder_level: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0
    )

    supplier_reference: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        Enum(
            "Active",
            "Inactive",
            "Discontinued",
            name="material_status"
        ),
        nullable=False,
        default="Active",
        index=True
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