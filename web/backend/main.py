import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.database import engine
from app.db.models import Base
from app.api.auth import router as auth_router
from app.api.charaktere import router as charaktere_router
from app.api.einstellungen import router as einstellungen_router
from app.api.spiellogik import router as spiellogik_router

data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(charaktere_router)
app.include_router(einstellungen_router)
app.include_router(spiellogik_router)


@app.get("/api/health")
def health():
    return {"status": "ok", "version": "0.1.0"}
