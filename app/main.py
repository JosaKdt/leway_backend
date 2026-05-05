from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import create_db_and_tables
import app.models  # noqa : force la découverte de tous les modèles par SQLModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Crée les tables au démarrage si elles n'existent pas encore."""
    create_db_and_tables()
    yield


app = FastAPI(
    title="LÉWAY API",
    description=(
        "Plateforme d'aide à l'orientation post-baccalauréat au Bénin. "
        "Scoring psychométrique RIASEC + données marché + impact IA."
    ),
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# ─── CORS (Flutter mobile + React web) ───────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────
from app.api import auth, filieres, favoris, bacheliers

app.include_router(auth.router,        prefix="/api/auth",       tags=["Auth"])
app.include_router(filieres.router,    prefix="/api/filieres",   tags=["Filières"])
app.include_router(favoris.router,     prefix="/api/favoris",    tags=["Favoris"])
app.include_router(bacheliers.router,  prefix="/api/bacheliers", tags=["Bacheliers"])


@app.get("/", tags=["Health"])
def root():
    return {
        "app": "LÉWAY API",
        "version": settings.APP_VERSION,
        "status": "running",
        "env": settings.APP_ENV,
    }


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok"}