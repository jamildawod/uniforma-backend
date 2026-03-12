from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.core.config import Settings
from app.core.logging import get_logger
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

        try:
            result = await session.execute(
                text("SELECT pg_try_advisory_lock(987654321)"),
            )
            lock_acquired = bool(result.scalar())
            if not lock_acquired:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Sync already running",
                )

            sync_result = await self.ingestion_service.ingest()
            sync_result.images_synced = await self.image_service.sync_images()
            self.logger.info("PIM sync finished with result: %s", sync_result.model_dump())
            return sync_result
        except IntegrityError as exc:
            await session.rollback()
            self.logger.error(
                "PIM sync integrity error",
                extra={
                    "event": "pim_sync_integrity_error",
                    "error": str(exc),
                },
            )
            raise
        finally:
            if lock_acquired:
                await session.execute(text("SELECT pg_advisory_unlock(987654321)"))
