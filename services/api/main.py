from contextlib import asynccontextmanager

from fastapi import FastAPI

from .database import init_db
from .routers.contacts import router as contacts_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="AI Recruiter Outreach API",
    description="Control-plane HTTP API for the n8n recruiter outreach loop.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(contacts_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
