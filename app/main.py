"""Ponto de entrada oficial do Backend Ministério Metanoia.
Serve a Landing Page em '/', a Plataforma Flet em '/plataforma' e a API REST em '/api/v1'.
"""
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import flet.fastapi as flet_fastapi

from app.core.config import APP_NAME, APP_VERSION, API_PREFIX
from app.db.database import init_db
from app.routers import estudos, oracao, celula
from app.flet_app import main as flet_main

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Backend e Plataforma oficial de Escola Bíblica, Discipulado, Célula Digital e Gestão Ministerial.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar Banco SQLite no startup
@app.on_event("startup")
def on_startup():
    init_db()

# Incluir Roteadores REST API
app.include_router(estudos.router, prefix=API_PREFIX)
app.include_router(oracao.router, prefix=API_PREFIX)
app.include_router(celula.router, prefix=API_PREFIX)

# Montar Plataforma Web Flet interativa em /plataforma
app.mount("/plataforma", flet_fastapi.app(flet_main))

# Landing Page de Apresentação em '/'
STATIC_INDEX = Path(__file__).resolve().parent / "static" / "index.html"

@app.get("/", response_class=HTMLResponse)
def index_landing():
    if STATIC_INDEX.exists():
        with open(STATIC_INDEX, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Ministério Metanoia</h1><a href='/plataforma'>Acessar Plataforma</a>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
