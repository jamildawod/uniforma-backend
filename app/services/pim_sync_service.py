import hashlib
from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.core.config import Settings
from app.core.logging import get_logger
from app.models.pim_sync_run import PimSyncRun
from app.models.sync_run import SyncRun
from app.schemas.sync import PimSyncResponse
from app.services.ftp_image_service import FtpImageService
from app.services.pim_ingestion_service import PimIngestionService


class PimSyncService:
    def __init__(
        self,
        ingestion_service: PimIngestionService,
        image_service: FtpImageService,
        settings: Settings,
    ) -> None:
        self.ingestion_service = ingestion_service
        self.image_service = image_service
        self.settings = settings
        self.logger = get_logger(self.__class__.__name__)

    async def run_sync(self) -> PimSyncResponse:
        session = self.ingestion_service.session
        lock_acquired = False
        sync_run = SyncRun(started_at=datetime.now(UTC), status="running")
        pim_sync_run = PimSyncRun(started_at=datetime.now(UTC), status="running", source_id=None)
        session.add(sync_run)
        session.add(pim_sync_run)
        await session.flush()
        advisory_lock_key = self._advisory_lock_key()

        try:
            self.logger.info("Attempting to acquire PIM sync advisory lock.")
            result = await session.execute(
                text("SELECT pg_try_advisory_lock(:key)"),
                {"key": advisory_lock_key},
            )
            lock_acquired = bool(result.scalar())
            if not lock_acquired:
                self.logger.warning("PIM sync advisory lock is already held.")
                sync_run.finished_at = datetime.now(UTC)
                sync_run.status = "failed"
                sync_run.error_message = "Sync already running"
                pim_sync_run.finished_at = datetime.now(UTC)
                pim_sync_run.status = "failed"
                await session.commit()
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Sync already running",
                )
            self.logger.info("PIM sync advisory lock acquired.")

            sync_result = await self.ingestion_service.ingest()
            sync_result.images_synced = await self.image_service.sync_images()
            sync_run.finished_at = datetime.now(UTC)
            sync_run.products_created = sync_result.products_created
            sync_run.products_updated = sync_result.products_updated
            sync_run.variants_created = sync_result.variants_created
            sync_run.variants_updated = sync_result.variants_updated
            sync_run.images_synced = sync_result.images_synced
            sync_run.status = "success"
            sync_run.error_message = None
            pim_sync_run.finished_at = datetime.now(UTC)
            pim_sync_run.status = "success"
            pim_sync_run.records_imported = (
                sync_result.products_created
                + sync_result.products_updated
                + sync_result.variants_created
                + sync_result.variants_updated
            )
            await session.commit()
            self.logger.info("PIM sync finished with result: %s", sync_result.model_dump())
            return sync_result
        except IntegrityError as exc:
            await session.rollback()
            sync_run.finished_at = datetime.now(UTC)
            sync_run.status = "failed"
            sync_run.error_message = str(exc)
            pim_sync_run.finished_at = datetime.now(UTC)
            pim_sync_run.status = "failed"
            session.add(sync_run)
            session.add(pim_sync_run)
            await session.commit()
            self.logger.error(
                "PIM sync integrity error",
                extra={
                    "event": "pim_sync_integrity_error",
                    "error": str(exc),
                },
            )
            raise
        except Exception as exc:
            await session.rollback()
            sync_run.finished_at = datetime.now(UTC)
            sync_run.status = "failed"
            sync_run.error_message = str(exc)
            pim_sync_run.finished_at = datetime.now(UTC)
            pim_sync_run.status = "failed"
            session.add(sync_run)
            session.add(pim_sync_run)
            await session.commit()
            self.logger.error(
                "PIM sync failed",
                extra={
                    "event": "pim_sync_failed",
                    "error": str(exc),
                },
            )
            raise
        finally:
            if lock_acquired:
                self.logger.info("Releasing PIM sync advisory lock.")
                await session.execute(
                    text("SELECT pg_advisory_unlock(:key)"),
                    {"key": advisory_lock_key},
                )

    def _advisory_lock_key(self) -> int:
        digest = hashlib.sha256(self.settings.project_slug.encode("utf-8")).digest()
        key = int.from_bytes(digest[:8], byteorder="big", signed=False)
        if key >= 2**63:
            key -= 2**64
        return key
