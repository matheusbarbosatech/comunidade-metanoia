"""Serviço de gerenciamento, sincronização e streaming da Playlist Ministerial Matheus.
Indexa músicas locais em C:\\Users\\matheus\\Music\\Playlist MATHEUS no banco SQLite.
"""
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.core.config import MUSIC_PLAYLIST_DIR
from app.db.database import get_connection

def parse_track_info(filename: str) -> tuple[str, str, str, str]:
    """Extrai Artista, Título, Categoria e Tags a partir do nome do arquivo MP3."""
    name = filename.rsplit('.', 1)[0]
    
    # Detecção de Artista e Título
    if ' - ' in name:
        parts = name.split(' - ', 1)
        if any(a in parts[1] for a in ['Nesk Only', '2metro', 'Brunno Ramos', 'VICTIN']):
            title = parts[0].strip()
            artist = parts[1].strip()
        else:
            artist = parts[0].strip()
            title = parts[1].strip()
    else:
        artist = '2metro & Nesk Only / Urban Worship'
        title = name.strip()

    # Normalizar pontuação e limpar ruídos
    title_clean = title.replace('（', '(').replace('）', ')').replace('｜', '|').replace('⧸', '/')
    
    lower = (title + ' ' + filename).lower()
    tags = []

    # Categorização inteligente para o Ministério Metanoia
    if any(k in lower for k in ['oracao', 'oração', 'abba', 'contempla', 'fervente', 'shekinah', 'teu amor', 'pela manhã', 'toque']):
        categoria = 'Oração & Adoração'
        tags.extend(['intimidade', 'clamor', 'espírito santo', 'quebrantamento'])
    elif any(k in lower for k in ['hebreus', 'efésios', 'efesios', 'vigia', 'coroa', 'guardado', 'atento', 'conquista', 'arão', 'josué', 'davi', 'escudo']):
        categoria = 'Guerra Espiritual & Fé'
        tags.extend(['armadura de deus', 'batalha', 'firmeza', 'propósito', 'vitória'])
    elif any(k in lower for k in ['bartimeu', 'mefibosete', 'samaritano', 'amor de deus', 'chuvas', 'abençoado', 'abencoado', 'cristo']):
        categoria = 'Graça & Restauração'
        tags.extend(['cura', 'perdão', 'graça', 'acolhimento', 'filho pródigo'])
    elif any(k in lower for k in ['medley', 'pentecostal', 'vitoria', 'vitória', 'sobrenatural']):
        categoria = 'Pentecostal & Celebração'
        tags.extend(['avivamento', 'fogo', 'alegria', 'louvor raiz'])
    else:
        categoria = 'Trap Gospel & Edificação'
        tags.extend(['juventude', 'metanoia', 'discipulado', 'evangelho nas ruas'])

    return artist, title_clean, categoria, ', '.join(tags)

def sync_music_playlist() -> int:
    """Escaneia a pasta física da Playlist e cadastra/atualiza as faixas no SQLite.
    Se estiver em ambiente de nuvem (Render) onde a pasta local C:\ não existe,
    carrega as 50 faixas com metadados a partir do musicas_seed.json.
    """
    conn = get_connection()
    cursor = conn.cursor()

    seed_file = Path(__file__).resolve().parent.parent / "static" / "musicas_seed.json"
    if not MUSIC_PLAYLIST_DIR.exists():
        if seed_file.exists():
            try:
                import json
                with open(seed_file, "r", encoding="utf-8") as sf:
                    faixas_seed = json.load(sf)
                cadastrados = 0
                for item in faixas_seed:
                    cursor.execute("""
                    INSERT INTO musicas_louvores (
                        id, titulo, artista, arquivo_nome, caminho_completo, tamanho_mb, categoria, tags, cdn_url
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(arquivo_nome) DO UPDATE SET
                        cdn_url = excluded.cdn_url,
                        tamanho_mb = excluded.tamanho_mb,
                        categoria = excluded.categoria
                    """, (
                        item.get("id"),
                        item.get("titulo"),
                        item.get("artista"),
                        item.get("arquivo_nome", f"{item.get('titulo')}.mp3"),
                        "",
                        item.get("tamanho_mb", 0),
                        item.get("categoria", "Geral"),
                        "",
                        item.get("cdn_url", "")
                    ))
                    cadastrados += 1
                conn.commit()
                conn.close()
                return cadastrados
            except Exception as e:
                print(f"[AVISO] Falha ao carregar seed de músicas: {e}")
        conn.close()
        return 0

    import unicodedata, re
    arquivos = list(MUSIC_PLAYLIST_DIR.glob("*.mp3"))
    cadastrados = 0

    for f in arquivos:
        try:
            stat = f.stat()
            tamanho_mb = round(stat.st_size / (1024 * 1024), 2)
            artist, title, categoria, tags = parse_track_info(f.name)
            
            clean = unicodedata.normalize('NFKD', f.name).encode('ASCII', 'ignore').decode('ASCII')
            clean = re.sub(r'[^a-zA-Z0-9._-]', '.', clean)
            clean = re.sub(r'\.+', '.', clean)
            cdn_url = f"https://github.com/matheusbarbosatech/ministerio/releases/download/v1.0.0-louvores/{clean}"

            cursor.execute("""
            INSERT INTO musicas_louvores (
                titulo, artista, arquivo_nome, caminho_completo, tamanho_mb, categoria, tags, cdn_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(arquivo_nome) DO UPDATE SET
                caminho_completo = excluded.caminho_completo,
                tamanho_mb = excluded.tamanho_mb,
                categoria = excluded.categoria,
                tags = excluded.tags,
                cdn_url = excluded.cdn_url
            """, (title, artist, f.name, str(f), tamanho_mb, categoria, tags, cdn_url))
            cadastrados += 1
        except Exception as e:
            print(f"Erro ao processar arquivo {f.name}: {e}")

    conn.commit()
    conn.close()
    return cadastrados

def get_all_musicas(
    categoria: Optional[str] = None,
    busca: Optional[str] = None,
    apenas_favoritos: bool = False
) -> List[Dict[str, Any]]:
    """Consulta músicas com suporte a busca, filtros e ordenação."""
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM musicas_louvores WHERE 1=1"
    params: List[Any] = []

    if categoria and categoria != 'Todos':
        query += " AND categoria = ?"
        params.append(categoria)

    if apenas_favoritos:
        query += " AND favorito = 1"

    if busca:
        query += " AND (titulo LIKE ? OR artista LIKE ? OR tags LIKE ?)"
        termo = f"%{busca}%"
        params.extend([termo, termo, termo])

    query += " ORDER BY categoria ASC, titulo ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(r) for r in rows]

def get_musica_by_id(musica_id: int) -> Optional[Dict[str, Any]]:
    """Retorna detalhes de uma música pelo ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM musicas_louvores WHERE id = ?", (musica_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def toggle_favorito(musica_id: int) -> bool:
    """Inverte o status de favorito de uma música."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT favorito FROM musicas_louvores WHERE id = ?", (musica_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return False

    novo_status = 0 if row["favorito"] else 1
    cursor.execute("UPDATE musicas_louvores SET favorito = ? WHERE id = ?", (novo_status, musica_id))
    conn.commit()
    conn.close()
    return bool(novo_status)

def increment_play_count(musica_id: int) -> None:
    """Registra uma reprodução para estatísticas ministeriais."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE musicas_louvores SET reproducoes_count = reproducoes_count + 1 WHERE id = ?", (musica_id,))
    conn.commit()
    conn.close()

def get_musicas_stats() -> Dict[str, Any]:
    """Retorna métricas gerais do repertório."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total, SUM(tamanho_mb) as total_mb, SUM(favorito) as favoritos FROM musicas_louvores")
    geral = dict(cursor.fetchone())

    cursor.execute("SELECT categoria, COUNT(*) as qtd FROM musicas_louvores GROUP BY categoria")
    por_categoria = {r["categoria"]: r["qtd"] for r in cursor.fetchall()}

    conn.close()
    return {
        "total_faixas": geral["total"] or 0,
        "total_mb": round(geral["total_mb"] or 0, 1),
        "favoritos": geral["favoritos"] or 0,
        "por_categoria": por_categoria
    }
