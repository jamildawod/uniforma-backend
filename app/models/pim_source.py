import enum

from sqlalchemy import Enum, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PimSourceType(str, enum.Enum):
    csv = "csv"
    ftp = "ftp"
    api = "api"


class PimSource(Base):
    __tablename__ = "pim_sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    type: Mapped[PimSourceType] = mapped_column(
        Enum(PimSourceType, name="pim_source_type_enum"),
        nullable=False,
    )
    config_json: Mapped[dict | list | str | int | float | bool | None] = mapped_column(JSONB, nullable=True)

    sync_runs: Mapped[list["PimSyncRun"]] = relationship(back_populates="source", cascade="all, delete-orphan")
