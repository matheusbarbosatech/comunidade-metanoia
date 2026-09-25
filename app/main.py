"""Ponto de entrada oficial do Backend Comunidade Metanoia.
Serve a Landing Page em '/', o Blog em '/blog', a Plataforma Flet em '/plataforma' e a API REST em '/api/v1'.
"""
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import APP_NAME, APP_VERSION, API_PREFIX
from app.db.database import init_db
from app.routers import estudos, oracao, celula, musica, blog, comunidade
from app.services.music_service import sync_music_playlist


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Plataforma oficial da Comunidade Metanoia // Acolhimento, Louvores 24h, Célula Digital e Escola Bíblica.",
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

# Inicializar Banco SQLite e Sincronizar Músicas + Blog no startup
@app.on_event("startup")
def on_startup():
    init_db()
    sync_music_playlist()
    try:
        blog.sync_blog_articles()
    except Exception as e:
        print(f"[AVISO] Falha ao sincronizar blog no startup: {e}")

# Incluir Roteadores REST API, Blog e Comunidade (Circle)
app.include_router(blog.router)
app.include_router(comunidade.router)
app.include_router(estudos.router, prefix=API_PREFIX)
app.include_router(oracao.router, prefix=API_PREFIX)
app.include_router(celula.router, prefix=API_PREFIX)
app.include_router(musica.router, prefix=API_PREFIX)


# Montar Plataforma Web Flet interativa em /plataforma
try:
    import flet.fastapi as flet_fastapi
    from app.flet_app import main as flet_main
    app.mount("/plataforma", flet_fastapi.app(flet_main))
    print("[OK] Plataforma Web Flet montada com sucesso em /plataforma")
except Exception as e:
    print(f"[AVISO] Flet Web não pôde ser montado em /plataforma: {e}")


# Landing Page de Apresentação em '/'
STATIC_INDEX = Path(__file__).resolve().parent / "static" / "index.html"
STATIC_TELEPROMPTER = Path(__file__).resolve().parent / "static" / "teleprompter.html"
STATIC_ESTUDIO = Path(__file__).resolve().parent / "static" / "estudio.html"

@app.get("/", response_class=HTMLResponse)
def index_landing():
    if STATIC_INDEX.exists():
        with open(STATIC_INDEX, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Comunidade Metanoia</h1><a href='/plataforma'>Acessar Plataforma</a>"

@app.get("/teleprompter", response_class=HTMLResponse)
def teleprompter_view():
    if STATIC_TELEPROMPTER.exists():
        with open(STATIC_TELEPROMPTER, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Teleprompter não encontrado</h1>"

@app.get("/estudio", response_class=HTMLResponse)
def estudio_web_view():
    """Estúdio Ministerial Web com câmera, cenário virtual, teleprompter e gravador."""
    if STATIC_ESTUDIO.exists():
        with open(STATIC_ESTUDIO, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Estúdio Web não encontrado</h1>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
