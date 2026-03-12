from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from pydantic import ValidationError

from app.api.router import router as api_router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.db.session import dispose_engine, get_session_factory
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserCreate
from app.services.ftp_image_service import FtpImageService
from app.services.pim_ingestion_service import PimIngestionService
from app.services.pim_sync_service import PimSyncService
from app.services.user_service import UserService

configure_logging()
logger = get_logger(__name__)


async def _bootstrap_default_admin() -> None:
    settings = get_settings()
    session_factory = get_session_factory()
    async with session_factory() as session:
        service = UserService(UserRepository(session))
        if await service.get_by_email(settings.default_admin_email) is None:
            try:
                user = await service.create_user(
                    UserCreate(
                        email=settings.default_admin_email,
                        password=settings.default_admin_password,
                        full_name="Uniforma Admin",
                    ),
                    is_superuser=True,
                )
            except ValidationError as exc:
                logger.error(
                    "Default admin bootstrap configuration is invalid.",
                    extra={
                        "event": "default_admin_bootstrap_invalid",
                        "error": str(exc),
                    },
                )
                await session.rollback()
                return

            await session.commit()
            await session.refresh(user)


def _build_scheduler() -> AsyncIOScheduler:
    settings = get_settings()
    scheduler = AsyncIOScheduler(timezone="UTC")

    async def scheduled_sync() -> None:
        session_factory = get_session_factory()
        async with session_factory() as session:
            product_repository = ProductRepository(session)
            sync_service = PimSyncService(
                PimIngestionService(session, product_repository, settings),
                FtpImageService(session, product_repository, settings),
                settings,
            )
            await sync_service.run_sync()

    if settings.pim_sync_enabled:
        scheduler.add_job(
            scheduled_sync,
            CronTrigger(hour=settings.pim_sync_cron_hour, minute=settings.pim_sync_cron_minute),
            id="pim-daily-sync",
            replace_existing=True,
        )
    return scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    await _bootstrap_default_admin()
    scheduler = _build_scheduler()
    scheduler.start()
    app.state.scheduler = scheduler
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)
        await dispose_engine()


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    lifespan=lifespan,
)
app.include_router(api_router)
