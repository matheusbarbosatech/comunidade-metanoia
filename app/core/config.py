"""Configurações centrais do sistema Ministério Metanoia."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "ministerio.db"

# Informações da Aplicação
APP_NAME = "Comunidade Metanoia // Ninguém Luta Sozinho"
APP_VERSION = "1.0.0"
API_PREFIX = "/api/v1"

# Diretório Oficial de Músicas / Louvores da Playlist
MUSIC_PLAYLIST_DIR = Path(r"C:\Users\matheus\Music\Playlist MATHEUS")

