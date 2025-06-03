from fastapi import APIRouter

# Import routers directly
from backend.src.api.auth import router as auth_router
from backend.src.api.agents import router as agents_router
from backend.src.api.workflows import router as workflows_router

# Create a main router that includes all sub-routers
api_router = APIRouter(prefix="/api")

# Add all sub-routers to the main router
api_router.include_router(auth_router)
api_router.include_router(agents_router)
api_router.include_router(workflows_router)

__all__ = ["api_router"] 