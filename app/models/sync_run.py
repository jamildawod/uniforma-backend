from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class SyncRun(Base):
    __tablename__ = "sync_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    products_created: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    products_updated: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    variants_created: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    variants_updated: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    images_synced: Mapped[int] = mapped_column(Integer, nullable=False, default=0, server_default="0")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="success", server_default="success")
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
