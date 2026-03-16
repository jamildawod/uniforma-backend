import asyncio
from ftplib import FTP
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse
from urllib.request import urlopen

import paramiko

from app.core.config import Settings
from app.models.pim_source import PimSource, PimSourceType


class PimDownloader:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def download(self, source: PimSource) -> Path:
        self.settings.pim_imports_root.mkdir(parents=True, exist_ok=True)
        if source.type == PimSourceType.local:
            if not source.path:
                raise ValueError("Local source requires path")
            return Path(source.path)
        if source.type == PimSourceType.http:
            return await self.download_http_file(source)
        if source.type == PimSourceType.ftp:
            return await self.download_ftp_file(source)
        if source.type == PimSourceType.sftp:
            return await self.download_sftp_file(source)
        raise ValueError(f"Unsupported source type: {source.type}")

    async def download_ftp_file(self, source: PimSource) -> Path:
        return await asyncio.to_thread(self._download_ftp_file, source)

    async def download_sftp_file(self, source: PimSource) -> Path:
        return await asyncio.to_thread(self._download_sftp_file, source)

    async def download_http_file(self, source: PimSource) -> Path:
        return await asyncio.to_thread(self._download_http_file, source)

    def _download_http_file(self, source: PimSource) -> Path:
        if not source.path:
            raise ValueError("HTTP source requires path")
        target = self._target_path(source, Path(urlparse(source.path).path).name or "import.dat")
        with urlopen(source.path) as response:
            target.write_bytes(response.read())
        return target

    def _download_ftp_file(self, source: PimSource) -> Path:
        if not source.host or not source.path:
            raise ValueError("FTP source requires host and path")
        target = self._target_path(source, Path(source.path).name or "import.dat")
        ftp = FTP()
        ftp.connect(source.host, source.port or 21, timeout=self.settings.ftp_timeout_seconds)
        ftp.login(source.username or "", source.password or "")
        try:
            with target.open("wb") as handle:
                ftp.retrbinary(f"RETR {self._remote_path(source)}", handle.write)
        finally:
            ftp.quit()
        return target

    def _download_sftp_file(self, source: PimSource) -> Path:
        if not source.host or not source.path:
            raise ValueError("SFTP source requires host and path")
        target = self._target_path(source, Path(source.path).name or "import.dat")
        transport = paramiko.Transport((source.host, source.port or 22))
        transport.connect(username=source.username or "", password=source.password or "")
        sftp = paramiko.SFTPClient.from_transport(transport)
        try:
            sftp.get(self._remote_path(source), str(target))
        finally:
            sftp.close()
            transport.close()
        return target

    def _remote_path(self, source: PimSource) -> str:
        return str(PurePosixPath(source.path or "/"))

    def _target_path(self, source: PimSource, file_name: str) -> Path:
        safe_name = f"source-{source.id}-{file_name}"
        return self.settings.pim_imports_root / safe_name
