from fastapi import FastAPI
from contextlib import asynccontextmanager

from .database import init_db
from .routers import tasks

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="Task Management API",
    description="FastAPI Task Management System with Background Processing",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(tasks.router)

@app.get("/")
async def root():
    return {"message": "Task Management API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
