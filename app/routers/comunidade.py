"""Roteador da Rede Social / Comunidade Metanoia (Estilo Circle.so).
Fornece tanto os endpoints REST em /api/v1/comunidade quanto a visualização Web completa em /comunidade.
"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from app.services import comunidade_service

router = APIRouter(tags=["Comunidade // Rede Social"])

# Schemas Pydantic
class PostCreateSchema(BaseModel):
    espaco_id: int
    autor_nome: str
    conteudo: str
    titulo: Optional[str] = None
    autor_papel: Optional[str] = "Discípulo"
    autor_avatar: Optional[str] = "🕊️"
    anonimo: Optional[bool] = False

class ComentarioCreateSchema(BaseModel):
    autor_nome: str
    conteudo: str
    autor_papel: Optional[str] = "Discípulo"
    autor_avatar: Optional[str] = "🕊️"
    anonimo: Optional[bool] = False

class ReacaoSchema(BaseModel):
    tipo: Optional[str] = "orando"
    usuario_id: Optional[str] = None


# --- ENDPOINTS REST API ---

@router.get("/api/v1/comunidade/espacos")
def listar_espacos():
    """Lista todos os canais e espaços temáticos da comunidade."""
    return comunidade_service.get_espacos()

@router.get("/api/v1/comunidade/posts")
def listar_posts(espaco_id: Optional[int] = None, q: Optional[str] = None):
    """Lista as publicações do feed com suporte a filtro por espaço e busca."""
    return comunidade_service.get_posts(espaco_id=espaco_id, busca=q)

@router.get("/api/v1/comunidade/posts/{post_id}")
def obter_post(post_id: int):
    """Retorna detalhes da publicação com lista de comentários."""
    post = comunidade_service.get_post_com_detalhes(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Publicação não encontrada.")
    return post

@router.post("/api/v1/comunidade/posts")
def publicar_post(payload: PostCreateSchema):
    """Cria uma nova publicação na comunidade."""
    if not payload.conteudo.strip():
        raise HTTPException(status_code=400, detail="O conteúdo não pode estar vazio.")
    post_id = comunidade_service.criar_post(
        espaco_id=payload.espaco_id,
        autor_nome=payload.autor_nome,
        conteudo=payload.conteudo,
        titulo=payload.titulo,
        autor_papel=payload.autor_papel or "Discípulo",
        autor_avatar=payload.autor_avatar or "🕊️",
        anonimo=bool(payload.anonimo)
    )
    return {"status": "sucesso", "post_id": post_id, "mensagem": "Publicado com sucesso na comunidade!"}

@router.post("/api/v1/comunidade/posts/{post_id}/reagir")
def reagir_post(post_id: int, payload: Optional[ReacaoSchema] = None):
    """Registra uma oração/amém no post e retorna o total atualizado."""
    tipo = payload.tipo if payload else "orando"
    uid = payload.usuario_id if payload else None
    novo_total = comunidade_service.reagir_post(post_id, tipo=tipo, usuario_id=uid)
    return {"status": "sucesso", "post_id": post_id, "likes_count": novo_total}

@router.post("/api/v1/comunidade/posts/{post_id}/comentarios")
def comentar_post(post_id: int, payload: ComentarioCreateSchema):
    """Adiciona um comentário à publicação."""
    if not payload.conteudo.strip():
        raise HTTPException(status_code=400, detail="O comentário não pode estar vazio.")
    cid = comunidade_service.adicionar_comentario(
        post_id=post_id,
        autor_nome=payload.autor_nome,
        conteudo=payload.conteudo,
        autor_papel=payload.autor_papel or "Discípulo",
        autor_avatar=payload.autor_avatar or "🕊️",
        anonimo=bool(payload.anonimo)
    )
    return {"status": "sucesso", "comentario_id": cid, "mensagem": "Comentário registrado!"}


# --- INTERFACE WEB COMPLETA DA COMUNIDADE CIRCLE (HTML) ---

@router.get("/comunidade", response_class=HTMLResponse)
def interface_comunidade(espaco: Optional[int] = None):
    """Página completa da Rede Social Ministerial inspirada no Circle.so."""
    espacos = comunidade_service.get_espacos()
    posts = comunidade_service.get_posts(espaco_id=espaco)
    espaco_atual = next((e for e in espacos if e["id"] == espaco), None) if espaco else None

    # Renderizar links de espaços na sidebar
    html_espacos = ""
    for e in espacos:
        ativo_class = "active" if (espaco == e["id"]) else ""
        html_espacos += f"""
        <a href="/comunidade?espaco={e['id']}" class="space-item {ativo_class}">
            <span class="space-icon">{e['icone']}</span>
            <span class="space-title">{e['nome']}</span>
            <span class="space-count">{e['total_posts']}</span>
        </a>
        """

    # Renderizar posts no feed
    html_posts = ""
    if not posts:
        html_posts = """
        <div class="empty-feed">
            <div style="font-size: 40px; margin-bottom: 12px;">🕊️</div>
            <h3>Nenhuma publicação neste espaço ainda</h3>
            <p>Seja o primeiro a compartilhar uma palavra, oração ou testemunho com os irmãos!</p>
        </div>
        """
    else:
        for p in posts:
            pin_badge = '<span class="post-pinned">📌 FIXADO PELO PASTOR</span>' if p["fixado"] else ""
            titulo_html = f'<h3 class="post-title">{p["titulo"]}</h3>' if p.get("titulo") else ""
            comentarios = comunidade_service.get_post_com_detalhes(p["id"])
            comentarios_list = comentarios["comentarios"] if comentarios else []
            
            html_comentarios = ""
            for c in comentarios_list:
                html_comentarios += f"""
                <div class="comment-bubble">
                    <div class="comment-author">
                        <span class="comment-avatar">{c['autor_avatar']}</span>
                        <strong>{c['autor_nome']}</strong>
                        <span class="comment-role">{c['autor_papel']}</span>
                    </div>
                    <div class="comment-text">{c['conteudo']}</div>
                </div>
                """

            html_posts += f"""
            <article class="post-card" id="post-{p['id']}">
                <div class="post-header">
                    <div class="author-block">
                        <div class="author-avatar">{p['autor_avatar']}</div>
                        <div>
                            <div class="author-name">
                                {p['autor_nome']}
                                <span class="author-badge">{p['autor_papel']}</span>
                            </div>
                            <div class="post-meta">
                                <span>{p['espaco_icone']} {p['espaco_nome']}</span> • <span>Há pouco</span>
                            </div>
                        </div>
                    </div>
                    {pin_badge}
                </div>

                <div class="post-body">
                    {titulo_html}
                    <p class="post-text">{p['conteudo']}</p>
                </div>

                <div class="post-actions">
                    <button class="btn-action" onclick="reagirPost({p['id']})">
                        🤍 <span>Estou Orando</span> (<span id="likes-{p['id']}">{p['likes_count']}</span>)
                    </button>
                    <button class="btn-action" onclick="toggleComentarios({p['id']})">
                        💬 <span>Comentários</span> (<span id="count-com-{p['id']}">{p['comentarios_count']}</span>)
                    </button>
                    <button class="btn-action" onclick="compartilharPost({p['id']})">
                        🔗 <span>Compartilhar</span>
                    </button>
                </div>

                <!-- Seção retrátil de comentários -->
                <div class="comments-section" id="comentarios-{p['id']}" style="display: none;">
                    <div class="comments-list" id="lista-com-{p['id']}">
                        {html_comentarios}
                    </div>
                    <div class="comment-input-box">
                        <input type="text" id="input-autor-{p['id']}" placeholder="Seu nome (ou deixe vazio p/ Anônimo)" class="input-mini">
                        <div style="display: flex; gap: 8px;">
                            <input type="text" id="input-com-{p['id']}" placeholder="Escreva uma palavra de bênção ou resposta..." class="input-com" onkeypress="if(event.key==='Enter') enviarComentario({p['id']})">
                            <button class="btn-enviar-com" onclick="enviarComentario({p['id']})">Enviar</button>
                        </div>
                    </div>
                </div>
            </article>
            """

    titulo_espaco = espaco_atual["nome"] if espaco_atual else "Todas as Publicações"
    desc_espaco = espaco_atual["descricao"] if espaco_atual else "Feed unificado da Comunidade Metanoia. Ninguém luta sozinho!"

    return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comunidade Metanoia // Rede Social Cristã (Estilo Circle)</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;1,400&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-base: #090B10;
            --bg-surface: #10131A;
            --bg-card: #151922;
            --bg-card-hover: #1A202C;
            --border-subtle: rgba(255, 255, 255, 0.08);
            --gold-primary: #F59E0B;
            --gold-hover: #D97706;
            --text-title: #F8FAFC;
            --text-body: #CBD5E1;
            --text-muted: #64748B;
            --flame: #EA580C;
        }}
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: var(--bg-base);
            color: var(--text-body);
            font-family: 'Plus Jakarta Sans', sans-serif;
            min-height: 100vh;
        }}

        /* HEADER */
        header.circle-header {{
            position: sticky;
            top: 0;
            z-index: 100;
            background: rgba(9, 11, 16, 0.88);
            backdrop-filter: blur(16px);
            border-bottom: 1px solid var(--border-subtle);
            padding: 12px 32px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .brand {{
            display: flex;
            align-items: center;
            gap: 12px;
            text-decoration: none;
        }}
        .brand-logo {{
            width: 38px;
            height: 38px;
            border-radius: 10px;
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.25), rgba(234, 88, 12, 0.15));
            border: 1px solid rgba(245, 158, 11, 0.4);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }}
        .brand-title {{
            font-family: 'Playfair Display', serif;
            font-size: 19px;
            font-weight: 700;
            color: var(--text-title);
        }}
        .brand-sub {{
            font-size: 11px;
            color: var(--gold-primary);
            text-transform: uppercase;
            letter-spacing: 0.8px;
            font-weight: 600;
        }}
        .header-links {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .btn-link {{
            color: var(--text-muted);
            text-decoration: none;
            font-size: 13px;
            font-weight: 600;
            padding: 8px 14px;
            border-radius: 30px;
            transition: all 0.2s;
        }}
        .btn-link:hover {{
            color: #FFF;
            background: rgba(255, 255, 255, 0.05);
        }}
        .btn-plat {{
            background: linear-gradient(135deg, var(--gold-primary), var(--gold-hover));
            color: #000;
            font-weight: 700;
            padding: 8px 18px;
            border-radius: 30px;
            text-decoration: none;
            font-size: 13px;
            transition: transform 0.2s;
        }}
        .btn-plat:hover {{
            transform: translateY(-1px);
        }}

        /* LAYOUT 3 COLUNAS CIRCLE.SO */
        .circle-layout {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 24px;
            display: grid;
            grid-template-columns: 280px 1fr 300px;
            gap: 24px;
            align-items: start;
        }}

        /* SIDEBAR ESQUERDA: ESPAÇOS / CANAIS */
        .sidebar-spaces {{
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: 16px;
            padding: 18px;
            position: sticky;
            top: 76px;
        }}
        .sidebar-title {{
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 700;
            color: var(--gold-primary);
            margin-bottom: 14px;
            display: flex;
            align-items: center;
            gap: 6px;
        }}
        .space-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 12px;
            border-radius: 10px;
            color: var(--text-body);
            text-decoration: none;
            font-size: 13.5px;
            font-weight: 500;
            margin-bottom: 4px;
            transition: all 0.2s;
        }}
        .space-item:hover {{
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-title);
        }}
        .space-item.active {{
            background: rgba(245, 158, 11, 0.15);
            border: 1px solid rgba(245, 158, 11, 0.3);
            color: var(--gold-primary);
            font-weight: 700;
        }}
        .space-icon {{ font-size: 16px; }}
        .space-title {{ flex: 1; }}
        .space-count {{
            font-size: 11px;
            background: rgba(255, 255, 255, 0.08);
            padding: 2px 7px;
            border-radius: 10px;
            color: var(--text-muted);
        }}

        /* FEED CENTRAL */
        .feed-container {{
            display: flex;
            flex-direction: column;
            gap: 20px;
        }}
        .feed-banner {{
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(234, 88, 12, 0.05));
            border: 1px solid rgba(245, 158, 11, 0.2);
            border-radius: 16px;
            padding: 20px 24px;
        }}
        .feed-banner h2 {{
            color: var(--text-title);
            font-size: 20px;
            margin-bottom: 6px;
            font-family: 'Playfair Display', serif;
        }}
        .feed-banner p {{
            color: var(--text-muted);
            font-size: 13.5px;
        }}

        /* CAIXA DE CRIAÇÃO DE POST (CIRCLE COMPOSER) */
        .post-composer {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 16px;
            padding: 20px;
        }}
        .composer-header {{
            font-size: 14px;
            font-weight: 700;
            color: var(--text-title);
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .composer-input-title {{
            width: 100%;
            background: rgba(0, 0, 0, 0.25);
            border: 1px solid var(--border-subtle);
            border-radius: 8px;
            padding: 10px 14px;
            color: #FFF;
            font-size: 14px;
            margin-bottom: 10px;
            font-family: inherit;
        }}
        .composer-textarea {{
            width: 100%;
            background: rgba(0, 0, 0, 0.25);
            border: 1px solid var(--border-subtle);
            border-radius: 8px;
            padding: 12px 14px;
            color: #FFF;
            font-size: 14px;
            min-height: 80px;
            resize: vertical;
            margin-bottom: 12px;
            font-family: inherit;
        }}
        .composer-textarea:focus, .composer-input-title:focus {{
            outline: none;
            border-color: var(--gold-primary);
        }}
        .composer-footer {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            flex-wrap: wrap;
        }}
        .composer-select {{
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            color: var(--text-body);
            padding: 8px 12px;
            border-radius: 8px;
            font-size: 13px;
        }}
        .btn-publish {{
            background: linear-gradient(135deg, var(--gold-primary), var(--gold-hover));
            color: #000;
            border: none;
            padding: 9px 20px;
            border-radius: 8px;
            font-weight: 700;
            cursor: pointer;
            font-size: 13px;
            transition: all 0.2s;
        }}
        .btn-publish:hover {{
            box-shadow: 0 0 16px rgba(245, 158, 11, 0.4);
            transform: translateY(-1px);
        }}

        /* POST CARD */
        .post-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-subtle);
            border-radius: 16px;
            padding: 22px;
            transition: border-color 0.2s;
        }}
        .post-card:hover {{
            border-color: rgba(245, 158, 11, 0.25);
        }}
        .post-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 14px;
        }}
        .author-block {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .author-avatar {{
            width: 42px;
            height: 42px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.06);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            border: 1px solid var(--border-subtle);
        }}
        .author-name {{
            font-size: 14.5px;
            font-weight: 700;
            color: var(--text-title);
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .author-badge {{
            font-size: 10.5px;
            padding: 2px 8px;
            border-radius: 12px;
            background: rgba(245, 158, 11, 0.15);
            color: var(--gold-primary);
            font-weight: 600;
        }}
        .post-meta {{
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 2px;
        }}
        .post-pinned {{
            font-size: 11px;
            font-weight: 700;
            color: var(--gold-primary);
            background: rgba(245, 158, 11, 0.15);
            border: 1px solid rgba(245, 158, 11, 0.3);
            padding: 4px 10px;
            border-radius: 20px;
        }}
        .post-title {{
            font-size: 17px;
            font-weight: 700;
            color: var(--text-title);
            margin-bottom: 10px;
            line-height: 1.35;
        }}
        .post-text {{
            font-size: 14.5px;
            line-height: 1.6;
            color: #E2E8F0;
            white-space: pre-wrap;
            margin-bottom: 16px;
        }}
        .post-actions {{
            display: flex;
            align-items: center;
            gap: 8px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            padding-top: 14px;
        }}
        .btn-action {{
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--border-subtle);
            color: var(--text-body);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12.5px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        .btn-action:hover {{
            background: rgba(245, 158, 11, 0.15);
            color: var(--gold-primary);
            border-color: rgba(245, 158, 11, 0.4);
        }}

        /* SEÇÃO DE COMENTÁRIOS */
        .comments-section {{
            margin-top: 16px;
            border-top: 1px dashed rgba(255, 255, 255, 0.1);
            padding-top: 16px;
        }}
        .comment-bubble {{
            background: rgba(0, 0, 0, 0.25);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 12px 14px;
            margin-bottom: 10px;
        }}
        .comment-author {{
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 12.5px;
            color: var(--text-title);
            margin-bottom: 4px;
        }}
        .comment-role {{
            font-size: 10px;
            color: var(--gold-primary);
            background: rgba(245, 158, 11, 0.1);
            padding: 1px 6px;
            border-radius: 6px;
        }}
        .comment-text {{
            font-size: 13.5px;
            color: var(--text-body);
            line-height: 1.45;
        }}
        .comment-input-box {{
            margin-top: 12px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .input-mini {{
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid var(--border-subtle);
            border-radius: 8px;
            padding: 6px 12px;
            color: #FFF;
            font-size: 12px;
        }}
        .input-com {{
            flex: 1;
            background: rgba(0, 0, 0, 0.3);
            border: 1px solid var(--border-subtle);
            border-radius: 8px;
            padding: 8px 12px;
            color: #FFF;
            font-size: 13px;
        }}
        .input-com:focus {{ outline: none; border-color: var(--gold-primary); }}
        .btn-enviar-com {{
            background: var(--gold-primary);
            color: #000;
            border: none;
            padding: 8px 16px;
            border-radius: 8px;
            font-weight: 700;
            cursor: pointer;
            font-size: 12.5px;
        }}

        /* SIDEBAR DIREITA: ATIVIDADES & REGRAS */
        .sidebar-right {{
            display: flex;
            flex-direction: column;
            gap: 20px;
            position: sticky;
            top: 76px;
        }}
        .widget-card {{
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            border-radius: 16px;
            padding: 18px;
        }}
        .widget-title {{
            font-size: 13px;
            font-weight: 700;
            color: var(--text-title);
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .widget-text {{
            font-size: 13px;
            color: var(--text-muted);
            line-height: 1.5;
        }}
        .pill-badge {{
            display: inline-block;
            background: rgba(16, 185, 129, 0.15);
            color: #6EE7B7;
            border: 1px solid rgba(16, 185, 129, 0.3);
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            margin-top: 8px;
        }}

        @media (max-width: 1024px) {{
            .circle-layout {{
                grid-template-columns: 240px 1fr;
            }}
            .sidebar-right {{ display: none; }}
        }}
        @media (max-width: 768px) {{
            .circle-layout {{
                grid-template-columns: 1fr;
                padding: 16px;
            }}
            .sidebar-spaces {{ position: static; }}
        }}
    </style>
</head>
<body>

    <header class="circle-header">
        <a href="/" class="brand">
            <div class="brand-logo">🕊️</div>
            <div>
                <div class="brand-title">Comunidade Metanoia</div>
                <div class="brand-sub">Rede Social Fraternal // Circle Hub</div>
            </div>
        </a>
        <div class="header-links">
            <a href="/" class="btn-link">← Voltar ao Início</a>
            <a href="/plataforma" class="btn-plat">Acessar App Completo</a>
        </div>
    </header>

    <main class="circle-layout">
        <!-- SIDEBAR DE CANAIS / ESPAÇOS -->
        <aside class="sidebar-spaces">
            <div class="sidebar-title">
                <span>CANAL & ESPAÇOS</span>
            </div>
            <a href="/comunidade" class="space-item {'active' if not espaco else ''}">
                <span class="space-icon">🌐</span>
                <span class="space-title">Todos os Espaços</span>
            </a>
            {html_espacos}
        </aside>

        <!-- FEED CENTRAL -->
        <section class="feed-container">
            <div class="feed-banner">
                <h2>{titulo_espaco}</h2>
                <p>{desc_espaco}</p>
            </div>

            <!-- COMPOSER DE POSTAGEM -->
            <div class="post-composer">
                <div class="composer-header">
                    <span>✍️ Compartilhar com a Comunidade</span>
                </div>
                <input type="text" id="post-title" class="composer-input-title" placeholder="Título opcional (ex: Motivo de Oração, Reflexão de Hoje...)">
                <textarea id="post-content" class="composer-textarea" placeholder="O que Deus colocou no seu coração hoje? Peça oração, compartilhe uma vitória ou deixe uma palavra..."></textarea>
                <div class="composer-footer">
                    <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
                        <select id="post-space" class="composer-select">
                            {"".join([f'<option value="{e["id"]}" {"selected" if (espaco==e["id"]) else ""}>{e["icone"]} {e["nome"]}</option>' for e in espacos])}
                        </select>
                        <input type="text" id="post-author" class="input-mini" placeholder="Seu Nome (ou vazio p/ Anônimo)" style="width: 170px;">
                    </div>
                    <button class="btn-publish" onclick="publicarPost()">Publicar na Comunidade →</button>
                </div>
            </div>

            <!-- FEED DE POSTS -->
            <div id="posts-list">
                {html_posts}
            </div>
        </section>

        <!-- SIDEBAR DIREITA -->
        <aside class="sidebar-right">
            <div class="widget-card">
                <div class="widget-title">
                    <span>🕊️ "Ninguém Luta Sozinho"</span>
                </div>
                <p class="widget-text">
                    Nossa comunidade é um hospital de acolhimento e uma escola bíblica. Aqui você é amado, ouvido e sustentado em oração diária.
                </p>
                <div class="pill-badge">🟢 Intercessores Online</div>
            </div>

            <div class="widget-card">
                <div class="widget-title">
                    <span>📻 Rádio Web 24h</span>
                </div>
                <p class="widget-text">
                    Louvores contínuos de adoração e quebra de cadeias sem comerciais para trazer paz ao seu dia.
                </p>
                <a href="/#btn-radio-web" class="btn-plat" style="display: block; text-align: center; margin-top: 10px; font-size: 12px;">Ouvir Rádio Web</a>
            </div>

            <div class="widget-card">
                <div class="widget-title">
                    <span>🛡️ Princípios de Convivência</span>
                </div>
                <p class="widget-text" style="font-size: 12px;">
                    • Respeito e mansidão mútua<br>
                    • Sigilo com pedidos de oração<br>
                    • Sem julgamentos sobre fraquezas humanas<br>
                    • Cristo como nosso único centro
                </p>
            </div>
        </aside>
    </main>

    <script>
        async function publicarPost() {{
            const conteudo = document.getElementById('post-content').value.trim();
            const titulo = document.getElementById('post-title').value.trim();
            const espacoId = document.getElementById('post-space').value;
            const autor = document.getElementById('post-author').value.trim();

            if (!conteudo) {{
                alert('Por favor, escreva uma mensagem antes de publicar.');
                return;
            }}

            try {{
                const res = await fetch('/api/v1/comunidade/posts', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        espaco_id: parseInt(espacoId),
                        titulo: titulo || null,
                        conteudo: conteudo,
                        autor_nome: autor || 'Discípulo Metanoia',
                        anonimo: !autor
                    }})
                }});
                const data = await res.json();
                if (res.ok) {{
                    window.location.reload();
                }} else {{
                    alert('Erro ao publicar: ' + (data.detail || 'Tente novamente.'));
                }}
            }} catch (err) {{
                console.error(err);
                alert('Erro de conexão ao publicar.');
            }}
        }}

        async function reagirPost(postId) {{
            try {{
                const res = await fetch(`/api/v1/comunidade/posts/${{postId}}/reagir`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ tipo: 'orando' }})
                }});
                const data = await res.json();
                if (res.ok) {{
                    const el = document.getElementById(`likes-${{postId}}`);
                    if (el) el.innerText = data.likes_count;
                }}
            }} catch (err) {{
                console.error(err);
            }}
        }}

        function toggleComentarios(postId) {{
            const sec = document.getElementById(`comentarios-${{postId}}`);
            if (sec) {{
                sec.style.display = (sec.style.display === 'none' || !sec.style.display) ? 'block' : 'none';
            }}
        }}

        async function enviarComentario(postId) {{
            const input = document.getElementById(`input-com-${{postId}}`);
            const autorInput = document.getElementById(`input-autor-${{postId}}`);
            const texto = input.value.trim();
            const autor = autorInput.value.trim();

            if (!texto) return;

            try {{
                const res = await fetch(`/api/v1/comunidade/posts/${{postId}}/comentarios`, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{
                        conteudo: texto,
                        autor_nome: autor || 'Irmão em Cristo',
                        anonimo: !autor
                    }})
                }});
                if (res.ok) {{
                    const lista = document.getElementById(`lista-com-${{postId}}`);
                    const countEl = document.getElementById(`count-com-${{postId}}`);
                    const div = document.createElement('div');
                    div.className = 'comment-bubble';
                    div.innerHTML = `
                        <div class="comment-author">
                            <span class="comment-avatar">🕊️</span>
                            <strong>${{autor || 'Irmão em Cristo'}}</strong>
                            <span class="comment-role">${{autor ? 'Membro' : 'Anônimo'}}</span>
                        </div>
                        <div class="comment-text">${{texto}}</div>
                    `;
                    lista.appendChild(div);
                    input.value = '';
                    if (countEl) {{
                        countEl.innerText = parseInt(countEl.innerText || 0) + 1;
                    }}
                }}
            }} catch (err) {{
                console.error(err);
            }}
        }}

        function compartilharPost(postId) {{
            const url = window.location.origin + `/comunidade#post-${{postId}}`;
            navigator.clipboard.writeText(url);
            alert('Link da publicação copiado para a área de transferência!');
        }}
    </script>
</body>
</html>
    """
