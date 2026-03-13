from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


PimSourceTypeValue = Literal["ftp", "sftp", "http", "local"]


class PimSourceCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    type: PimSourceTypeValue
    host: str | None = Field(default=None, max_length=255)
    port: int | None = None
    username: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, max_length=255)
    path: str | None = Field(default=None, max_length=1024)
    file_pattern: str | None = Field(default=None, max_length=255)
    schedule: str | None = Field(default="0 2 * * *", max_length=255)
    is_active: bool = True


class PimSourceRead(BaseModel):
    id: int
    name: str
    type: PimSourceTypeValue
    host: str | None
    port: int | None
    username: str | None
    password: str | None
    path: str | None
    file_pattern: str | None
    schedule: str | None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PimRunImportRequest(BaseModel):
    source_id: int


class PimImportRunRead(BaseModel):
    id: int
    source_id: int | None
    status: str
    started_at: datetime
    finished_at: datetime | None
    records_processed: int
    records_created: int
    records_updated: int
    error_log: str | None
    source: PimSourceRead | None = None

    model_config = ConfigDict(from_attributes=True)


class PimConnectionTestResponse(BaseModel):
    ok: bool
