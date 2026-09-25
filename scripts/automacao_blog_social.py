"""Motor de Automação de Publicação: Blog Bíblico & Redes Sociais.
Comunidade Metanoia // "Ninguém luta sozinho"
100% Python - Transforma os estudos bíblicos em artigos formatados e kits prontos para:
- Instagram (Carrossel de 6 slides + Legenda)
- YouTube Shorts / Reels (Roteiro cronometrado de 60 segundos para Teleprompter)
- WhatsApp (Mensagem para lista de transmissão e grupos de discipulado)
- X / Twitter (Thread teológica de 4 tweets)
"""
import sys
import re
import json
from pathlib import Path

# Suporte a Unicode/emojis no terminal Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.db.database import get_connection

OUTPUT_DIR = BASE_DIR / "data" / "posts_redes"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HASHTAGS_PADRAO = "#ComunidadeMetanoia #NinguemLutaSozinho #EstudoBiblico #TeologiaDaGraca #PalavraDeDeus #DevocionalDiario #VidaCrista"

def extrair_metadados_estudo(markdown_content: str, titulo_original: str) -> dict:
    """Extrai capítulos, versículos e temas centrais do estudo."""
    versiculos = re.findall(r"([1-3]?\s?[A-Z][a-zçãõáéíóúâêô]+\s+\d+:\d+(?:-\d+)?)", markdown_content)
    versiculos_unicos = list(dict.fromkeys(versiculos))
    
    capitulos = []
    for linha in markdown_content.splitlines():
        linha_strip = linha.replace("*", "").replace("#", "").strip()
        if re.search(r"(CAP[IÍ]TULO|\b[0-9]+\.\s+[A-ZÁÉÍÓÚÂÊÔÃÕ])", linha_strip, re.IGNORECASE):
            if len(linha_strip) < 70 and linha_strip not in capitulos:
                capitulos.append(linha_strip)
                
    # Determinar tema principal e promessa de consolo
    tema = titulo_original.replace("Apostila", "").replace("Modulo", "").replace("RESUMO EXECUTIVO //", "").strip()
    return {
        "tema": tema,
        "versiculos": versiculos_unicos[:4] if versiculos_unicos else ["Josué 1:9", "Salmos 119:105"],
        "capitulos": capitulos[:5] if capitulos else ["Fundamentos Bíblicos", "Princípios da Fé", "Aplicação Prática"]
    }

def gerar_kit_social(artigo: dict) -> dict:
    """Gera kit completo de postagens multiplataforma para um artigo."""
    slug = artigo["slug"]
    titulo = artigo["titulo"]
    conteudo_md = artigo["conteudo_markdown"]
    meta = extrair_metadados_estudo(conteudo_md, titulo)
    versiculo_chave = meta["versiculos"][0] if meta["versiculos"] else "Salmos 119:105"
    url_artigo = f"https://ministerio-ts5s.onrender.com/blog/{slug}"

    # 1. Instagram Carrossel (6 Slides)
    carrossel_slides = [
        {
            "slide": 1,
            "tipo": "Capa / Gancho",
            "texto": f"🚨 VOCÊ REALMENTE CONHECE ISSO NA BÍBLIA?\n\n{titulo.upper()}\n\n👉 Arraste para o lado e entenda o que quase ninguém te ensina na igreja."
        },
        {
            "slide": 2,
            "tipo": "O Problema / Dilema Real",
            "texto": f"Muitas vezes nos sentimos cansados, fracos e com a fé abalada porque tentamos viver o Evangelho na força do nosso próprio braço.\n\nMas a Escritura Sagrada nos ensina um caminho de transformação profunda de mentalidade."
        },
        {
            "slide": 3,
            "tipo": "A Revelação Bíblica",
            "texto": f"📖 Veja o que diz a Palavra:\n\n\"{versiculo_chave}\"\n\nNão se trata de regras humanas. Trata-se da graça viva de Deus nos alcançando exatamente onde estamos."
        },
        {
            "slide": 4,
            "tipo": "Pilares do Estudo",
            "texto": "Pontos fundamentais desta matéria:\n\n" + "\n".join([f"✅ {c}" for c in meta["capitulos"][:3]])
        },
        {
            "slide": 5,
            "tipo": "Aplicação Pessoal",
            "texto": "💡 COMO APLICAR HOJE:\n\n1. Pare de lutar sozinho.\n2. Coloque sua mente na verdade de Cristo.\n3. Busque irmãos para caminhar com você.\n\nNa Comunidade Metanoia, ninguém fica para trás."
        },
        {
            "slide": 6,
            "tipo": "CTA / Chamada Final",
            "texto": f"🤍 GOSTOU DESTE ESTUDO?\n\nLeia a matéria completa no nosso Blog Bíblico:\n🔗 {url_artigo}\n\n💬 Comente 'METANOIA' para receber no direct ou entre na nossa Célula Digital."
        }
    ]

    legenda_instagram = f"""📖 {titulo.upper()} // Comunidade Metanoia

Você já parou para pensar que o conhecimento da Palavra de Deus liberta mais a sua mente do que qualquer conselho humano?

Neste estudo profundo da nossa Escola Bíblica, analisamos as raízes de {titulo} e como essa verdade cura a ansiedade e fortalece quem está cansado na caminhada.

🕊️ "{versiculo_chave}"

👉 Quer ler a análise completa de graça no nosso Blog?
Acesse agora pelo link da bio: {url_artigo}

🤍 "Ninguém luta sozinho."
Marque um irmão que precisa dessa palavra hoje nos comentários!

{HASHTAGS_PADRAO} #{slug.replace('-', '')}
"""

    # 2. Roteiro Cronometrado de 60 Segundos para Shorts / Reels / Teleprompter
    roteiro_shorts = f"""⏱️ ROTEIRO PARA VÍDEO VERTICAL (60 SEGUNDOS // TELEPROMPTER)
Tema: {titulo}
Versículo Base: {versiculo_chave}

[00:00 - 00:06] GANCHO IMPACTANTE:
"Se você está cansado de fingir que está tudo bem e sente que sua fé está no limite... para esse vídeo agora e escuta isso."

[00:07 - 00:25] A VERDADE BÍBLICA:
"A Bíblia diz em {versiculo_chave} que a verdade de Deus não é para nos acusar, é para nos libertar. No nosso estudo sobre {titulo}, nós descobrimos que Deus nunca te chamou para carregar o peso do mundo sozinho."

[00:26 - 00:45] O CONFRONTO DE AMOR:
"Metanoia significa mudar a forma de pensar para viver o plano de Deus. Pare de se condenar pelo que você não conseguiu fazer hoje. A graça de Cristo te basta para o dia de amanhã."

[00:46 - 01:00] CHAMADA DE AÇÃO:
"Nós criamos a Comunidade Metanoia para isso: ninguém luta sozinho. Tem louvor 24h tocando e o estudo completo te esperando no link do meu perfil. Entra lá agora e seja abençoado."
"""

    # 3. Mensagem para Grupos e Lista de Transmissão de WhatsApp
    mensagem_whatsapp = f"""*🕊️ COMUNIDADE METANOIA // PALAVRA DO DIA*
_"{titulo}"_

Irmãos, a paz do Senhor! 🙏

Acabamos de disponibilizar um estudo bíblico poderoso e totalmente gratuito na nossa Escola Bíblica.

📖 *Versículo do Estudo:* {versiculo_chave}

Se você está precisando de direção espiritual, clareza sobre as Escrituras e um renovo para a sua semana, não deixe de ler:

👉 *Clique para ler o estudo completo:*
{url_artigo}

Compartilhe com alguém da sua família ou célula que precisa desta mensagem hoje! 🤍
_Comunidade Metanoia // "Ninguém luta sozinho"_
"""

    # 4. Thread para o Twitter / X
    thread_x = [
        f"1/4 🧵 Por que estudar {titulo} pode mudar a sua saúde emocional e espiritual? Um fio bíblico rápido para o seu coração 👇",
        f"2/4 📖 Em {versiculo_chave}, vemos que a Revelação de Deus não é um peso moralista, mas um mapa de libertação. Quando você entende as Escrituras, a mentira da solidão perde o poder.",
        f"3/4 💡 Metanoia = Mudança de mentalidade. Você não foi chamado para travar batalhas silenciosas no seu quarto. Foi chamado para caminhar em comunidade.",
        f"4/4 🤍 Liberamos o estudo teológico completo com acesso livre no nosso blog da Comunidade Metanoia. Leia e compartilhe: {url_artigo}"
    ]

    return {
        "slug": slug,
        "titulo": titulo,
        "url": url_artigo,
        "carrossel_slides": carrossel_slides,
        "legenda_instagram": legenda_instagram,
        "roteiro_shorts": roteiro_shorts,
        "mensagem_whatsapp": mensagem_whatsapp,
        "thread_x": thread_x
    }

def salvar_kit_no_banco(kit: dict) -> None:
    """Salva os posts gerados na tabela postagens_redes_sociais do SQLite."""
    conn = get_connection()
    cursor = conn.cursor()
    slug = kit["slug"]
    titulo = kit["titulo"]

    # 1. Instagram Carrossel
    cursor.execute("""
    INSERT INTO postagens_redes_sociais (artigo_slug, plataforma, tipo, titulo, conteudo, hashtags, status)
    VALUES (?, 'instagram', 'carrossel', ?, ?, ?, 'pronto')
    """, (slug, f"Carrossel: {titulo}", json.dumps(kit["carrossel_slides"], ensure_ascii=False), HASHTAGS_PADRAO))

    # 2. Instagram Legenda
    cursor.execute("""
    INSERT INTO postagens_redes_sociais (artigo_slug, plataforma, tipo, titulo, conteudo, hashtags, status)
    VALUES (?, 'instagram', 'legenda', ?, ?, ?, 'pronto')
    """, (slug, f"Legenda: {titulo}", kit["legenda_instagram"], HASHTAGS_PADRAO))

    # 3. Roteiro Shorts/Reels/Teleprompter
    cursor.execute("""
    INSERT INTO postagens_redes_sociais (artigo_slug, plataforma, tipo, titulo, conteudo, hashtags, status)
    VALUES (?, 'youtube_shorts', 'roteiro_video', ?, ?, ?, 'pronto')
    """, (slug, f"Roteiro 60s: {titulo}", kit["roteiro_shorts"], HASHTAGS_PADRAO))

    # 4. WhatsApp Mensagem
    cursor.execute("""
    INSERT INTO postagens_redes_sociais (artigo_slug, plataforma, tipo, titulo, conteudo, hashtags, status)
    VALUES (?, 'whatsapp', 'mensagem_grupo', ?, ?, '', 'pronto')
    """, (slug, f"WhatsApp: {titulo}", kit["mensagem_whatsapp"]))

    # 5. Twitter / X Thread
    cursor.execute("""
    INSERT INTO postagens_redes_sociais (artigo_slug, plataforma, tipo, titulo, conteudo, hashtags, status)
    VALUES (?, 'twitter', 'thread', ?, ?, '', 'pronto')
    """, (slug, f"Thread: {titulo}", "\n\n---\n\n".join(kit["thread_x"])))

    conn.commit()
    conn.close()

def exportar_kit_markdown(kit: dict) -> Path:
    """Salva o kit em um arquivo markdown pronto para uso em data/posts_redes/."""
    arquivo = OUTPUT_DIR / f"{kit['slug']}_social_kit.md"
    
    slides_formatados = ""
    for s in kit["carrossel_slides"]:
        slides_formatados += f"#### Slide {s['slide']} ({s['tipo']}):\n```\n{s['texto']}\n```\n\n"

    conteudo_arquivo = f"""# 🚀 KIT DE REDES SOCIAIS // {kit['titulo']}
**Artigo no Blog:** [{kit['url']}]({kit['url']})
**Comunidade Metanoia // "Ninguém Luta Sozinho"**

---

## 📸 1. INSTAGRAM CARROSSEL (6 SLIDES)
{slides_formatados}

### 📝 LEGENDA PRONTA PARA O INSTAGRAM:
```text
{kit['legenda_instagram']}
```

---

## 🎬 2. ROTEIRO DE 60 SEGUNDOS (SHORTS / REELS / TELEPROMPTER)
```text
{kit['roteiro_shorts']}
```

---

## 📱 3. MENSAGEM PARA WHATSAPP (LISTA DE TRANSMISSÃO & GRUPOS)
```text
{kit['mensagem_whatsapp']}
```

---

## 🐦 4. THREAD PARA O X / TWITTER
"""
    for tweet in kit["thread_x"]:
        conteudo_arquivo += f"```text\n{tweet}\n```\n\n"

    with open(arquivo, "w", encoding="utf-8") as f:
        f.write(conteudo_arquivo)

    return arquivo

def processar_todos_artigos():
    """Gera o kit de redes sociais para todos os artigos cadastrados no banco."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM artigos_blog WHERE publicado = 1")
    artigos = [dict(r) for r in cursor.fetchall()]
    conn.close()

    print(f"============================================================")
    print(f"🚀 INICIANDO GERADOR AUTOMÁTICO DE POSTS PARA REDES SOCIAIS")
    print(f"Total de estudos encontrados no banco: {len(artigos)}")
    print(f"============================================================")

    for a in artigos:
        try:
            kit = gerar_kit_social(a)
            salvar_kit_no_banco(kit)
            md_path = exportar_kit_markdown(kit)
            print(f" [OK] Kit Gerado: {a['titulo']} -> {md_path.name}")
        except Exception as e:
            print(f" [ERRO] Falha ao processar {a.get('titulo')}: {e}")

    print("============================================================")
    print(f"✨ Todos os kits foram salvos no SQLite e na pasta data/posts_redes/")
    print("============================================================")

if __name__ == "__main__":
    processar_todos_artigos()
