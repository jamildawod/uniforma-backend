from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app.api.router import router as api_router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.db.session import dispose_engine, get_session_factory
from app.repositories.pim_repository import PimRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import UserCreate
from app.services.category_tree_service import CategoryTreeService
from app.services.hejco_import_service import HejcoImportService
from app.services.pim_downloader import PimDownloader
from app.services.pim_import_service import PimImportService
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


async def _bootstrap_category_tree() -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        await CategoryTreeService(session).ensure_default_tree()


def _build_scheduler() -> AsyncIOScheduler:
    settings = get_settings()
    scheduler = AsyncIOScheduler(timezone="UTC")

    async def scheduled_sync() -> None:
        session_factory = get_session_factory()
        async with session_factory() as session:
            import_service = PimImportService(
                session,
                settings,
                ProductRepository(session),
                PimRepository(session),
                PimDownloader(settings),
            )
            await import_service.run_active_imports()

    async def scheduled_hejco_sync() -> None:
        session_factory = get_session_factory()
        async with session_factory() as session:
            hejco_service = HejcoImportService(
                session,
                settings,
                ProductRepository(session),
            )
            await hejco_service.run_full_sync()

    if settings.pim_sync_enabled:
        scheduler.add_job(
            scheduled_sync,
            CronTrigger(hour=settings.pim_sync_cron_hour, minute=settings.pim_sync_cron_minute),
            id="pim-daily-sync",
            replace_existing=True,
        )
    if settings.hejco_nightly_sync_enabled:
        scheduler.add_job(
            scheduled_hejco_sync,
            CronTrigger(hour=settings.hejco_nightly_sync_hour, minute=settings.hejco_nightly_sync_minute),
            id="hejco-nightly-sync",
            replace_existing=True,
        )
    return scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    await _bootstrap_default_admin()
    await _bootstrap_category_tree()
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://uniforma.livosys.se",
        "https://admin.uniforma.livosys.se",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
settings.pim_imports_root.mkdir(parents=True, exist_ok=True)
settings.uploads_root.mkdir(parents=True, exist_ok=True)
settings.uploads_root.joinpath("products").mkdir(parents=True, exist_ok=True)
settings.hejco_images_root.mkdir(parents=True, exist_ok=True)
settings.hejco_csv_root.mkdir(parents=True, exist_ok=True)
settings.hejco_work_root.mkdir(parents=True, exist_ok=True)
settings.hejco_stock_root.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.uploads_root), name="uploads")
app.mount("/images/products", StaticFiles(directory=settings.hejco_images_root), name="hejco-product-images")
app.include_router(api_router)
