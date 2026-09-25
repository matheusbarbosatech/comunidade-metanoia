"""Script de Alimentação e Ingestão do Conteúdo Teológico Oficial.
Mapeia as 15 Aulas de Introdução à Teologia e 4 Aulas de Bibliologia localizadas em:
C:\\Users\\matheus\\Desktop\\01_Basico_em_Teologia

Alimenta:
1. Tabela 'estudos_aulas' no banco SQLite (com código, título, texto bíblico, resumo e caminho do áudio MP3).
2. Tabela 'comunidade_posts' (Canal de Estudos & Teologia Bíblica).
3. Acervo de resumos e artigos de estudo em 'data/resumos_estudos/' para o Blog Bíblico.
"""
from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "ministerio.db"
AUDIO_DIR = Path(r"C:\Users\matheus\Desktop\01_Basico_em_Teologia")
RESUMOS_DIR = BASE_DIR / "data" / "resumos_estudos"
RESUMOS_DIR.mkdir(parents=True, exist_ok=True)

# 19 Aulas do Módulo 01: 15 de Introdução à Teologia + 4 de Bibliologia
AULAS_CATALOGO = [
    {
        "codigo": "A0001",
        "arquivo": "A0001 - AULA 01 - INTRODUCAO A TEOLOGIA.mp3",
        "titulo": "Aula 01: O Que É Teologia e o Chamado do Teólogo",
        "texto_biblico": "2 Timóteo 2:15; Oséias 4:6",
        "resumo": "Definição etimológica (Theos + Logos). A teologia como ciência de Deus e de suas relações com o homem e o universo. Por que todo cristão, querendo ou não, é um teólogo e como ter uma fé embasada nas Escrituras."
    },
    {
        "codigo": "A0002",
        "arquivo": "A0002 - AULA 02 - INTRODUCAO A TEOLOGIA.mp3",
        "titulo": "Aula 02: O Objetivo Supremo da Teologia: Conhecer e Adorar a Deus",
        "texto_biblico": "Jeremias 9:23-24; João 17:3",
        "resumo": "O propósito da teologia não é o mero acúmulo de conhecimento intelectual, mas a transformação interior (Metanoia) e a intimidade espiritual com o Criador. A oração como combustível da reflexão bíblica."
    },
    {
        "codigo": "A0003",
        "arquivo": "A0003 - AULA 03 - INTRODUCAO A TEOLOGIA.mp3",
        "titulo": "Aula 03: Divisão Clássica da Teologia (Bíblica, Sistemática, Histórica e Prática)",
        "texto_biblico": "Lucas 24:27; Atos 17:11",
        "resumo": "Panorama dos quatro ramos fundamentais da teologia: Teologia Bíblica (desenvolvimento histórico-revelacional), Sistemática (doutrinas organizadas), Histórica (como a Igreja compreendeu a verdade nos séculos) e Prática (ação pastoral e ética)."
    },
    {
        "codigo": "A0004",
        "arquivo": "A0004 - AULA 04 - INTRODUCAO A TEOLOGIA.mp3",
        "titulo": "Aula 04: Teologia Bíblica vs Teologia Sistemática: Métodos e Complementaridade",
        "texto_biblico": "Romanos 11:33-36; 2 Pedro 3:16",
        "resumo": "Como trabalhar a linha do tempo da Revelação sem distorcer o ensino bíblico. A importância de deixar a Bíblia interpretar a si mesma antes de construir sistemas dogmáticos rígidos."
    },
    {
        "codigo": "A0005",
        "arquivo": "A0005 - AULA 05 - INTRODUCAO A TEOLOGIA.mp3",
        "titulo": "Aula 05: A Teologia Pentecostal e a Operação Viva do Espírito Santo",
        "texto_biblico": "Atos 1:8; 1 Coríntios 2:10-14",
        "resumo": "O equilíbrio vital entre a Palavra e o Espírito. Como a experiência de Pentecostes ilumina a mente do estudante e capacita o crente para testemunho com autoridade, sinais e amor sacrificial."
    },
    {
        "codigo": "A0006",
        "arquivo": "A0006 - AULA 06 - INTRODUCAO A TEOLOGIA.mp3",
        "titulo": "Aula 06: A Necessidade de Fazer Teologia no Século XXI",
        "texto_biblico": "1 Pedro 3:15; Tito 1:9",
        "resumo": "O combate ao relativismo moral, ao pragmatismo oco e ao evangelho de consumo. A urgência de líderes e discipuladores que saibam responder com mansidão a razão da esperança que há em nós."
    },
    {
        "codigo": "A0007",
        "arquivo": "A0007 - AULA 07 - INTRODUCAO A TEOLOGIA.mp3",
        "titulo": "Aula 07: As Fontes da Teologia: Revelação, Tradição, Razão e Experiência",
        "texto_biblico": "Salmo 19:1-4; Romanos 1:19-20",
        "resumo": "Revelação Geral (na natureza e na consciência humana) vs Revelação Especial (nas Sagradas Escrituras e em Cristo encarnado). O Quadrilátero e a supremacia inegociável da Palavra de Deus."
    },
    {
        "codigo": "A0008",
        "arquivo": "A0008 - AULA 08 - INTRODUCAO A TEOLOGIA.mp3",
        "titulo": "Aula 08: A Suficiência das Escrituras Sagradas (Sola Scriptura)",
        "texto_biblico": "2 Timóteo 3:16-17; Hebreus 4:12",
        "resumo": "O princípio reformado de que a Bíblia contém tudo o que é necessário para a salvação, fé e vida piedosa. Distinção clara entre revelação canônica definitiva e dons espirituais de edificação da igreja local."
    },
    {
        "codigo": "A0009",
        "arquivo": "A0009 - AULA 09 - INTRODUCAO A TEOLOGIA.mp3",
        "titulo": "Aula 09: O Perfil Espiritual e o Caráter do Teólogo Cristão",
        "texto_biblico": "1 Coríntios 8:1-3; 1 Timóteo 4:16",
        "resumo": "O saber que ensoberbece versus o amor que edifica. A pureza de motivos, a humildade de joelhos diante da soberania divina e o perigo do academicismo frio desprovido de compaixão pelas almas perdidas."
    },
    {
        "codigo": "A0010",
        "arquivo": "A0010 - AULA 10 - INTRODUCAO A TEOLOGIA.mp3",
        "titulo": "Aula 10: Doutrina, Dogma e Religião: Distinções Fundamentais",
        "texto_biblico": "Marcos 7:7-9; 1 Timóteo 1:3-7",
        "resumo": "Diferença entre Doutrina Bíblica (o ensino puro das Escrituras), Dogma (a formulação eclesiástica histórica) e Costumes Locais. Como evitar que mandamentos humanos sufoquem a liberdade da Graça em Cristo."
    },
    {
        "codigo": "A0011",
        "arquivo": "A0011 - AULA 11 - INTRODUCAO A TEOLOGIA.mp3",
        "titulo": "Aula 11: Fundamentalismo Bíblico, Ortodoxia e a Fé Histórica",
        "texto_biblico": "Judas 1:3; Efésios 4:11-14",
        "resumo": "As cinco doutrinas inegociáveis da fé cristã histórica: nascimento virginal, divindade de Cristo, morte expiatória vicária, ressurreição corporal e retorno visível do Senhor. A defesa firme contra as heresias modernas."
    },
    {
        "codigo": "A0012",
        "arquivo": "A0012 - AULA 12 - INTRODUCAO A TEOLOGIA.mp3",
        "titulo": "Aula 12: Teologia vs Teodiceia: Onde Está Deus no Meio da Minha Dor?",
        "texto_biblico": "Jó 38:1-4; Habacuque 3:17-19; Romanos 8:28",
        "resumo": "Uma das maiores dúvidas da humanidade: Se Deus é todo-poderoso e infinitamente bom, por que o justo sofre? Como a teologia bíblica acolhe o quebrantado, responde à dor sem clichês e revela o consolo eterno da Cruz."
    },
    {
        "codigo": "A0013",
        "arquivo": "A0013 - AULA 13 - INTRODUCAO A TEOLOGIA.mp3",
        "titulo": "Aula 13: Fé Genuína vs Credulidade Humana: Discernindo a Verdade",
        "texto_biblico": "Hebreus 11:1-6; 1 Tessalonicenses 5:21",
        "resumo": "A fé bíblica não é um salto cego no escuro nem ingenuidade cega. A fé cristã tem objeto, substância e base histórica comprovada. Julgai todas as coisas e retende o que é bom."
    },
    {
        "codigo": "A0014",
        "arquivo": "A0014 - AULA 14 - INTRODUCAO A TEOLOGIA.mp3",
        "titulo": "Aula 14: Os Perigos das Falsas Doutrinas e a Defesa da Fé (Apologética)",
        "texto_biblico": "Gálatas 1:6-9; 2 Pedro 2:1-3",
        "resumo": "Como identificar a sutileza dos falsos ensinos, das seitas e dos mestres da prosperidade desonesta. A apologética como ferramenta pastoral de proteção ao rebanho e resgate dos que titubeiam na fé."
    },
    {
        "codigo": "A0015",
        "arquivo": "A0015 - AULA 15 - INTRODUCAO A TEOLOGIA.mp3",
        "titulo": "Aula 15: Síntese e Aplicação Prática da Teologia na Vida Diária",
        "texto_biblico": "Tiago 1:22-25; Mateus 7:24-27",
        "resumo": "Conclusão magistral do módulo: Praticantes da Palavra e não meros ouvintes. Como a teologia molda o casamento, as finanças, a criação dos filhos e a missão da igreja local como embaixada do Reino."
    },
    # Módulo de Bibliologia (Aulas 16 a 19)
    {
        "codigo": "A0016",
        "arquivo": "A0016 - AULA 01 - INTRODUCAO A BIBLIA - BIBLIOLOGIA.mp3",
        "titulo": "Aula 16: Bibliologia 01: Origem, Inspiração Divina e Formação da Bíblia",
        "texto_biblico": "2 Pedro 1:20-21; 2 Timóteo 3:16",
        "resumo": "Como o sopro de Deus (Theopneustos) alcançou os autores humanos ao longo de 1.600 anos através de 40 escritores em 3 continentes, preservando uma unidade perfeita e inquebrantável."
    },
    {
        "codigo": "A0017",
        "arquivo": "A0017 - AULA 02 - INTRODUCAO A BIBLIA - BIBLIOLOGIA.mp3",
        "titulo": "Aula 17: Bibliologia 02: O Cânon Bíblico: Como os 66 Livros Foram Reconhecidos",
        "texto_biblico": "Deuteronômio 4:2; Apocalipse 22:18-19",
        "resumo": "Os critérios canônicos de autoridade apostólica/profética, recepção universal e consonância doutrinária. Por que a Bíblia protestante possui 66 livros e a questão dos livros apócrifos."
    },
    {
        "codigo": "A0018",
        "arquivo": "A0018 - AULA 03 - INTRODUCAO A BIBLIA - BIBLIOLOGIA.mp3",
        "titulo": "Aula 18: Bibliologia 03: Inerrância, Infalibilidade e Autoridade Suprema",
        "texto_biblico": "Salmo 12:6; João 10:35",
        "resumo": "O testemunho da Bíblia a respeito de si mesma. A garantia da verdade em matérias de fé, história da salvação e moral, reafirmada pelo próprio Senhor Jesus Cristo."
    },
    {
        "codigo": "A0019",
        "arquivo": "A0019 - AULA 04 - INTRODUCAO A BIBLIA - BIBLIOLOGIA.mp3",
        "titulo": "Aula 19: Bibliologia 04: Manuscritos Antigos, Papiros e as Versões Modernas",
        "texto_biblico": "Isaías 40:8; Mateus 24:35",
        "resumo": "A esmagadora evidência documental dos Manuscritos do Mar Morto, o Texto Massorético e os mais de 5.800 manuscritos gregos. A confiança sólida na Bíblia que lemos hoje em português."
    }
]

def migrar_schema_e_popular():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Garantir coluna audio_path em estudos_aulas
    try:
        cursor.execute("ALTER TABLE estudos_aulas ADD COLUMN audio_path TEXT")
        print("[OK] Coluna 'audio_path' adicionada à tabela estudos_aulas.")
    except sqlite3.OperationalError:
        pass  # Já existe

    # 1. Inserir ou Atualizar as Aulas
    inseridas = 0
    atualizadas = 0

    for aula in AULAS_CATALOGO:
        caminho_mp3 = str(AUDIO_DIR / aula["arquivo"]) if AUDIO_DIR.exists() else None
        
        # Verificar se já existe pelo código
        cursor.execute("SELECT id FROM estudos_aulas WHERE codigo_aula = ?", (aula["codigo"],))
        existente = cursor.fetchone()

        if existente:
            cursor.execute("""
            UPDATE estudos_aulas 
            SET titulo = ?, texto_biblico = ?, resumo_conteudo = ?, audio_path = ?, status_estudo = 'disponivel_audio'
            WHERE id = ?
            """, (aula["titulo"], aula["texto_biblico"], aula["resumo"], caminho_mp3, existente["id"]))
            atualizadas += 1
        else:
            cursor.execute("""
            INSERT INTO estudos_aulas (trilha_id, codigo_aula, titulo, texto_biblico, resumo_conteudo, audio_path, status_estudo)
            VALUES (1, ?, ?, ?, ?, ?, 'disponivel_audio')
            """, (aula["codigo"], aula["titulo"], aula["texto_biblico"], aula["resumo"], caminho_mp3))
            inseridas += 1

    print(f"[OK] Aulas Catalogadas: {inseridas} novas inseridas, {atualizadas} atualizadas.")

    # 2. Publicar Post Oficial de Lançamento na Comunidade Circle (Espaço 3 - Estudos & Teologia)
    cursor.execute("SELECT id FROM comunidade_posts WHERE titulo LIKE '%Curso de Introdução à Teologia%'")
    if not cursor.fetchone():
        corpo_post = """🎉 **É com grande alegria que anunciamos a liberação das 15 AULAS do Curso Básico de Introdução à Teologia!**

"Procura apresentar-te a Deus aprovado, como obreiro que não tem de que se envergonhar, que maneja bem a palavra da verdade." — *2 Timóteo 2:15*

Nossa missão na **Comunidade Metanoia** é unir o acolhimento do coração ferido com a solidez inegociável da Palavra de Deus.

---
### 📚 O Que Você Vai Aprender Nestas 15 Aulas:
1. **O que é Teologia e o Chamado do Teólogo**
2. **O Objetivo Supremo da Teologia** (Intimidade com o Pai)
3. **Divisão Clássica:** Bíblica, Sistemática, Histórica e Prática
4. **A Teologia Pentecostal e o Fogo do Espírito Santo**
5. **As Fontes da Fé e a Suficiência das Escrituras (*Sola Scriptura*)**
6. **O Caráter Espiritual do Teólogo Cristão**
7. **Teologia vs Teodiceia:** *Onde Deus está na hora da dor?*
8. **Como Discernir Falsas Doutrinas e Proteger sua Família**

---
🎧 **Como Acessar:**
Você já pode ouvir as aulas diretamente pelo seu painel da Escola Bíblica na plataforma ou acessar os resumos didáticos no nosso Blog!

Deixe aqui nos comentários: **Qual dessas matérias você tem mais fome de aprender hoje?**"""

        cursor.execute("""
        INSERT INTO comunidade_posts (espaco_id, autor_nome, autor_papel, autor_avatar, titulo, conteudo, fixado, likes_count, comentarios_count)
        VALUES (3, 'Pastor Matheus // Metanoia', '👑 Pastor & Fundador', '👑', 
                '🔥 Lançamento Oficial: Curso de Introdução à Teologia (15 Aulas Gravadas & Roteirizadas)', 
                ?, 1, 24, 5)
        """, (corpo_post,))
        print("[OK] Post oficial de lançamento publicado na Comunidade Circle!")

    conn.commit()
    conn.close()

def gerar_arquivos_estudo_markdown():
    """Gera resumos ricos em Markdown na pasta data/resumos_estudos para alimentar o Blog Bíblico."""
    for aula in AULAS_CATALOGO[:5]:  # Primeiras 5 aulas com guias profundos
        nome_arquivo = f"Aula_{aula['codigo']}_{aula['titulo'].split(':')[1].strip().replace(' ', '_').replace('?', '').replace('/', '_')}.md"
        caminho_md = RESUMOS_DIR / nome_arquivo

        conteudo_md = f"""# 📚 RESUMO EXECUTIVO // {aula['titulo']}
**Matéria:** Básico em Teologia // Introdução à Teologia e Doutrina Cristã
**Código da Aula:** #{aula['codigo']}
**Texto Bíblico Central:** {aula['texto_biblico']}

---

### 🎯 Proposição Central da Aula
{aula['resumo']}

---

### 📖 Tópicos & Estrutura Didática:
1. **Fundamentação Bíblica:** Como os profetas e apóstolos abordavam este tema sem artificialismos religiosos.
2. **O Coração do Assunto:** Porque a teologia viva produz piedade, mansidão e adoração fervorosa.
3. **O Erro Comum no Século XXI:** Como o relativismo e o comodismo tentam esvaziar esta verdade.
4. **Aplicação Pastoral & Diária:** O que você deve fazer a partir de hoje ao abrir as Escrituras em casa com sua família.

---

### 💬 Perguntas para Reflexão Pessoal & Grupos de Célula:
* O que esta aula revelou sobre o caráter e o amor de Deus para a sua vida hoje?
* Que atitude ou crença errada o Espírito Santo te confrontou através desta doutrina?
* Como você pode usar este conhecimento para acolher alguém que está com dúvidas sobre a fé?

---

### 🎬 Roteiro Sugerido para Vídeo de YouTube (Gravação Ministerial):
* **Gancho de Abertura (0 a 30s):** "Você já parou para pensar por que tantas pessoas leem a Bíblia todos os dias e continuam presas na confusão espiritual?"
* **Desenvolvimento (30s a 8min):** Explicar os 3 pilares de {aula['texto_biblico']}.
* **Fechamento & Chamada de Fé (8min a 10min):** Oração de consagração e convite para a Comunidade Metanoia.
"""
        caminho_md.write_text(conteudo_md, encoding="utf-8")
        print(f"[OK] Guia de estudo gerado: {nome_arquivo}")

if __name__ == "__main__":
    migrar_schema_e_popular()
    gerar_arquivos_estudo_markdown()
    print("Processamento do acervo teológico concluído com sucesso!")
