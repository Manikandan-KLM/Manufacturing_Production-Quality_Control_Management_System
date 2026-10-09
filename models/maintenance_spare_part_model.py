from datetime import datetime

from sqlalchemy import (
    Integer,
    Float,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class MaintenanceSparePart(Base):

    __tablename__ = "maintenance_spare_parts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    maintenance_id: Mapped[int] = mapped_column(
        ForeignKey("maintenances.id"),
        nullable=False,
        index=True
    )

    material_id: Mapped[int] = mapped_column(
        ForeignKey("materials.id"),
        nullable=False,
        index=True
    )

    quantity_used: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    unit_cost: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    total_cost: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )