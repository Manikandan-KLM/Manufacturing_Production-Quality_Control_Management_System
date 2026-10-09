from datetime import datetime, time

from sqlalchemy import (
    Integer,
    String,
    Time,
    DateTime,
    Enum,
    ForeignKey
)

from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class Shift(Base):

    __tablename__ = "shifts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    shift_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )

    shift_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    start_time: Mapped[time] = mapped_column(
        Time,
        nullable=False
    )

    end_time: Mapped[time] = mapped_column(
        Time,
        nullable=False
    )

    shift_type: Mapped[str] = mapped_column(
        Enum(
            "Morning",
            "Evening",
            "Night",
            name="shift_type"
        ),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        Enum(
            "Active",
            "Inactive",
            name="shift_status"
        ),
        nullable=False,
        default="Active"
    )

    plant_id: Mapped[int] = mapped_column(
        ForeignKey("plants.id"),
        nullable=False,
        index=True
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