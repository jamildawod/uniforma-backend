from fastapi import APIRouter

from app.api.v1.endpoints.admin_products import router as admin_products_router
from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.public_products import router as public_products_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(public_products_router, tags=["products"])
api_router.include_router(admin_products_router, tags=["admin"])
