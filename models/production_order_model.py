from datetime import date, datetime

from sqlalchemy import Index

from sqlalchemy import (
    Integer,
    String,
    Float,
    Date,
    DateTime,
    Enum,
    ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class ProductionOrder(Base):
    __tablename__ = "production_orders"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    order_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False
    )

    quantity: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    target_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    production_line_id: Mapped[int] = mapped_column(
        ForeignKey("production_lines.id"),
        nullable=False
    )

    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="Normal"
    )

    supervisor_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        Enum(
            "Draft",
            "Pending Supervisor Review",
            "Supervisor Approved",
            "Supervisor Rejected",
            "Material Checked",
            "In Production",
            "Quality Approved",
            "Completed",
            "Manager Approved",
            name="production_order_status"
        ),
        nullable=False,
        default="Draft",
        index=True
    )

    supervisor_reviewed_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    supervisor_reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    material_checked_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    material_checked_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    production_started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    quality_approved_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    manager_approved_by: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True
    )

    manager_approved_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    __table_args__ = (
      Index(
        "ix_production_orders_status_target_date",
        "status",
        "target_date",
     ),
    )