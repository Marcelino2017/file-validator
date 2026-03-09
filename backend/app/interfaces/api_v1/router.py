from fastapi import APIRouter

from app.interfaces.api_v1.auth_routes import router as auth_router
from app.interfaces.api_v1.pdf_routes import router as pdf_router


api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(pdf_router)
