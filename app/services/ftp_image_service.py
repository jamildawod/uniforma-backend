import asyncio
import hashlib
from ftplib import FTP
from pathlib import Path, PurePosixPath

import paramiko
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.logging import get_logger
from app.models.product_image import ProductImage
from app.repositories.product_repository import ProductRepository


class FtpImageService:
    def __init__(
        self,
        session: AsyncSession,
        product_repository: ProductRepository,
        settings: Settings,
    ) -> None:
        self.session = session
        self.product_repository = product_repository
        self.settings = settings
        self.logger = get_logger(self.__class__.__name__)

    async def sync_images(self) -> int:
        images = await self.product_repository.list_images_needing_sync()
        synced = 0
        storage_root = self.settings.image_storage_root
        storage_root.mkdir(parents=True, exist_ok=True)

        for image in images:
            if not image.external_path:
                continue
            local_path = storage_root / self._relative_image_path(image.external_path)
            local_path.parent.mkdir(parents=True, exist_ok=True)

            remote_bytes = await self._download_bytes(image.external_path)
            if remote_bytes is None:
                continue

            if local_path.exists():
                local_hash = await asyncio.to_thread(self._file_hash, local_path)
                remote_hash = hashlib.sha256(remote_bytes).hexdigest()
                if local_hash == remote_hash:
                    image.local_path = str(local_path)
                    continue

            await asyncio.to_thread(local_path.write_bytes, remote_bytes)
            image.local_path = str(local_path)
            synced += 1

        if synced:
            await self.session.commit()

        self.logger.info("Image sync completed: images synced=%s", synced)
        return synced

    async def _download_bytes(self, external_path: str) -> bytes | None:
        if not self.settings.ftp_host or not self.settings.ftp_username or not self.settings.ftp_password:
            self.logger.warning("FTP/SFTP is not configured; skipping image sync.")
            return None

        if self.settings.ftp_protocol == "sftp":
            return await asyncio.to_thread(self._download_via_sftp, external_path)
        return await asyncio.to_thread(self._download_via_ftp, external_path)

    def _download_via_sftp(self, external_path: str) -> bytes:
        transport = paramiko.Transport(
            (
                self.settings.ftp_host,
                self.settings.ftp_port or 22,
            )
        )
        transport.connect(
            username=self.settings.ftp_username,
            password=self.settings.ftp_password,
        )
        sftp = paramiko.SFTPClient.from_transport(transport)
        try:
            remote_path = self._remote_path(external_path)
            with sftp.file(remote_path, "rb") as remote_file:
                return remote_file.read()
        finally:
            sftp.close()
            transport.close()

    def _download_via_ftp(self, external_path: str) -> bytes:
        ftp = FTP()
        ftp.connect(
            host=self.settings.ftp_host,
            port=self.settings.ftp_port or 21,
            timeout=self.settings.ftp_timeout_seconds,
        )
        ftp.login(self.settings.ftp_username, self.settings.ftp_password)
        chunks: list[bytes] = []
        try:
            ftp.retrbinary(f"RETR {self._remote_path(external_path)}", chunks.append)
            return b"".join(chunks)
        finally:
            ftp.quit()

    def _remote_path(self, external_path: str) -> str:
        base = PurePosixPath(self.settings.ftp_remote_base_path)
        path = PurePosixPath(external_path.lstrip("/"))
        return str(base / path)

    def _relative_image_path(self, external_path: str) -> Path:
        return Path(external_path.lstrip("/"))

    def _file_hash(self, path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            while chunk := handle.read(65536):
                digest.update(chunk)
        return digest.hexdigest()
