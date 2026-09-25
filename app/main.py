"""Ponto de entrada oficial do Backend Ministério Metanoia."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import APP_NAME, APP_VERSION, API_PREFIX
from app.db.database import init_db
from app.routers import estudos, oracao, celula

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Backend oficial de Escola Bíblica, Discipulado, Célula Digital e Gestão Ministerial.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Habilitar CORS para permitir conexão com Web App, Desktop e Mobile
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

# Incluir Roteadores com Prefixo Oficial
app.include_router(estudos.router, prefix=API_PREFIX)
app.include_router(oracao.router, prefix=API_PREFIX)
app.include_router(celula.router, prefix=API_PREFIX)

@app.get("/")
def home():
    return {
        "status": "online",
        "ministério": "Metanoia // Altar, Ensino & Tecnologia",
        "versão": APP_VERSION,
        "documentacao": "/docs",
        "versiculo": "Romanos 12:2 — Transformai-vos pela renovação da vossa mente."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
