from datetime import date, datetime

from sqlalchemy import (
    String,
    Integer,
    Float,
    Date,
    DateTime,
    Enum,
    ForeignKey
)

from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class Machine(Base):

    __tablename__ = "machines"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    machine_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )

    machine_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    machine_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    production_line_id: Mapped[int] = mapped_column(
        ForeignKey("production_lines.id"),
        nullable=False,
        index=True
    )

    installation_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        Enum(
            "Running",
            "Idle",
            "Maintenance",
            "Breakdown",
            "Decommissioned",
            name="machine_status"
        ),
        nullable=False,
        default="Idle",
        index=True
    )

    operating_hours: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0
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