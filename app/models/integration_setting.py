from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class IntegrationSetting(Base):
    __tablename__ = "integration_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)
    ftp_host: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ftp_username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ftp_password_encrypted: Mapped[str | None] = mapped_column(Text, nullable=True)
    pictures_path: Mapped[str] = mapped_column(String(1024), nullable=False, server_default="/Hejco/Pictures/jpeg")
    product_data_path: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
        server_default="/Hejco/product_data/Swedish/PIMexport_Hejco_sv-SE.csv",
    )
    stock_path: Mapped[str] = mapped_column(String(1024), nullable=False, server_default="/Hejco/stock_availability")
    sync_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    sync_hour: Mapped[int] = mapped_column(Integer, nullable=False, default=3, server_default="3")
    timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=60, server_default="60")
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_sync_status: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_sync_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_imported_product_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
