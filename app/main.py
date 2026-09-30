from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api.router import api_router
from app.workers.video_worker import VideoWorker
from app.queue.asyncio_queue import local_queue

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize background task in FastAPI lifespan to run worker in the background
    worker = VideoWorker(queue=local_queue)
    await worker.start()
    yield
    # Cleanup resources if needed

app = FastAPI(
    title="Growtrics AI Video API",
    description="API for managing AI educational video generation",
    version="1.0.0",
    lifespan=lifespan
)

from fastapi.staticfiles import StaticFiles
import os

app.include_router(api_router, prefix="/api")

# Mount artifacts folder to serve video files
artifacts_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "artifacts")
os.makedirs(artifacts_dir, exist_ok=True)
app.mount("/artifacts", StaticFiles(directory=artifacts_dir), name="artifacts")
from fastapi.responses import FileResponse

@app.get("/", tags=["UI"])
async def serve_ui():
    return FileResponse(os.path.join(os.path.dirname(os.path.dirname(__file__)), "index.html"))

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}
