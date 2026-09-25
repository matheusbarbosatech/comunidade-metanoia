"""Roteador FastAPI para o Acervo de Músicas & Louvores (Playlist Matheus)."""
import os
import re
from pathlib import Path
from typing import Optional, Generator
from fastapi import APIRouter, HTTPException, Query, Header, Request, status
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse

from app.services.music_service import (
    get_all_musicas,
    get_musica_by_id,
    toggle_favorito,
    increment_play_count,
    get_musicas_stats,
    sync_music_playlist
)

router = APIRouter(prefix="/musicas", tags=["Músicas & Louvores"])

@router.get("/")
def listar_musicas(
    categoria: Optional[str] = Query(None, description="Filtrar por categoria"),
    busca: Optional[str] = Query(None, description="Busca por termo no título, artista ou tags"),
    favoritos: bool = Query(False, description="Filtrar apenas favoritas")
):
    """Lista todas as faixas do acervo musical indexado."""
    faixas = get_all_musicas(categoria=categoria, busca=busca, apenas_favoritos=favoritos)
    return {
        "total": len(faixas),
        "categoria_filtrada": categoria or "Todas",
        "faixas": faixas
    }

@router.get("/stats")
def metricas_musicais():
    """Retorna estatísticas gerais da playlist e acervo ministerial."""
    return get_musicas_stats()

@router.post("/sync")
def sincronizar_playlist():
    """Varre o diretório da playlist local e sincroniza com o banco de dados."""
    total = sync_music_playlist()
    return {"mensagem": f"Sincronização concluída com sucesso! {total} faixas cadastradas/atualizadas."}

@router.get("/{musica_id}")
def obter_detalhes_musica(musica_id: int):
    """Obtém os detalhes cadastrais de uma faixa musical específica."""
    musica = get_musica_by_id(musica_id)
    if not musica:
        raise HTTPException(status_code=404, detail="Música não encontrada.")
    return musica

@router.post("/{musica_id}/favorito")
def favoritar_musica(musica_id: int):
    """Marca ou desmarca uma música como favorita."""
    status_favorito = toggle_favorito(musica_id)
    return {"id": musica_id, "favorito": status_favorito}

@router.post("/{musica_id}/play")
def registrar_reproducao(musica_id: int):
    """Registra uma reprodução da faixa."""
    increment_play_count(musica_id)
    return {"sucesso": True}

@router.get("/{musica_id}/stream")
def stream_audio(musica_id: int, request: Request):
    """Transmite o áudio MP3 com suporte oficial a requisições de intervalo (HTTP Range Requests).
    Permite busca imediata (seek) e reprodução fluida no navegador e player Flet.
    """
    musica = get_musica_by_id(musica_id)
    if not musica:
        raise HTTPException(status_code=404, detail="Música não encontrada.")

    caminho = Path(musica["caminho_completo"]) if musica.get("caminho_completo") else None
    if not caminho or not caminho.exists():
        # Fallback de Alta Performance para Nuvem (GitHub Releases CDN 24/7):
        import urllib.parse
        from fastapi.responses import RedirectResponse
        arquivo_nome = musica.get("arquivo_nome") or f"{musica['titulo']}.mp3"
        encoded_name = urllib.parse.quote(arquivo_nome)
        cdn_url = f"https://github.com/matheusbarbosatech/ministerio/releases/download/v1.0.0-louvores/{encoded_name}"
        return RedirectResponse(url=cdn_url, status_code=307)

    file_size = caminho.stat().st_size
    range_header = request.headers.get("range")

    if not range_header:
        # Se não há cabeçalho Range, retorna o arquivo completo
        return FileResponse(
            caminho,
            media_type="audio/mpeg",
            headers={"Accept-Ranges": "bytes"}
        )

    # Interpretação do Range Header (ex: 'bytes=0-1024' ou 'bytes=1024-')
    range_match = re.match(r"^bytes=(\d+)-(\d+)?$", range_header)
    if not range_match:
        return FileResponse(
            caminho,
            media_type="audio/mpeg",
            headers={"Accept-Ranges": "bytes"}
        )

    start = int(range_match.group(1))
    end = int(range_match.group(2)) if range_match.group(2) else file_size - 1

    if start >= file_size or end >= file_size:
        return HTTPException(
            status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE,
            detail="Intervalo solicitado inválido.",
            headers={"Content-Range": f"bytes */{file_size}"}
        )

    chunk_size = (end - start) + 1

    def iterfile() -> Generator[bytes, None, None]:
        with open(caminho, mode="rb") as f:
            f.seek(start)
            bytes_left = chunk_size
            while bytes_left > 0:
                read_size = min(bytes_left, 64 * 1024) # 64KB chunks
                data = f.read(read_size)
                if not data:
                    break
                bytes_left -= len(data)
                yield data

    headers = {
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Accept-Ranges": "bytes",
        "Content-Length": str(chunk_size),
        "Content-Type": "audio/mpeg",
    }

    return StreamingResponse(
        iterfile(),
        status_code=status.HTTP_206_PARTIAL_CONTENT,
        headers=headers
    )
