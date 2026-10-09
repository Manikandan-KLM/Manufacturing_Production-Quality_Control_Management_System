from datetime import datetime

from sqlalchemy import (
    Integer,
    Float,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class ProductInventory(Base):

    __tablename__ = "product_inventory"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        unique=True,
        nullable=False,
        index=True
    )

    available_quantity: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0
    )

    rejected_quantity: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )