from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.hejco import HejcoImportResponse


class HejcoIntegrationUpdateRequest(BaseModel):
    provider: str = "Hejco"
    ftp_host: str = Field(default="partnerftp.hejco.com", max_length=255)
    ftp_username: str | None = Field(default=None, max_length=255)
    ftp_password: str | None = Field(default=None, max_length=255)
    pictures_path: str = Field(default="/Hejco/Pictures/jpeg", max_length=1024)
    product_data_path: str = Field(default="/Hejco/product_data/Swedish/PIMexport_Hejco_sv-SE.csv", max_length=1024)
    stock_path: str = Field(default="/Hejco/stock_availability", max_length=1024)
    sync_enabled: bool = True
    sync_hour: int = Field(default=3, ge=0, le=23)
    timeout_seconds: int = Field(default=60, ge=5, le=600)


class HejcoIntegrationRead(BaseModel):
    provider: str
    ftp_host: str | None
    ftp_username: str | None
    ftp_password_masked: str | None = None
    has_password: bool = False
    pictures_path: str
    product_data_path: str
    stock_path: str
    sync_enabled: bool
    sync_hour: int
    timeout_seconds: int
    last_sync_at: datetime | None = None
    last_sync_status: str | None = None
    last_sync_message: str | None = None
    last_imported_product_count: int | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class HejcoConnectionTestResponse(BaseModel):
    ok: bool
    message: str


class HejcoSyncResponse(HejcoImportResponse):
    message: str | None = None
