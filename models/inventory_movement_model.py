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


class InventoryMovement(Base):

    __tablename__ = "inventory_movements"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    transaction_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )

    movement_type: Mapped[str] = mapped_column(
        Enum(
            "Raw Material Receipt",
            "Material Consumption",
            "Finished Goods Production",
            "Rejected Goods",
            "Stock Adjustment",
            name="inventory_movement_type"
        ),
        nullable=False,
        index=True
    )

    material_id: Mapped[int | None] = mapped_column(
        ForeignKey("materials.id"),
        nullable=True,
        index=True
    )

    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("products.id"),
        nullable=True,
        index=True
    )

    production_batch_id: Mapped[int | None] = mapped_column(
        ForeignKey("production_batches.id"),
        nullable=True,
        index=True
    )

    quantity: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    quantity_before: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    quantity_after: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    reference_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    performed_by: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )