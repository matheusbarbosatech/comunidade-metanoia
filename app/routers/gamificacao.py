"""Roteador REST API da Trilha Gamificada Bíblica (Módulo 01 - Introdução à Teologia)."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services import gamificacao_service

router = APIRouter(prefix="/gamificacao", tags=["Trilha Gamificada // Duolingo Teológico"])

class RespostaQuizSchema(BaseModel):
    codigo_aula: str
    resposta: str

@router.get("/modulo1")
def obter_modulo1():
    """Retorna o progresso atual, os 3 mundos e as 15 aulas da Trilha Gamificada."""
    return gamificacao_service.get_modulo1_data()

@router.post("/responder")
def enviar_resposta_quiz(payload: RespostaQuizSchema):
    """Envia a resposta de uma questão para validação e ganho de XP."""
    resultado = gamificacao_service.responder_quiz(payload.codigo_aula, payload.resposta)
    if not resultado.get("sucesso"):
        raise HTTPException(status_code=404, detail=resultado.get("mensagem"))
    return resultado
