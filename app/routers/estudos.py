"""Rotas da Escola Bíblica e Planejamento de Gravação de Vídeos Longos."""
from fastapi import APIRouter, HTTPException
from typing import List
from app.db.database import get_connection
from app.models.schemas import EstudoAulaCreate, EstudoAulaResponse, CorteVideoCreate, CorteVideoResponse

router = APIRouter(prefix="/estudos", tags=["Estudos Teológicos & Produção de Vídeos"])

@router.get("/trilhas")
def listar_trilhas():
    """Lista as matérias teológicas (inspiradas na Academia de Pregadores)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM trilhas_teologicas ORDER BY id ASC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

@router.post("/aulas", response_model=EstudoAulaResponse)
def criar_estudo_aula(aula: EstudoAulaCreate):
    """Cadastra um novo estudo ou aula planejada para gravação no YouTube."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO estudos_aulas (trilha_id, codigo_aula, titulo, texto_biblico, resumo_conteudo, video_youtube_url, status_estudo)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (aula.trilha_id, aula.codigo_aula, aula.titulo, aula.texto_biblico, aula.resumo_conteudo, aula.video_youtube_url, aula.status_estudo))
    conn.commit()
    aula_id = cursor.lastrowid
    cursor.execute("SELECT * FROM estudos_aulas WHERE id = ?", (aula_id,))
    row = dict(cursor.fetchone())
    conn.close()
    return row

@router.get("/aulas", response_model=List[EstudoAulaResponse])
def listar_aulas(status: str = None):
    """Lista as aulas cadastradas filtradas por status (a_estudar, estudado, gravado)."""
    conn = get_connection()
    cursor = conn.cursor()
    if status:
        cursor.execute("SELECT * FROM estudos_aulas WHERE status_estudo = ? ORDER BY id DESC", (status,))
    else:
        cursor.execute("SELECT * FROM estudos_aulas ORDER BY id DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

@router.post("/cortes", response_model=CorteVideoResponse)
def registrar_corte(corte: CorteVideoCreate):
    """Registra um corte de ouro extraído de uma aula longa para Reels/TikTok/Shorts."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO cortes_videos (aula_id, titulo_corte, hook, timestamp_inicio, timestamp_fim, status)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (corte.aula_id, corte.titulo_corte, corte.hook, corte.timestamp_inicio, corte.timestamp_fim, corte.status))
    conn.commit()
    corte_id = cursor.lastrowid
    cursor.execute("SELECT * FROM cortes_videos WHERE id = ?", (corte_id,))
    row = dict(cursor.fetchone())
    conn.close()
    return row
