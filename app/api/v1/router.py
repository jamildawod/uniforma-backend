from fastapi import APIRouter

from app.api.admin_intelligence import router as admin_intelligence_router
from app.api.products import router as products_router
from app.api.quotes import router as quotes_router
from app.api.v1.endpoints.admin_pim import router as admin_pim_router
from app.api.v1.endpoints.admin_products import router as admin_products_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.health import router as health_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(products_router, tags=["products"])
api_router.include_router(quotes_router, tags=["quotes"])
api_router.include_router(admin_products_router, tags=["admin"])
api_router.include_router(admin_pim_router, tags=["admin-pim"])
api_router.include_router(admin_intelligence_router, tags=["admin-intelligence"])
