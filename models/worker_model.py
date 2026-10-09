from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    Date,
    DateTime,
    Enum,
    ForeignKey
)

from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class Worker(Base):

    __tablename__ = "workers"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    employee_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )

    full_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    skill: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    department: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    shift: Mapped[str] = mapped_column(
        Enum(
            "Morning",
            "Afternoon",
            "Night",
            "General",
            name="worker_shift"
        ),
        nullable=False,
        default="General"
    )

    production_line_id: Mapped[int | None] = mapped_column(
        ForeignKey("production_lines.id"),
        nullable=True,
        index=True
    )

    status: Mapped[str] = mapped_column(
        Enum(
            "Active",
            "Inactive",
            "On Leave",
            "Suspended",
            "Resigned",
            name="worker_status"
        ),
        nullable=False,
        default="Active",
        index=True
    )

    joining_date: Mapped[Date | None] = mapped_column(
        Date,
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