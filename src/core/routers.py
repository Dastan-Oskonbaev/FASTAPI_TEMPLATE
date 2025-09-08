from fastapi import APIRouter

from src.auth.router import router as auth_router
from src.profile.router import router as profile_router

api_router_v1 = APIRouter()
api_router_v1.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router_v1.include_router(profile_router, prefix="/profile", tags=["Profile"])
