"""Motor de Blog Automatizado para Estudos Bíblicos // Comunidade Metanoia.
Permite publicação contínua de matérias, resumos de teologia e compartilhamento em redes sociais.
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from pathlib import Path
import re
import html
from app.db.database import get_connection
from app.core.config import BASE_URL

router = APIRouter(tags=["Blog Bíblico & Estudos da Palavra"])

def slugify(text: str) -> str:
    """Gera um slug amigável para URLs a partir do título."""
    import unicodedata
    clean = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII').lower()
    clean = re.sub(r'[^a-z0-9]+', '-', clean).strip('-')
    return clean

def sync_blog_articles() -> int:
    """Sincroniza automaticamente as apostilas e resumos de data/resumos_estudos no banco SQLite."""
    conn = get_connection()
    cursor = conn.cursor()
    
    pasta_resumos = Path(__file__).resolve().parent.parent.parent / "data" / "resumos_estudos"
    if not pasta_resumos.exists():
        conn.close()
        return 0

    arquivos = list(pasta_resumos.glob("*.md"))
    cadastrados = 0

    for arq in arquivos:
        try:
            with open(arq, "r", encoding="utf-8") as f:
                content = f.read()

            # Extrair título
            first_line = content.splitlines()[0] if content.splitlines() else arq.stem
            titulo = first_line.replace("#", "").replace("📚", "").replace("RESUMO EXECUTIVO //", "").strip()
            if not titulo:
                titulo = arq.stem.replace("_", " ").title()

            # Gerar slug único
            slug = slugify(titulo)
            if not slug:
                slug = slugify(arq.stem)

            # Categoria deduzida
            if any(k in titulo.lower() for k in ["pentateuco", "historicos", "poeticos", "profetas"]):
                categoria = "Antigo Testamento"
            elif any(k in titulo.lower() for k in ["evangelhos", "atos", "epistolas", "apocalipse"]):
                categoria = "Novo Testamento"
            elif "doutrina" in titulo.lower() or "teologia" in titulo.lower():
                categoria = "Teologia Sistemática"
            else:
                categoria = "Escola Teológica"

            # Tempo estimado de leitura (base 200 palavras/min)
            palavras = len(content.split())
            tempo_min = max(3, round(palavras / 180))

            cursor.execute("""
            INSERT INTO artigos_blog (
                slug, titulo, subtitulo, categoria, tempo_leitura_min, autor, conteudo_markdown, publicado
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 1)
            ON CONFLICT(slug) DO UPDATE SET
                titulo = excluded.titulo,
                categoria = excluded.categoria,
                tempo_leitura_min = excluded.tempo_leitura_min,
                conteudo_markdown = excluded.conteudo_markdown
            """, (slug, titulo, f"Estudo estruturado e aprofundado sobre {titulo}.", categoria, tempo_min, "Matheus Barbosa // Comunidade Metanoia", content))
            cadastrados += 1
        except Exception as e:
            print(f"[AVISO] Erro ao sincronizar artigo {arq.name}: {e}")

    conn.commit()
    conn.close()
    return cadastrados

@router.post("/api/v1/blog/sync")
def trigger_sync():
    """Aciona a sincronização automática dos artigos do blog."""
    total = sync_blog_articles()
    return {"sucesso": True, "artigos_sincronizados": total}

@router.get("/blog", response_class=HTMLResponse)
def listar_artigos_blog(categoria: str = None, busca: str = None):
    """Página principal do Blog Bíblico da Comunidade Metanoia."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Garantir que há artigos cadastrados
    cursor.execute("SELECT COUNT(*) as total FROM artigos_blog")
    if cursor.fetchone()["total"] == 0:
        sync_blog_articles()

    query = "SELECT * FROM artigos_blog WHERE publicado = 1"
    params = []

    if categoria and categoria != "Todos":
        query += " AND categoria = ?"
        params.append(categoria)

    if busca:
        query += " AND (titulo LIKE ? OR conteudo_markdown LIKE ?)"
        termo = f"%{busca}%"
        params.extend([termo, termo])

    query += " ORDER BY id ASC"
    cursor.execute(query, params)
    artigos = [dict(r) for r in cursor.fetchall()]
    conn.close()

    cards_html = ""
    for a in artigos:
        cards_html += f"""
        <article class="card-artigo">
            <span class="badge-cat">{html.escape(a['categoria'])}</span>
            <span class="meta-leitura">⏱️ {a['tempo_leitura_min']} min de leitura</span>
            <h2><a href="/blog/{a['slug']}">{html.escape(a['titulo'])}</a></h2>
            <p>{html.escape(a.get('subtitulo') or '')}</p>
            <div class="card-footer">
                <span>✍️ {html.escape(a['autor'])}</span>
                <a href="/blog/{a['slug']}" class="btn-ler">Ler Estudo Completo ➔</a>
            </div>
        </article>
        """

    if not cards_html:
        cards_html = "<p style='text-align:center; color:#94A3B8; padding:50px;'>Nenhum estudo encontrado com este filtro.</p>"

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Blog Bíblico & Estudos da Palavra // Comunidade Metanoia</title>
    <meta name="description" content="Artigos teológicos e estudos bíblicos profundos da Comunidade Metanoia. Formação cristã sólida e 100% gratuita.">
    <!-- Favicon & Touch Icons -->
    <link rel="icon" type="image/svg+xml" href="/static/favicon.svg">
    <link rel="icon" type="image/png" sizes="32x32" href="/static/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/static/favicon-16x16.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/static/apple-touch-icon.png">
    <link rel="shortcut icon" href="/favicon.ico">
    <meta name="theme-color" content="#090B10">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #090B10;
            --card-bg: #11141D;
            --gold: #F59E0B;
            --gold-light: #FCD34D;
            --text-title: #FFFFFF;
            --text-body: #CBD5E1;
            --text-muted: #94A3B8;
            --border: #1F2536;
        }}
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ background: var(--bg); color: var(--text-body); font-family: 'Plus Jakarta Sans', sans-serif; line-height: 1.6; padding-bottom: 60px; }}
        header {{ display:flex; justify-content:space-between; align-items:center; padding: 20px 40px; background: rgba(9,11,16,0.9); border-bottom:1px solid var(--border); position:sticky; top:0; z-index:50; backdrop-filter:blur(10px); }}
        .logo {{ font-family: 'Playfair Display', serif; font-size:22px; color:var(--text-title); text-decoration:none; font-weight:700; }}
        .logo span {{ color:var(--gold-light); font-size:13px; font-family:'Plus Jakarta Sans', sans-serif; font-weight:500; }}
        .hero-blog {{ text-align:center; padding: 60px 20px 40px; max-width:800px; margin:0 auto; }}
        .hero-blog h1 {{ font-family:'Playfair Display', serif; font-size:38px; color:var(--text-title); margin-bottom:12px; }}
        .hero-blog p {{ font-size:16px; color:var(--text-muted); }}
        .grid-artigos {{ max-width: 1100px; margin: 40px auto 0; padding: 0 20px; display: grid; grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); gap: 24px; }}
        .card-artigo {{ background: var(--card-bg); border: 1px solid var(--border); border-radius: 18px; padding: 26px; display: flex; flex-direction: column; justify-content: space-between; transition: all 0.3s; }}
        .card-artigo:hover {{ transform: translateY(-4px); border-color: rgba(245,158,11,0.4); box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
        .badge-cat {{ display:inline-block; font-size:11px; font-weight:700; text-transform:uppercase; color:var(--gold-light); background:rgba(245,158,11,0.12); padding:4px 10px; border-radius:15px; margin-bottom:12px; width:fit-content; }}
        .meta-leitura {{ font-size:12px; color:var(--text-muted); margin-left:10px; }}
        .card-artigo h2 {{ font-family:'Playfair Display', serif; font-size:21px; margin-bottom:10px; }}
        .card-artigo h2 a {{ color:var(--text-title); text-decoration:none; transition:color 0.2s; }}
        .card-artigo h2 a:hover {{ color:var(--gold); }}
        .card-artigo p {{ font-size:14px; color:var(--text-muted); line-height:1.6; margin-bottom:18px; }}
        .card-footer {{ display:flex; justify-content:space-between; align-items:center; border-top:1px solid var(--border); padding-top:14px; font-size:12px; color:var(--text-muted); }}
        .btn-ler {{ color:var(--gold); font-weight:700; text-decoration:none; }}
        .btn-header {{ background:var(--gold); color:#000; padding:8px 18px; border-radius:20px; font-weight:700; font-size:13px; text-decoration:none; }}
    </style>
</head>
<body>
    <header>
        <a href="/" class="logo">Comunidade Metanoia <span>// Blog Bíblico</span></a>
        <div>
            <a href="/" style="color:var(--text-muted); text-decoration:none; margin-right:16px; font-size:14px;">🏠 Início</a>
            <a href="/#louvores" style="color:var(--text-muted); text-decoration:none; margin-right:16px; font-size:14px;">🎶 Louvores 24h</a>
            <a href="/plataforma" class="btn-header">Entrar na Comunidade</a>
        </div>
    </header>

    <div class="hero-blog">
        <span class="badge-cat" style="font-size:13px; padding:6px 16px;">📖 Escola Bíblica Aberta</span>
        <h1>Estudos Profundos & Teologia da Graça</h1>
        <p>Aprofunde sua fé com análises bíblicas capítulo por capítulo, resumos didáticos e teologia aplicada à vida real. 100% gratuito.</p>
    </div>

    <div class="grid-artigos">
        {cards_html}
    </div>
</body>
</html>"""

@router.get("/blog/{slug}", response_class=HTMLResponse)
def ler_artigo_blog(slug: str):
    """Página de leitura do estudo individual com renderizador de markdown e botão WhatsApp."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM artigos_blog WHERE slug = ? AND publicado = 1", (slug,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Estudo bíblico não encontrado.")

    artigo = dict(row)
    cursor.execute("UPDATE artigos_blog SET visualizacoes = visualizacoes + 1 WHERE id = ?", (artigo['id'],))
    conn.commit()
    conn.close()

    escaped_title = html.escape(artigo['titulo'])
    escaped_cat = html.escape(artigo['categoria'])
    share_url = f"{BASE_URL}/blog/{slug}"
    share_text = f"📖 Estudo Bíblico Impactante: {artigo['titulo']}\nLeia completo na Comunidade Metanoia: {share_url}"
    import urllib.parse
    whatsapp_link = f"https://api.whatsapp.com/send?text={urllib.parse.quote(share_text)}"

    # Escapar conteúdo para passar com segurança para a biblioteca marked.js
    raw_md_json = re.sub(r'</script>', '<\\/script>', artigo['conteudo_markdown'])

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escaped_title} // Comunidade Metanoia</title>
    <meta name="description" content="{html.escape(artigo.get('subtitulo') or artigo['titulo'])}">
    
    <!-- Open Graph / WhatsApp -->
    <meta property="og:title" content="{escaped_title} // Comunidade Metanoia">
    <meta property="og:description" content="{html.escape(artigo.get('subtitulo') or '')}">
    <meta property="og:type" content="article">
    
    <!-- Favicon & Touch Icons -->
    <link rel="icon" type="image/svg+xml" href="/static/favicon.svg">
    <link rel="icon" type="image/png" sizes="32x32" href="/static/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/static/favicon-16x16.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/static/apple-touch-icon.png">
    <link rel="shortcut icon" href="/favicon.ico">
    <meta name="theme-color" content="#090B10">

    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,600;0,700;1,400&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <style>
        :root {{
            --bg: #090B10;
            --card-bg: #11141D;
            --gold: #F59E0B;
            --gold-light: #FCD34D;
            --text-title: #FFFFFF;
            --text-body: #E2E8F0;
            --text-muted: #94A3B8;
            --border: #1F2536;
        }}
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ background: var(--bg); color: var(--text-body); font-family: 'Plus Jakarta Sans', sans-serif; line-height: 1.8; }}
        header {{ display:flex; justify-content:space-between; align-items:center; padding: 20px 40px; background: rgba(9,11,16,0.9); border-bottom:1px solid var(--border); position:sticky; top:0; z-index:50; backdrop-filter:blur(10px); }}
        .logo {{ font-family: 'Playfair Display', serif; font-size:22px; color:var(--text-title); text-decoration:none; font-weight:700; }}
        .logo span {{ color:var(--gold-light); font-size:13px; font-family:'Plus Jakarta Sans', sans-serif; font-weight:500; }}
        .article-container {{ max-width: 820px; margin: 40px auto 80px; padding: 0 24px; }}
        .breadcrumb {{ font-size: 13px; color: var(--text-muted); margin-bottom: 20px; }}
        .breadcrumb a {{ color: var(--gold); text-decoration: none; }}
        .article-header {{ margin-bottom: 40px; border-bottom: 1px solid var(--border); padding-bottom: 24px; }}
        .badge-cat {{ display:inline-block; font-size:12px; font-weight:700; text-transform:uppercase; color:var(--gold-light); background:rgba(245,158,11,0.12); padding:4px 12px; border-radius:15px; margin-bottom:16px; }}
        .article-header h1 {{ font-family:'Playfair Display', serif; font-size:40px; color:var(--text-title); line-height:1.25; margin-bottom:14px; }}
        .meta-bar {{ display:flex; gap:16px; font-size:13px; color:var(--text-muted); flex-wrap:wrap; }}
        
        /* Rendered Markdown Body */
        #article-content {{ font-size: 17px; line-height: 1.9; color: var(--text-body); }}
        #article-content h1, #article-content h2, #article-content h3 {{ font-family: 'Playfair Display', serif; color: var(--text-title); margin: 36px 0 16px; }}
        #article-content h2 {{ font-size: 26px; border-bottom: 1px solid var(--border); padding-bottom: 8px; }}
        #article-content h3 {{ font-size: 20px; color: var(--gold-light); }}
        #article-content p {{ margin-bottom: 22px; }}
        #article-content ul, #article-content ol {{ margin: 0 0 24px 24px; }}
        #article-content li {{ margin-bottom: 8px; }}
        #article-content blockquote {{ background: rgba(245,158,11,0.06); border-left: 4px solid var(--gold); padding: 18px 24px; margin: 26px 0; border-radius: 0 12px 12px 0; font-style: italic; color: #FEF3C7; }}
        #article-content hr {{ border: none; border-top: 1px solid var(--border); margin: 36px 0; }}

        /* Share Box */
        .share-box {{ margin-top: 50px; padding: 24px; background: var(--card-bg); border: 1px solid var(--border); border-radius: 18px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px; }}
        .btn-whatsapp {{ background: #25D366; color: #000; font-weight: 700; padding: 10px 22px; border-radius: 25px; text-decoration: none; display: flex; align-items: center; gap: 8px; font-size: 14px; transition: transform 0.2s; }}
        .btn-whatsapp:hover {{ transform: scale(1.04); }}
        .cta-box {{ margin-top: 40px; padding: 32px; background: linear-gradient(135deg, rgba(245,158,11,0.1), rgba(17,20,29,0.9)); border: 1px solid rgba(245,158,11,0.3); border-radius: 20px; text-align: center; }}
    </style>
</head>
<body>
    <header>
        <a href="/" class="logo">Comunidade Metanoia <span>// Blog</span></a>
        <div>
            <a href="/blog" style="color:var(--text-muted); text-decoration:none; margin-right:16px; font-size:14px;">📚 Todos os Estudos</a>
            <a href="/" class="btn-whatsapp" style="background:var(--gold); color:#000;">Voltar ao Início</a>
        </div>
    </header>

    <main class="article-container">
        <div class="breadcrumb">
            <a href="/">Início</a> › <a href="/blog">Blog Bíblico</a> › <span>{escaped_title}</span>
        </div>

        <div class="article-header">
            <span class="badge-cat">{escaped_cat}</span>
            <h1>{escaped_title}</h1>
            <div class="meta-bar">
                <span>✍️ {html.escape(artigo['autor'])}</span>
                <span>⏱️ {artigo['tempo_leitura_min']} min de leitura</span>
                <span>👁️ {artigo['visualizacoes']} leituras</span>
                <a href="/blog/{slug}/social" style="color:var(--gold-light); text-decoration:none; font-weight:600; background:rgba(245,158,11,0.15); border:1px solid rgba(245,158,11,0.3); padding:4px 14px; border-radius:14px; margin-left:auto; display:inline-flex; align-items:center; gap:6px;">🚀 Kit de Redes Sociais</a>
            </div>
        </div>

        <div id="article-content"></div>

        <div class="share-box">
            <div>
                <strong>Gostou deste estudo?</strong>
                <p style="font-size:13px; color:var(--text-muted);">Edifique a vida de alguém enviando no WhatsApp ou use o Kit de Redes.</p>
            </div>
            <div style="display:flex; gap:10px; flex-wrap:wrap;">
                <a href="/blog/{slug}/social" class="btn-whatsapp" style="background:rgba(245,158,11,0.15); color:var(--gold-light); border:1px solid rgba(245,158,11,0.4);">
                    🚀 Kit de Postagens
                </a>
                <a href="{whatsapp_link}" target="_blank" class="btn-whatsapp">
                    📱 Compartilhar no WhatsApp
                </a>
            </div>
        </div>

        <div class="cta-box">
            <h3 style="font-family:'Playfair Display', serif; font-size:24px; color:var(--text-title); margin-bottom:10px;">
                Você Não Precisa Estudar Sozinho
            </h3>
            <p style="font-size:15px; color:var(--text-muted); max-width:600px; margin:0 auto 20px;">
                Conheça a Comunidade Metanoia. Temos encontros semanais na nossa Célula Digital, mural de oração anônimo e louvores 24h tocando para sua paz.
            </p>
            <a href="/plataforma" style="background:var(--gold); color:#000; padding:12px 28px; border-radius:25px; font-weight:700; text-decoration:none; display:inline-block;">
                🤍 Entrar na Comunidade Metanoia
            </a>
        </div>
    </main>

    <script id="raw-markdown" type="text/plain">{raw_md_json}</script>
    <script>
        const raw = document.getElementById('raw-markdown').textContent;
        document.getElementById('article-content').innerHTML = marked.parse(raw);
    </script>
</body>
</html>"""

@router.get("/blog/{slug}/social", response_class=HTMLResponse)
def kit_redes_sociais_estudo(slug: str):
    """Painel de Kit de Redes Sociais com cópia em 1 clique e envio ao Teleprompter."""
    import json
    import urllib.parse
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM artigos_blog WHERE slug = ?", (slug,))
    artigo_row = cursor.fetchone()
    if not artigo_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Estudo não encontrado.")

    artigo = dict(artigo_row)

    # Buscar postagens do kit
    cursor.execute("SELECT * FROM postagens_redes_sociais WHERE artigo_slug = ?", (slug,))
    posts = [dict(r) for r in cursor.fetchall()]
    conn.close()

    # Mapear posts por tipo
    posts_map = {f"{p['plataforma']}_{p['tipo']}": p['conteudo'] for p in posts}
    
    # Se não existia no banco, buscar do gerador
    if not posts_map:
        from scripts.automacao_blog_social import gerar_kit_social, salvar_kit_no_banco
        kit = gerar_kit_social(artigo)
        salvar_kit_no_banco(kit)
        legenda_ig = kit["legenda_instagram"]
        roteiro_video = kit["roteiro_shorts"]
        zap_msg = kit["mensagem_whatsapp"]
        slides = kit["carrossel_slides"]
        thread = "\n\n---\n\n".join(kit["thread_x"])
    else:
        legenda_ig = posts_map.get("instagram_legenda", "")
        roteiro_video = posts_map.get("youtube_shorts_roteiro_video", "")
        zap_msg = posts_map.get("whatsapp_mensagem_grupo", "")
        thread = posts_map.get("twitter_thread", "")
        slides_raw = posts_map.get("instagram_carrossel", "[]")
        try:
            slides = json.loads(slides_raw)
        except Exception:
            slides = []

    slides_cards_html = ""
    for s in slides:
        slides_cards_html += f"""
        <div style="background:#11141D; border:1px solid #1F2536; border-radius:12px; padding:16px; margin-bottom:12px;">
            <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                <strong style="color:#FCD34D; font-size:13px;">SLIDE {s.get('slide', '')} // {html.escape(s.get('tipo', ''))}</strong>
                <button onclick="copiarTexto(this)" data-content="{html.escape(s.get('texto', ''))}" style="background:#1F2536; color:#CBD5E1; border:none; padding:4px 10px; border-radius:8px; font-size:11px; cursor:pointer;">📋 Copiar Slide</button>
            </div>
            <pre style="white-space:pre-wrap; font-family:inherit; font-size:14px; color:#E2E8F0; line-height:1.5;">{html.escape(s.get('texto', ''))}</pre>
        </div>
        """

    url_teleprompter = f"/teleprompter?texto={urllib.parse.quote(roteiro_video)}"
    url_zap_share = f"https://api.whatsapp.com/send?text={urllib.parse.quote(zap_msg)}"

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kit de Redes Sociais // {html.escape(artigo['titulo'])}</title>
    <!-- Favicon & Touch Icons -->
    <link rel="icon" type="image/svg+xml" href="/static/favicon.svg">
    <link rel="icon" type="image/png" sizes="32x32" href="/static/favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="/static/favicon-16x16.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/static/apple-touch-icon.png">
    <link rel="shortcut icon" href="/favicon.ico">
    <meta name="theme-color" content="#090B10">
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Playfair+Display:wght@600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg: #090B10;
            --card-bg: #11141D;
            --gold: #F59E0B;
            --gold-light: #FCD34D;
            --text-title: #FFFFFF;
            --text-body: #E2E8F0;
            --text-muted: #94A3B8;
            --border: #1F2536;
        }}
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{ background: var(--bg); color: var(--text-body); font-family: 'Plus Jakarta Sans', sans-serif; line-height: 1.6; padding-bottom: 80px; }}
        header {{ display:flex; justify-content:space-between; align-items:center; padding: 18px 40px; background: rgba(9,11,16,0.95); border-bottom:1px solid var(--border); position:sticky; top:0; z-index:50; backdrop-filter:blur(10px); }}
        .logo {{ font-family: 'Playfair Display', serif; font-size:20px; color:var(--text-title); text-decoration:none; font-weight:700; }}
        .logo span {{ color:var(--gold-light); font-size:12px; font-weight:500; }}
        .container {{ max-width: 900px; margin: 30px auto; padding: 0 20px; }}
        .badge {{ display:inline-block; font-size:11px; font-weight:700; text-transform:uppercase; color:var(--gold-light); background:rgba(245,158,11,0.12); padding:4px 10px; border-radius:15px; margin-bottom:10px; }}
        .section-box {{ background: var(--card-bg); border: 1px solid var(--border); border-radius: 16px; padding: 26px; margin-bottom: 28px; }}
        .section-header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom: 16px; border-bottom: 1px solid var(--border); padding-bottom: 12px; }}
        .section-title {{ font-size: 18px; font-weight: 700; color: var(--text-title); display: flex; align-items: center; gap: 8px; }}
        .btn-copy {{ background: var(--gold); color: #000; font-weight: 700; border: none; padding: 8px 16px; border-radius: 20px; cursor: pointer; font-size: 13px; transition: transform 0.2s; }}
        .btn-copy:hover {{ transform: scale(1.04); }}
        .btn-secondary {{ background: #1F2536; color: var(--gold-light); text-decoration: none; padding: 8px 16px; border-radius: 20px; font-size: 13px; font-weight: 600; display: inline-flex; align-items: center; gap: 6px; }}
        pre {{ white-space: pre-wrap; font-family: inherit; font-size: 14px; color: var(--text-body); background: #0D1017; border: 1px solid var(--border); border-radius: 12px; padding: 18px; line-height: 1.7; }}
    </style>
</head>
<body>
    <header>
        <a href="/" class="logo">Comunidade Metanoia <span>// Automação Ministerial</span></a>
        <div>
            <a href="/blog/{slug}" style="color:var(--text-muted); text-decoration:none; margin-right:16px; font-size:14px;">📖 Voltar ao Estudo</a>
            <a href="/blog" style="color:var(--gold); text-decoration:none; font-size:14px; font-weight:600;">📚 Todos os Estudos</a>
        </div>
    </header>

    <div class="container">
        <div style="margin-bottom: 30px;">
            <span class="badge">🚀 Kit de Publicação Automática</span>
            <h1 style="font-family:'Playfair Display', serif; font-size:32px; color:var(--text-title); margin-bottom:8px;">
                {html.escape(artigo['titulo'])}
            </h1>
            <p style="color:var(--text-muted); font-size:15px;">
                Conteúdo estratégico 100% modelado para redes sociais. Copie com 1 clique ou grave direto no teleprompter.
            </p>
        </div>

        <!-- 1. YOUTUBE SHORTS / REELS COM TELEPROMPTER -->
        <div class="section-box" style="border-color: rgba(245,158,11,0.4);">
            <div class="section-header">
                <div class="section-title">⏱️ 1. Roteiro Vertical de 60 Segundos (Shorts / Reels)</div>
                <div style="display:flex; gap:10px;">
                    <button class="btn-copy" onclick="copiarElemento('txt-shorts', this)">📋 Copiar Roteiro</button>
                    <a href="{url_teleprompter}" target="_blank" class="btn-secondary" style="background:#F59E0B; color:#000;">
                        🎬 Gravar no Teleprompter
                    </a>
                </div>
            </div>
            <pre id="txt-shorts">{html.escape(roteiro_video)}</pre>
        </div>

        <!-- 2. WHATSAPP BROADCAST -->
        <div class="section-box">
            <div class="section-header">
                <div class="section-title">📱 2. Mensagem para WhatsApp (Transmissão & Grupos)</div>
                <div style="display:flex; gap:10px;">
                    <button class="btn-copy" onclick="copiarElemento('txt-zap', this)">📋 Copiar Mensagem</button>
                    <a href="{url_zap_share}" target="_blank" class="btn-secondary" style="background:#25D366; color:#000;">
                        💬 Abrir no WhatsApp
                    </a>
                </div>
            </div>
            <pre id="txt-zap">{html.escape(zap_msg)}</pre>
        </div>

        <!-- 3. INSTAGRAM CARROSSEL -->
        <div class="section-box">
            <div class="section-header">
                <div class="section-title">📸 3. Instagram Carrossel (6 Slides Estruturados)</div>
            </div>
            {slides_cards_html}

            <div style="margin-top: 20px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                    <strong style="color:var(--gold-light); font-size:14px;">📝 Legenda Completa com Hashtags:</strong>
                    <button class="btn-copy" onclick="copiarElemento('txt-legenda-ig', this)">📋 Copiar Legenda</button>
                </div>
                <pre id="txt-legenda-ig">{html.escape(legenda_ig)}</pre>
            </div>
        </div>

        <!-- 4. THREAD X / TWITTER -->
        <div class="section-box">
            <div class="section-header">
                <div class="section-title">🐦 4. Fio Teológico para o X / Twitter</div>
                <button class="btn-copy" onclick="copiarElemento('txt-thread', this)">📋 Copiar Fio Completo</button>
            </div>
            <pre id="txt-thread">{html.escape(thread)}</pre>
        </div>
    </div>

    <script>
        function copiarElemento(id, btn) {{
            const el = document.getElementById(id);
            const text = el.innerText || el.textContent;
            navigator.clipboard.writeText(text).then(() => {{
                const originalText = btn.innerText;
                btn.innerText = '✅ Copiado!';
                setTimeout(() => btn.innerText = originalText, 2000);
            }});
        }}

        function copiarTexto(btn) {{
            const text = btn.getAttribute('data-content');
            navigator.clipboard.writeText(text).then(() => {{
                const originalText = btn.innerText;
                btn.innerText = '✅ Copiado!';
                setTimeout(() => btn.innerText = originalText, 2000);
            }});
        }}
    </script>
</body>
</html>"""

