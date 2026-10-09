from datetime import datetime

from sqlalchemy import String, DateTime

from sqlalchemy.orm import Mapped, mapped_column

from db.database import Base


class RevokedToken(Base):

    __tablename__ = "revoked_tokens"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    token: Mapped[str] = mapped_column(
        String(1000),
        unique=True,
        nullable=False
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )