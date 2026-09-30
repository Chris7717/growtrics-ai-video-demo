from fastapi import APIRouter
from app.api.videos import router as videos_router
from app.api.concepts import router as concepts_router

api_router = APIRouter()
api_router.include_router(videos_router, prefix="/v1")
api_router.include_router(concepts_router, prefix="/v1")
