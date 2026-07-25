import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine, Base
from app.api.router import router
from app.services.stream_simulator import start_live_stream_simulator

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise Forward Deployed Engineer (FDE) Control Plane API for Data Ingestion, Entity Resolution, and Human-In-The-Loop AI Agents.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware setup for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.on_event("startup")
async def startup_event():
    # Initialize DB tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Launch background live stream simulator
    asyncio.create_task(start_live_stream_simulator())

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
