from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from ftplib import FTP

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.secrets import decrypt_secret, encrypt_secret
from app.models.integration_setting import IntegrationSetting


@dataclass(slots=True)
class HejcoRuntimeConfig:
    provider: str = "Hejco"
    ftp_host: str = "partnerftp.hejco.com"
    ftp_username: str | None = None
    ftp_password: str | None = None
    pictures_path: str = "/Hejco/Pictures/jpeg"
    product_data_path: str = "/Hejco/product_data/Swedish/PIMexport_Hejco_sv-SE.csv"
    stock_path: str = "/Hejco/stock_availability"
    sync_enabled: bool = True
    sync_hour: int = 3
    timeout_seconds: int = 60


class IntegrationSettingService:
    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self.session = session
        self.settings = settings

    async def get_hejco_setting(self) -> IntegrationSetting | None:
        result = await self.session.execute(
            select(IntegrationSetting).where(IntegrationSetting.provider == "Hejco")
        )
        return result.scalar_one_or_none()

    async def resolve_hejco_config(self) -> HejcoRuntimeConfig:
        setting = await self.get_hejco_setting()
        if setting is None:
            return HejcoRuntimeConfig(
                ftp_host=self.settings.hejco_ftp_host,
                ftp_username=self.settings.hejco_ftp_user,
                ftp_password=self.settings.hejco_ftp_pass,
                pictures_path="/Hejco/Pictures/jpeg",
                product_data_path="/Hejco/product_data/Swedish/PIMexport_Hejco_sv-SE.csv",
                stock_path="/Hejco/stock_availability",
                sync_enabled=self.settings.hejco_nightly_sync_enabled,
                sync_hour=self.settings.hejco_nightly_sync_hour,
                timeout_seconds=self.settings.hejco_ftp_timeout_seconds,
            )
        return HejcoRuntimeConfig(
            ftp_host=setting.ftp_host or self.settings.hejco_ftp_host,
            ftp_username=setting.ftp_username,
            ftp_password=decrypt_secret(setting.ftp_password_encrypted, self.settings.jwt_secret_key)
            if setting.ftp_password_encrypted
            else self.settings.hejco_ftp_pass,
            pictures_path=setting.pictures_path,
            product_data_path=setting.product_data_path,
            stock_path=setting.stock_path,
            sync_enabled=setting.sync_enabled,
            sync_hour=setting.sync_hour,
            timeout_seconds=setting.timeout_seconds,
        )

    async def upsert_hejco_setting(self, payload: dict) -> IntegrationSetting:
        setting = await self.get_hejco_setting()
        if setting is None:
            setting = IntegrationSetting(provider="Hejco")
            self.session.add(setting)

        setting.ftp_host = payload["ftp_host"]
        setting.ftp_username = payload.get("ftp_username")
        if payload.get("ftp_password"):
            setting.ftp_password_encrypted = encrypt_secret(payload["ftp_password"], self.settings.jwt_secret_key)
        setting.pictures_path = payload["pictures_path"]
        setting.product_data_path = payload["product_data_path"]
        setting.stock_path = payload["stock_path"]
        setting.sync_enabled = payload["sync_enabled"]
        setting.sync_hour = payload["sync_hour"]
        setting.timeout_seconds = payload["timeout_seconds"]
        await self.session.flush()
        return setting

    async def test_hejco_connection(self) -> tuple[bool, str]:
        config = await self.resolve_hejco_config()
        if not config.ftp_username or not config.ftp_password:
            return False, "FTP credentials are missing."
        try:
            ftp = FTP()
            ftp.connect(config.ftp_host, 21, timeout=config.timeout_seconds)
            ftp.login(config.ftp_username, config.ftp_password)
            ftp.quit()
            return True, "Connection successful."
        except Exception as exc:
            return False, str(exc)

    async def record_sync_result(
        self,
        *,
        status: str,
        message: str | None,
        imported_product_count: int | None,
    ) -> None:
        setting = await self.get_hejco_setting()
        if setting is None:
            return
        setting.last_sync_at = datetime.now(UTC)
        setting.last_sync_status = status
        setting.last_sync_message = message
        setting.last_imported_product_count = imported_product_count
        self.session.add(setting)
        await self.session.commit()
