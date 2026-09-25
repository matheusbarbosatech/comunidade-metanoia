"""Rotas do Mural de Oração da Célula e Intercessão Pastoral."""
from fastapi import APIRouter, HTTPException
from typing import List
from app.db.database import get_connection
from app.models.schemas import PedidoOracaoCreate, PedidoOracaoResponse

router = APIRouter(prefix="/oracao", tags=["Mural de Oração & Intercessão"])

@router.post("/pedir", response_model=PedidoOracaoResponse)
def criar_pedido(pedido: PedidoOracaoCreate):
    """Envia um pedido de oração para o mural da célula ou para o pastor."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO pedidos_oracao (nome_solicitante, motivo, categoria, anonimo)
    VALUES (?, ?, ?, ?)
    """, (pedido.nome_solicitante, pedido.motivo, pedido.categoria, pedido.anonimo))
    conn.commit()
    pedido_id = cursor.lastrowid
    cursor.execute("SELECT * FROM pedidos_oracao WHERE id = ?", (pedido_id,))
    row = dict(cursor.fetchone())
    conn.close()
    return row

@router.get("/mural", response_model=List[PedidoOracaoResponse])
def listar_pedidos():
    """Lista todos os pedidos ativos no mural de oração."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pedidos_oracao WHERE status = 'em_oracao' ORDER BY id DESC")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows

@router.post("/interceder/{pedido_id}")
def interceder_por_pedido(pedido_id: int):
    """Incrementa a contagem de irmãos que oraram por este pedido específico."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE pedidos_oracao SET intercessoes_count = intercessoes_count + 1 WHERE id = ?", (pedido_id,))
    conn.commit()
    conn.close()
    return {"status": "sucesso", "mensagem": "Oração computada! Ninguém luta sozinho."}
