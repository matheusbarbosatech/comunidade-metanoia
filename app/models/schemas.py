"""Modelos Pydantic para validação e serialização de dados na API."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# --- Membros & Alunos ---
class MembroCreate(BaseModel):
    nome: str
    email: Optional[str] = None
    whatsapp: Optional[str] = None
    papel: str = "aluno"

class MembroResponse(MembroCreate):
    id: int
    ativo: bool
    criado_em: str

# --- Aulas e Estudos (Base do YouTube Longo) ---
class EstudoAulaCreate(BaseModel):
    trilha_id: Optional[int] = None
    codigo_aula: Optional[str] = None
    titulo: str
    texto_biblico: Optional[str] = None
    resumo_conteudo: Optional[str] = None
    video_youtube_url: Optional[str] = None
    status_estudo: str = "a_estudar"

class EstudoAulaResponse(EstudoAulaCreate):
    id: int
    criado_em: str

# --- Cortes de Vídeo (Shorts / Reels) ---
class CorteVideoCreate(BaseModel):
    aula_id: int
    titulo_corte: str
    hook: str
    timestamp_inicio: Optional[str] = None
    timestamp_fim: Optional[str] = None
    status: str = "planejado"

class CorteVideoResponse(CorteVideoCreate):
    id: int
    video_path: Optional[str] = None

# --- Pedidos de Oração ---
class PedidoOracaoCreate(BaseModel):
    nome_solicitante: str
    motivo: str
    categoria: str = "geral"
    anonimo: bool = False

class PedidoOracaoResponse(PedidoOracaoCreate):
    id: int
    status: str
    intercessoes_count: int
    criado_em: str

# --- Encontros de Célula ---
class EncontroCelulaCreate(BaseModel):
    tema: str
    data_hora: str
    link_sala: Optional[str] = None
    material_apoio: Optional[str] = None

class EncontroCelulaResponse(EncontroCelulaCreate):
    id: int
    realizado: bool
