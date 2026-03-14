from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Uniforma Backend"
    project_slug: str = "uniforma"
    app_env: Literal["development", "staging", "production"] = "development"
    app_debug: bool = False
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"

    db_host: str = "db"
    db_port: int = 5432
    db_name: str = "uniforma"
    db_user: str = "uniforma"
    db_password: str = Field(..., min_length=8)
    db_echo: bool = False

    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_minutes: int = 10080
    jwt_secret_key: str = Field(..., min_length=32)
    jwt_refresh_secret_key: str = Field(..., min_length=32)

    default_admin_email: str = "admin@uniforma.app"
    default_admin_password: str = Field(..., min_length=12)

    pim_csv_path: Path = Path("/opt/uniforma/data/PIMexport_Hejco_sv-SE.csv")
    pim_csv_delimiter: str = ";"
    pim_batch_size: int = 200
    pim_sync_enabled: bool = True
    pim_sync_cron_hour: int = 2
    pim_sync_cron_minute: int = 0

    ftp_protocol: Literal["ftp", "sftp"] = "sftp"
    ftp_host: str | None = None
    ftp_port: int | None = None
    ftp_username: str | None = None
    ftp_password: str | None = None
    ftp_remote_base_path: str = "/"
    ftp_timeout_seconds: int = 30

    storage_root: Path = Path("/opt/uniforma/storage")
    uploads_root: Path = Path("/opt/uniforma/uploads")
    pim_imports_root: Path = Path("/opt/uniforma/pim_imports")

    hejco_data_root: Path = Path("/opt/uniforma/data")
    hejco_images_root: Path = Path("/opt/uniforma/data/images")
    hejco_csv_root: Path = Path("/opt/uniforma/data/csv")
    hejco_work_root: Path = Path("/opt/uniforma/data/hejco")
    hejco_csv_file: Path = Path("/opt/uniforma/data/csv/PIMexport_Hejco_sv-SE.csv")
    hejco_stock_root: Path = Path("/opt/uniforma/data/csv/stock_availability")
    hejco_ftp_host: str = "partnerftp.hejco.com"
    hejco_ftp_user: str | None = None
    hejco_ftp_pass: str | None = None
    hejco_ftp_timeout_seconds: int = 60
    hejco_batch_size: int = 250
    hejco_nightly_sync_enabled: bool = True
    hejco_nightly_sync_hour: int = 3
    hejco_nightly_sync_minute: int = 0

    redis_url: str | None = "redis://redis:6379/0"
    cache_ttl_seconds: int = 600
    catalog_default_limit: int = 24
    catalog_max_limit: int = 200

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sqlalchemy_database_uri(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def alembic_database_uri(self) -> str:
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def image_storage_root(self) -> Path:
        return self.storage_root / "images"


@lru_cache
def get_settings() -> Settings:
    return Settings()
