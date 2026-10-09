from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    Float,
    DateTime,
    Enum,
    ForeignKey,
    Text
)

from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class MaterialHistory(Base):

    __tablename__ = "material_histories"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    material_id: Mapped[int] = mapped_column(
        ForeignKey("materials.id"),
        nullable=False,
        index=True
    )

    transaction_type: Mapped[str] = mapped_column(
        Enum(
            "STOCK_IN",
            "STOCK_OUT",
            "ADJUSTMENT",
            name="material_transaction_type"
        ),
        nullable=False,
        index=True
    )

    quantity: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    previous_quantity: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    new_quantity: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    reference: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    remarks: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    performed_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )