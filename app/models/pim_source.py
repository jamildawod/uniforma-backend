import enum

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PimSourceType(str, enum.Enum):
    ftp = "ftp"
    sftp = "sftp"
    http = "http"
    local = "local"


class PimSource(Base):
    __tablename__ = "pim_sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    type: Mapped[PimSourceType] = mapped_column(
        Enum(PimSourceType, name="pim_source_type_enum"),
        nullable=False,
    )
    host: Mapped[str | None] = mapped_column(String(255), nullable=True)
    port: Mapped[int | None] = mapped_column(Integer, nullable=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    path: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    file_pattern: Mapped[str | None] = mapped_column(String(255), nullable=True)
    schedule: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    import_runs: Mapped[list["PimImportRun"]] = relationship(back_populates="source", cascade="all, delete-orphan")
    sync_runs: Mapped[list["PimSyncRun"]] = relationship(back_populates="source", cascade="all, delete-orphan")
