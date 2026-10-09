from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    DateTime,
    ForeignKey,
    Text
)
from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class ProductionWorkflowHistory(Base):
    __tablename__ = "production_workflow_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    production_order_id: Mapped[int] = mapped_column(
        ForeignKey("production_orders.id"),
        nullable=False,
        index=True
    )

    from_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    to_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False
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
        default=datetime.utcnow,
        nullable=False
    )