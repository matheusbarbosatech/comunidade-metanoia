"""Serviço de Gamificação Bíblica (Estilo Duolingo) para o Módulo 01 de Teologia."""
import json
import sqlite3
from typing import Dict, Any, List, Optional
from app.db.database import get_connection

AUDIO_DIR = r"C:\Users\matheus\Desktop\01_Basico_em_Teologia"
APOSTILA_TEOLOGIA = r"C:\Users\matheus\Desktop\ACADEMIA DE PREGADORES\ACADEMIA DE PREGADORES\BÁSICO EM TEOLOGIA\_Apostila_Modulo_1226_01._INTRODUCAO_A_TEOLOGIA.pdf"
APOSTILA_BIBLIOLOGIA = r"C:\Users\matheus\Desktop\ACADEMIA DE PREGADORES\ACADEMIA DE PREGADORES\BÁSICO EM TEOLOGIA\_Apostila_Modulo_1227_02._BIBLIOLOGIA.pdf"

DADOS_AULAS_GAMIFICADAS = [
    {
        "codigo": "A0001",
        "numero": 1,
        "mundo": 1,
        "mundo_nome": "O Despertar da Mente & O Chamado",
        "titulo": "Aula 01: O Que É Teologia e o Chamado do Teólogo",
        "texto_biblico": "2 Timóteo 2:15; Oséias 4:6",
        "resumo": "Definição etimológica (Theos + Logos). A teologia como ciência de Deus e de suas relações com o homem e o universo. Por que todo cristão, querendo ou não, é um teólogo e como ter uma fé embasada nas Escrituras sem cair no intelectualismo frio.",
        "icone": "📖",
        "audio_arquivo": "A0001 - AULA 01 - INTRODUCAO A TEOLOGIA.mp3",
        "apostila_path": APOSTILA_TEOLOGIA,
        "pergunta": "Qual é o sentido etimológico original do termo Teologia?",
        "opcoes": [
            "Theos (Deus) + Logos (Discurso / Estudo racional)",
            "Theos (Igreja) + Logos (Tradição eclesiástica)",
            "Theos (Templo) + Logos (Ritos sacerdotais)"
        ],
        "correta": "Theos (Deus) + Logos (Discurso / Estudo racional)",
        "explicacao": "Perfeito! Theos significa Deus e Logos significa razão, palavra, estudo. Teologia é refletir com reverência sobre a revelação divina."
    },
    {
        "codigo": "A0002",
        "numero": 2,
        "mundo": 1,
        "mundo_nome": "O Despertar da Mente & O Chamado",
        "titulo": "Aula 02: O Objetivo Supremo da Teologia: Conhecer e Adorar",
        "texto_biblico": "Jeremias 9:23-24; João 17:3",
        "resumo": "O propósito da teologia não é o mero acúmulo de conhecimento intelectual, mas a transformação interior (Metanoia) e a intimidade espiritual com o Criador. A oração como combustível da reflexão bíblica.",
        "icone": "🎯",
        "audio_arquivo": "A0002 - AULA 02 - INTRODUCAO A TEOLOGIA.mp3",
        "apostila_path": APOSTILA_TEOLOGIA,
        "pergunta": "Qual o objetivo final e supremo do estudo da Teologia segundo Jeremias 9:23-24?",
        "opcoes": [
            "Vencer debates religiosos na internet",
            "Conhecer e glorificar a Deus de todo o coração",
            "Alcançar títulos eclesiásticos de prestígio"
        ],
        "correta": "Conhecer e glorificar a Deus de todo o coração",
        "explicacao": "Glória a Deus! A teologia bíblica gera adoração sincera e coração quebrantado, nunca soberba."
    },
    {
        "codigo": "A0003",
        "numero": 3,
        "mundo": 1,
        "mundo_nome": "O Despertar da Mente & O Chamado",
        "titulo": "Aula 03: Divisão Clássica da Teologia",
        "texto_biblico": "Lucas 24:27; Atos 17:11",
        "resumo": "Panorama dos quatro ramos fundamentais da teologia: Teologia Bíblica (desenvolvimento histórico-revelacional), Sistemática (doutrinas organizadas), Histórica (como a Igreja compreendeu a verdade nos séculos) e Prática (ação pastoral e ética).",
        "icone": "🏛️",
        "audio_arquivo": "A0003 - AULA 03 - INTRODUCAO A TEOLOGIA.mp3",
        "apostila_path": APOSTILA_TEOLOGIA,
        "pergunta": "Quais são os 4 ramos da divisão clássica da Teologia?",
        "opcoes": [
            "Bíblica, Sistemática, Histórica e Prática",
            "Mística, Política, Filosófica e Dogmática",
            "Literal, Alegórica, Poética e Canônica"
        ],
        "correta": "Bíblica, Sistemática, Histórica e Prática",
        "explicacao": "Excelente! Essa divisão nos ajuda a investigar o texto na sua história, sistema doutrinário e aplicação diária."
    },
    {
        "codigo": "A0004",
        "numero": 4,
        "mundo": 1,
        "mundo_nome": "O Despertar da Mente & O Chamado",
        "titulo": "Aula 04: Teologia Bíblica vs Teologia Sistemática",
        "texto_biblico": "Romanos 11:33-36; 2 Pedro 3:16",
        "resumo": "Como trabalhar a linha do tempo da Revelação sem distorcer o ensino bíblico. A importância de deixar a Bíblia interpretar a si mesma antes de construir sistemas dogmáticos rígidos.",
        "icone": "⚖️",
        "audio_arquivo": "A0004 - AULA 04 - INTRODUCAO A TEOLOGIA.mp3",
        "apostila_path": APOSTILA_TEOLOGIA,
        "pergunta": "Qual o foco central da Teologia Bíblica?",
        "opcoes": [
            "A revelação progressiva de Deus ao longo da história bíblica",
            "Criar regras e manuais de membros de igrejas",
            "Focar exclusivamente na filosofia grega antiga"
        ],
        "correta": "A revelação progressiva de Deus ao longo da história bíblica",
        "explicacao": "Muito bem! A Teologia Bíblica rastreia o desdobramento da graça divina desde o Éden até a Nova Jerusalém."
    },
    {
        "codigo": "A0005",
        "numero": 5,
        "mundo": 1,
        "mundo_nome": "O Despertar da Mente & O Chamado",
        "titulo": "Aula 05: A Teologia Pentecostal e a Operação Viva do Espírito",
        "texto_biblico": "Atos 1:8; 1 Coríntios 2:10-14",
        "resumo": "O equilíbrio vital entre a Palavra e o Espírito. Como a experiência de Pentecostes ilumina a mente do estudante e capacita o crente para testemunho com autoridade, sinais e amor sacrificial.",
        "icone": "🔥",
        "audio_arquivo": "A0005 - AULA 05 - INTRODUCAO A TEOLOGIA.mp3",
        "apostila_path": APOSTILA_TEOLOGIA,
        "pergunta": "Qual o equilíbrio essencial ensinado na Teologia Pentecostal sadia?",
        "opcoes": [
            "Palavra sem o Espírito Santo",
            "União indissolúvel entre a sã doutrina da Palavra e o fogo do Espírito",
            "Apenas emoções sem qualquer fundamento nas Escrituras"
        ],
        "correta": "União indissolúvel entre a sã doutrina da Palavra e o fogo do Espírito",
        "explicacao": "Amém! A Palavra sem o Espírito seca; o Espírito sem a Palavra dispersa; mas a Palavra com o Espírito inflama a Igreja!"
    },
    {
        "codigo": "A0006",
        "numero": 6,
        "mundo": 2,
        "mundo_nome": "A Rocha Firme das Escrituras",
        "titulo": "Aula 06: A Necessidade de Fazer Teologia no Século XXI",
        "texto_biblico": "1 Pedro 3:15; Tito 1:9",
        "resumo": "Responder ao relativismo cultural, secularismo e heresias digitais com mansidão, firmeza apologética e integridade de vida.",
        "icone": "⏳",
        "audio_arquivo": "A0006 - AULA 06 - INTRODUCAO A TEOLOGIA.mp3",
        "apostila_path": APOSTILA_TEOLOGIA,
        "pergunta": "Como 1 Pedro 3:15 nos orienta a defender a nossa esperança em Cristo?",
        "opcoes": [
            "Com ataques verbais e soberba intelectual",
            "Com mansidão, respeito e boa consciência",
            "Fugindo de qualquer conversa ou questionamento"
        ],
        "correta": "Com mansidão, respeito e boa consciência",
        "explicacao": "Correto! A apologética bíblica é feita de joelhos, com amor pastoral e mansidão."
    },
    {
        "codigo": "A0007",
        "numero": 7,
        "mundo": 2,
        "mundo_nome": "A Rocha Firme das Escrituras",
        "titulo": "Aula 07: As Fontes da Teologia & Revelação Geral e Especial",
        "texto_biblico": "Salmo 19:1-4; 2 Timóteo 3:16",
        "resumo": "A criação manifesta a glória de Deus (Revelação Geral), mas somente as Escrituras revelam o plano redentor de Cristo (Revelação Especial).",
        "icone": "📜",
        "audio_arquivo": "A0007 - AULA 07 - INTRODUCAO A TEOLOGIA.mp3",
        "apostila_path": APOSTILA_TEOLOGIA,
        "pergunta": "O que a Revelação Especial oferece que a Revelação Geral (natureza) não pode conceder?",
        "opcoes": [
            "Apenas noções astronômicas do universo",
            "O conhecimento salvífico de Jesus Cristo e o perdão dos pecados",
            "Explicações biológicas sobre plantas"
        ],
        "correta": "O conhecimento salvífico de Jesus Cristo e o perdão dos pecados",
        "explicacao": "Exato! A natureza mostra que Deus existe, mas a cruz revela quem Ele é e como somos salvos."
    },
    {
        "codigo": "A0008",
        "numero": 8,
        "mundo": 2,
        "mundo_nome": "A Rocha Firme das Escrituras",
        "titulo": "Aula 08: A Suficiência das Escrituras (Sola Scriptura)",
        "texto_biblico": "Gálatas 1:8; Apocalipse 22:18-19",
        "resumo": "A Bíblia como única regra infalível de fé e prática cristã. Nenhum dogma ou visão pode sobrepor o texto sagrado inspirado.",
        "icone": "🛡️",
        "audio_arquivo": "A0008 - AULA 08 - INTRODUCAO A TEOLOGIA.mp3",
        "apostila_path": APOSTILA_TEOLOGIA,
        "pergunta": "O princípio de Sola Scriptura afirma que:",
        "opcoes": [
            "A Bíblia é a suprema e inerrante autoridade sobre tradições humanas",
            "Não devemos ler nenhum livro histórico ou comentário",
            "Cada pessoa pode inventar suas próprias doutrinas"
        ],
        "correta": "A Bíblia é a suprema e inerrante autoridade sobre tradições humanas",
        "explicacao": "Glória a Deus! Tudo é examinado e provado à luz da Palavra inspirada."
    },
    {
        "codigo": "A0009",
        "numero": 9,
        "mundo": 2,
        "mundo_nome": "A Rocha Firme das Escrituras",
        "titulo": "Aula 09: O Perfil Espiritual e Moral do Teólogo",
        "texto_biblico": "Esdras 7:10; 1 Timóteo 4:16",
        "resumo": "O perigo do orgulho intelectual. A tríade de Esdras: dispor o coração para buscar a Lei, praticá-la na vida e só então ensiná-la.",
        "icone": "🕊️",
        "audio_arquivo": "A0009 - AULA 09 - INTRODUCAO A TEOLOGIA.mp3",
        "apostila_path": APOSTILA_TEOLOGIA,
        "pergunta": "Qual era a ordem do ministério do escriba Esdras em Esdras 7:10?",
        "opcoes": [
            "Ensinar aos outros antes de praticar em sua vida",
            "Buscar a lei do Senhor, praticá-la, e então ensinar",
            "Buscar aplausos das multidões em Jerusalém"
        ],
        "correta": "Buscar a lei do Senhor, praticá-la, e então ensinar",
        "explicacao": "Perfeito! A prática precede o ensino. Não há sã teologia sem santidade de vida."
    },
    {
        "codigo": "A0010",
        "numero": 10,
        "mundo": 2,
        "mundo_nome": "A Rocha Firme das Escrituras",
        "titulo": "Aula 10: Doutrina, Dogma e Religião",
        "texto_biblico": "Mateus 15:8-9; Romanos 14:1-4",
        "resumo": "Discernindo os fundamentos imutáveis da fé das tradições culturais secundárias de homens. Guardando o amor no essencial.",
        "icone": "💎",
        "audio_arquivo": "A0010 - AULA 10 - INTRODUCAO A TEOLOGIA.mp3",
        "apostila_path": APOSTILA_TEOLOGIA,
        "pergunta": "Em coisas essenciais a unidade, em secundárias a liberdade, e em tudo:",
        "opcoes": [
            "O amor cristão fraternal",
            "A disputa e divisão de igrejas",
            "A exclusão imediata do irmão"
        ],
        "correta": "O amor cristão fraternal",
        "explicacao": "Maravilha! Esse é o lema da Igreja de Cristo: no essencial unidade, no não-essencial liberdade, e em tudo amor."
    },
    {
        "codigo": "A0011",
        "numero": 11,
        "mundo": 3,
        "mundo_nome": "O Crisol da Fé e da Dor",
        "titulo": "Aula 11: Fundamentalismo Bíblico e Ortodoxia Sadia",
        "texto_biblico": "Judas 1:3; Tito 2:1",
        "resumo": "Batalhar pela fé que uma vez foi entregue aos santos sem cair no farisaísmo legalista ou no extremismo raivoso.",
        "icone": "⚓",
        "audio_arquivo": "A0011 - AULA 11 - INTRODUCAO A TEOLOGIA.mp3",
        "apostila_path": APOSTILA_TEOLOGIA,
        "pergunta": "O que Judas nos exorta em Judas 1:3?",
        "opcoes": [
            "Batalhar pela fé que uma vez foi dada aos santos",
            "Criar inovações espirituais sem apoio bíblico",
            "Desprezar as Escrituras antigas"
        ],
        "correta": "Batalhar pela fé que uma vez foi dada aos santos",
        "explicacao": "Excelente! A ortodoxia verdadeira preserva a mensagem apostólica sem tirar nem acrescentar."
    },
    {
        "codigo": "A0012",
        "numero": 12,
        "mundo": 3,
        "mundo_nome": "O Crisol da Fé e da Dor",
        "titulo": "Aula 12: Teodiceia: Onde Está Deus na Minha Dor?",
        "texto_biblico": "Jó 42:1-6; 2 Coríntios 12:9-10",
        "resumo": "A reconciliação da soberania de Deus com a existência do mal e do sofrimento. O consolo de Cristo na cruz ao lado de quem chora.",
        "icone": "💔",
        "audio_arquivo": "A0012 - AULA 12 - INTRODUCAO A TEOLOGIA.mp3",
        "apostila_path": APOSTILA_TEOLOGIA,
        "pergunta": "O que a Teodiceia cristã nos ensina sobre a presença de Deus no sofrimento?",
        "opcoes": [
            "Que Deus é indiferente e abandonou a humanidade à própria sorte",
            "Que em Cristo Ele sofreu conosco e Sua graça nos sustenta até a redenção",
            "Que todo sofrimento é resultado imediato de falta de fé"
        ],
        "correta": "Que em Cristo Ele sofreu conosco e Sua graça nos sustenta até a redenção",
        "explicacao": "Glória a Deus! Ele é o Deus Emanuel — o Deus conosco até mesmo no vale da sombra da morte."
    },
    {
        "codigo": "A0013",
        "numero": 13,
        "mundo": 3,
        "mundo_nome": "O Crisol da Fé e da Dor",
        "titulo": "Aula 13: Fé Genuína vs Credulidade Humana",
        "texto_biblico": "Hebreus 11:1; Provérbios 14:15",
        "resumo": "A diferença vital entre a fé bíblica fundamentada no caráter de Deus e a credulidade cega que engole qualquer engano humano.",
        "icone": "🌱",
        "audio_arquivo": "A0013 - AULA 13 - INTRODUCAO A TEOLOGIA.mp3",
        "apostila_path": APOSTILA_TEOLOGIA,
        "pergunta": "Segundo Provérbios 14:15, qual a atitude do tolo versus a do prudente?",
        "opcoes": [
            "O ingênuo dá crédito a toda palavra, mas o prudente atenta para seus passos",
            "Ambos acreditam em boatos sem examinar nada",
            "O prudente desiste de crer em Deus"
        ],
        "correta": "O ingênuo dá crédito a toda palavra, mas o prudente atenta para seus passos",
        "explicacao": "Isso mesmo! O crente bereano confere na Palavra antes de abraçar qualquer ensinamento."
    },
    {
        "codigo": "A0014",
        "numero": 14,
        "mundo": 3,
        "mundo_nome": "O Crisol da Fé e da Dor",
        "titulo": "Aula 14: Perigos das Falsas Doutrinas & Apologética Mansa",
        "texto_biblico": "Efésios 4:14; 2 Timóteo 4:3-4",
        "resumo": "Como identificar o evangelho da prosperidade ganancioso, o misticismo sincretista e manter os olhos fixos na suficiência da Graça.",
        "icone": "⚔️",
        "audio_arquivo": "A0014 - AULA 14 - INTRODUCAO A TEOLOGIA.mp3",
        "apostila_path": APOSTILA_TEOLOGIA,
        "pergunta": "Qual o antídoto bíblico em Efésios 4:14 contra ventos de doutrina enganosa?",
        "opcoes": [
            "O crescimento no conhecimento do Filho de Deus e maturidade espiritual",
            "Comprar amuletos ungidos e campanhas financeiras",
            "Isolar-se de qualquer comunidade de fé"
        ],
        "correta": "O crescimento no conhecimento do Filho de Deus e maturidade espiritual",
        "explicacao": "Glória! O discipulado constante nos protege das ciladas do erro doutrinário."
    },
    {
        "codigo": "A0015",
        "numero": 15,
        "mundo": 3,
        "mundo_nome": "O Crisol da Fé e da Dor",
        "titulo": "Aula 15: Síntese e Aplicação Prática: Teologia Viva",
        "texto_biblico": "Tiago 1:22; Miquéias 6:8",
        "resumo": "Conclusão do Módulo 01: Fazer teologia de joelhos e com as mãos estendidas aos necessitados. Praticantes da Palavra e não meros ouvintes.",
        "icone": "👑",
        "audio_arquivo": "A0015 - AULA 15 - INTRODUCAO A TEOLOGIA.mp3",
        "apostila_path": APOSTILA_TEOLOGIA,
        "pergunta": "De acordo com Tiago 1:22, o que devemos ser em relação à Palavra?",
        "opcoes": [
            "Apenas acumuladores de teorias e debates",
            "Praticantes da Palavra e não meros ouvintes",
            "Críticos distantes da dor do próximo"
        ],
        "correta": "Praticantes da Palavra e não meros ouvintes",
        "explicacao": "Parabéns, Discípulo! Você completou a jornada de 15 aulas fundamentais da Teologia Metanoia!"
    }
]

def init_gamificacao_db(conn: sqlite3.Connection):
    """Garante que as tabelas de gamificação e o conteúdo das 15 aulas existam."""
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gamificacao_perfil (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_nome TEXT DEFAULT 'Discípulo Bereano',
        xp_total INTEGER DEFAULT 450,
        nivel TEXT DEFAULT 'Discípulo Bereano Nível II',
        streak_dias INTEGER DEFAULT 7,
        ultimo_estudo_data DATE DEFAULT CURRENT_DATE
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trilha_gamificada_aulas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_aula TEXT UNIQUE NOT NULL,
        numero_aula INTEGER NOT NULL,
        mundo INTEGER NOT NULL,
        mundo_nome TEXT NOT NULL,
        titulo TEXT NOT NULL,
        texto_biblico TEXT,
        resumo TEXT,
        icone TEXT DEFAULT '📖',
        audio_path TEXT,
        apostila_path TEXT,
        xp_recompensa INTEGER DEFAULT 50,
        quiz_pergunta TEXT,
        quiz_opcoes_json TEXT,
        quiz_resposta_correta TEXT,
        quiz_explicacao TEXT,
        concluida BOOLEAN DEFAULT 0,
        acertos_count INTEGER DEFAULT 0
    );
    """)

    # Perfil padrão se vazio
    cursor.execute("SELECT COUNT(*) as tot FROM gamificacao_perfil")
    if cursor.fetchone()["tot"] == 0:
        cursor.execute("""
        INSERT INTO gamificacao_perfil (usuario_nome, xp_total, nivel, streak_dias)
        VALUES ('Discípulo Bereano', 450, 'Discípulo Bereano Nível II', 7)
        """)

    # Povoar as 15 aulas
    cursor.execute("SELECT COUNT(*) as tot FROM trilha_gamificada_aulas")
    if cursor.fetchone()["tot"] < len(DADOS_AULAS_GAMIFICADAS):
        for aula in DADOS_AULAS_GAMIFICADAS:
            audio_full = f"{AUDIO_DIR}\\{aula['audio_arquivo']}"
            cursor.execute("""
            INSERT OR REPLACE INTO trilha_gamificada_aulas (
                codigo_aula, numero_aula, mundo, mundo_nome, titulo, texto_biblico, resumo, icone,
                audio_path, apostila_path, xp_recompensa, quiz_pergunta, quiz_opcoes_json,
                quiz_resposta_correta, quiz_explicacao, concluida
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                aula["codigo"],
                aula["numero"],
                aula["mundo"],
                aula["mundo_nome"],
                aula["titulo"],
                aula["texto_biblico"],
                aula["resumo"],
                aula["icone"],
                audio_full,
                aula["apostila_path"],
                50,
                aula["pergunta"],
                json.dumps(aula["opcoes"], ensure_ascii=False),
                aula["correta"],
                aula["explicacao"],
                1 if aula["numero"] == 1 else 0
            ))

    conn.commit()


def get_modulo1_data() -> Dict[str, Any]:
    """Retorna dados completos do Módulo 01 para API ou UI."""
    conn = get_connection()
    init_gamificacao_db(conn)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM gamificacao_perfil LIMIT 1")
    perfil_row = cursor.fetchone()
    perfil = dict(perfil_row) if perfil_row else {
        "usuario_nome": "Discípulo Bereano",
        "xp_total": 450,
        "nivel": "Discípulo Bereano Nível II",
        "streak_dias": 7
    }

    cursor.execute("SELECT * FROM trilha_gamificada_aulas ORDER BY numero_aula ASC")
    aulas_rows = cursor.fetchall()
    conn.close()

    aulas = []
    concluidas_count = 0
    mundos_dict = {}

    for row in aulas_rows:
        d = dict(row)
        d["quiz_opcoes"] = json.loads(d["quiz_opcoes_json"]) if d.get("quiz_opcoes_json") else []
        if d.get("concluida"):
            concluidas_count += 1

        mundo_id = d["mundo"]
        if mundo_id not in mundos_dict:
            mundos_dict[mundo_id] = {
                "id": mundo_id,
                "nome": d["mundo_nome"],
                "aulas": []
            }
        mundos_dict[mundo_id]["aulas"].append(d)
        aulas.append(d)

    total_aulas = len(aulas)
    porcentagem = round((concluidas_count / total_aulas * 100), 1) if total_aulas > 0 else 0

    perfil["aulas_concluidas"] = concluidas_count
    perfil["total_aulas"] = total_aulas
    perfil["porcentagem"] = porcentagem

    return {
        "perfil": perfil,
        "mundos": list(mundos_dict.values()),
        "aulas": aulas
    }


def responder_quiz(codigo_aula: str, resposta: str) -> Dict[str, Any]:
    """Valida a resposta do quiz, soma XP e marca conclusão."""
    conn = get_connection()
    init_gamificacao_db(conn)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM trilha_gamificada_aulas WHERE codigo_aula = ?", (codigo_aula,))
    aula_row = cursor.fetchone()
    if not aula_row:
        conn.close()
        return {"sucesso": False, "mensagem": "Aula não encontrada."}

    aula = dict(aula_row)
    correta = aula["quiz_resposta_correta"].strip().lower() == resposta.strip().lower()

    if correta:
        # Marcar aula como concluída e somar XP
        cursor.execute("""
        UPDATE trilha_gamificada_aulas 
        SET concluida = 1, acertos_count = acertos_count + 1 
        WHERE codigo_aula = ?
        """, (codigo_aula,))

        cursor.execute("UPDATE gamificacao_perfil SET xp_total = xp_total + 50")
        conn.commit()

        cursor.execute("SELECT xp_total, nivel, streak_dias FROM gamificacao_perfil LIMIT 1")
        p = dict(cursor.fetchone())
        conn.close()

        return {
            "sucesso": True,
            "acertou": True,
            "xp_ganho": 50,
            "novo_xp": p["xp_total"],
            "nivel": p["nivel"],
            "streak_dias": p["streak_dias"],
            "explicacao": aula["quiz_explicacao"],
            "mensagem": "🎉 Resposta Correta! Você ganhou +50 XP!"
        }
    else:
        conn.close()
        return {
            "sucesso": True,
            "acertou": False,
            "xp_ganho": 0,
            "explicacao": aula["quiz_explicacao"],
            "mensagem": "💡 Quase lá! Confira a dica bíblica e tente novamente."
        }
