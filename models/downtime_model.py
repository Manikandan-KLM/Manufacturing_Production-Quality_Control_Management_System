from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    DateTime,
    Enum,
    ForeignKey,
    Text,
    Float
)

from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class Downtime(Base):

    __tablename__ = "downtimes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    downtime_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )

    machine_id: Mapped[int] = mapped_column(
        ForeignKey("machines.id"),
        nullable=False,
        index=True
    )

    production_line_id: Mapped[int] = mapped_column(
        ForeignKey("production_lines.id"),
        nullable=False,
        index=True
    )

    responsible_person_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    category: Mapped[str] = mapped_column(
        Enum(
            "Machine Breakdown",
            "Material Shortage",
            "Quality Issue",
            "Power Failure",
            "Maintenance",
            "Operator Issue",
            name="downtime_category"
        ),
        nullable=False,
        index=True
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    start_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True
    )

    end_time: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    duration_minutes: Mapped[float] = mapped_column(
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