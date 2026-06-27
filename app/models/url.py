from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class URL(Base):
    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    short_code: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    long_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    click_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0", nullable=False)
