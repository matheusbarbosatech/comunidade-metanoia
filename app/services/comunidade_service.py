"""Serviço de gerenciamento da Rede Social & Comunidade Metanoia (Estilo Circle.so).
Fornece canais temáticos (Espaços), feed social de publicações, interações comunitárias e comentários.
"""
from typing import List, Dict, Any, Optional
from app.db.database import get_connection

def get_espacos() -> List[Dict[str, Any]]:
    """Retorna todos os canais/espaços temáticos da comunidade com total de posts."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT e.*, COUNT(p.id) as total_posts
    FROM comunidade_espacos e
    LEFT JOIN comunidade_posts p ON p.espaco_id = e.id
    GROUP BY e.id
    ORDER BY e.ordem ASC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_posts(espaco_id: Optional[int] = None, busca: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retorna as publicações do feed com suporte a filtro por espaço e busca."""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT p.*, e.nome as espaco_nome, e.icone as espaco_icone, e.slug as espaco_slug
    FROM comunidade_posts p
    JOIN comunidade_espacos e ON e.id = p.espaco_id
    WHERE 1=1
    """
    params = []
    
    if espaco_id:
        query += " AND p.espaco_id = ?"
        params.append(espaco_id)
        
    if busca and busca.strip():
        query += " AND (p.titulo LIKE ? OR p.conteudo LIKE ? OR p.autor_nome LIKE ?)"
        term = f"%{busca.strip()}%"
        params.extend([term, term, term])
        
    query += " ORDER BY p.fixado DESC, p.id DESC"
    
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_post_com_detalhes(post_id: int) -> Optional[Dict[str, Any]]:
    """Retorna uma publicação com todos os seus comentários."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    SELECT p.*, e.nome as espaco_nome, e.icone as espaco_icone, e.slug as espaco_slug
    FROM comunidade_posts p
    JOIN comunidade_espacos e ON e.id = p.espaco_id
    WHERE p.id = ?
    """, (post_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
        
    post = dict(row)
    
    cursor.execute("""
    SELECT * FROM comunidade_comentarios
    WHERE post_id = ?
    ORDER BY id ASC
    """, (post_id,))
    post["comentarios"] = [dict(c) for c in cursor.fetchall()]
    conn.close()
    return post

def criar_post(
    espaco_id: int,
    autor_nome: str,
    conteudo: str,
    titulo: Optional[str] = None,
    autor_papel: str = "Discípulo",
    autor_avatar: str = "🕊️",
    anonimo: bool = False
) -> int:
    """Cria uma nova publicação na comunidade."""
    nome = "Irmão em Silêncio (Anônimo)" if anonimo else (autor_nome or "Discípulo Metanoia")
    avatar = "🕊️" if anonimo else (autor_avatar or "🕊️")
    papel = "Acolhido" if anonimo else autor_papel

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO comunidade_posts (espaco_id, autor_nome, autor_papel, autor_avatar, titulo, conteudo, anonimo)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (espaco_id, nome, papel, avatar, titulo, conteudo, 1 if anonimo else 0))
    post_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return post_id

def adicionar_comentario(
    post_id: int,
    autor_nome: str,
    conteudo: str,
    autor_papel: str = "Discípulo",
    autor_avatar: str = "🕊️",
    anonimo: bool = False
) -> int:
    """Adiciona um comentário a um post existente e atualiza a contagem."""
    nome = "Irmão Anônimo" if anonimo else (autor_nome or "Discípulo")
    avatar = "🕊️" if anonimo else (autor_avatar or "🕊️")
    papel = "Acolhido" if anonimo else autor_papel

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO comunidade_comentarios (post_id, autor_nome, autor_papel, autor_avatar, conteudo, anonimo)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (post_id, nome, papel, avatar, conteudo, 1 if anonimo else 0))
    comentario_id = cursor.lastrowid

    cursor.execute("""
    UPDATE comunidade_posts
    SET comentarios_count = comentarios_count + 1
    WHERE id = ?
    """, (post_id,))
    conn.commit()
    conn.close()
    return comentario_id

def reagir_post(post_id: int, tipo: str = "orando", usuario_id: Optional[str] = None) -> int:
    """Registra uma reação ao post ('orando', 'amem', 'gloria') e incrementa o contador."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO comunidade_reacoes (post_id, tipo, usuario_identificador)
    VALUES (?, ?, ?)
    """, (post_id, tipo, usuario_id or "visitante"))

    cursor.execute("""
    UPDATE comunidade_posts
    SET likes_count = likes_count + 1
    WHERE id = ?
    """, (post_id,))
    conn.commit()

    cursor.execute("SELECT likes_count FROM comunidade_posts WHERE id = ?", (post_id,))
    row = cursor.fetchone()
    total = row["likes_count"] if row else 0
    conn.close()
    return total
