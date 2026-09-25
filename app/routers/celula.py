"""Rotas da Célula Digital: Encontros ao Vivo e Pastoreio."""
from fastapi import APIRouter, HTTPException
from typing import List
from app.db.database import get_connection
from app.models.schemas import EncontroCelulaCreate, EncontroCelulaResponse

router = APIRouter(prefix="/celula", tags=["Célula Digital & Encontros"])

@router.post("/encontros", response_model=EncontroCelulaResponse)
def agendar_encontro(encontro: EncontroCelulaCreate):
    """Agenda uma nova reunião da Célula Digital."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO encontros_celula (tema, data_hora, link_sala, material_apoio)
    VALUES (?, ?, ?, ?)
    """, (encontro.tema, encontro.data_hora, encontro.link_sala, encontro.material_apoio))
    conn.commit()
    encontro_id = cursor.lastrowid
    cursor.execute("SELECT * FROM encontros_celula WHERE id = ?", (encontro_id,))
    row = dict(cursor.fetchone())
    conn.close()
    return row

@router.get("/proximo", response_model=EncontroCelulaResponse)
def obter_proximo_encontro():
    """Retorna o próximo encontro agendado com link do Google Meet e material."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM encontros_celula WHERE realizado = 0 ORDER BY data_hora ASC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Nenhum encontro agendado no momento.")
    return dict(row)
