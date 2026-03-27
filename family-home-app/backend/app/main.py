from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_db
from .routers import assets, family, reminders, sync, tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Family Home App",
    description="A warm, pleasant household task manager for the whole family",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tasks.router, prefix="/api")
app.include_router(family.router, prefix="/api")
app.include_router(reminders.router, prefix="/api")
app.include_router(sync.router, prefix="/api")
app.include_router(assets.router, prefix="/api")


@app.get("/")
def root():
    return {
        "name": "Family Home App",
        "version": "0.1.0",
        "message": "Welcome! Your family's cozy task manager is running.",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}
