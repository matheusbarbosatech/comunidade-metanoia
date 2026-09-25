"""Camada de banco de dados SQLite para o ecossistema ministerial."""
import sqlite3
from typing import Generator
from app.core.config import DB_PATH

def get_connection() -> sqlite3.Connection:
    """Retorna uma conexão ativa configurada com Row Factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """Inicializa as tabelas fundamentais do ministério e da escola de estudos."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Tabela de Membros & Alunos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS membros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        email TEXT UNIQUE,
        whatsapp TEXT,
        papel TEXT DEFAULT 'aluno', -- aluno, intercessor, lider_celula, pastor
        ativo BOOLEAN DEFAULT 1,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Cursos & Trilhas de Estudo (Inspirado no currículo teológico)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trilhas_teologicas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nivel TEXT NOT NULL, -- Basico, Medio, Bacharel, Especializacao
        materia TEXT NOT NULL, -- Ex: Bibliologia, Hermeneutica, Escatologia
        total_aulas INTEGER DEFAULT 0,
        descricao TEXT,
        apostila_path TEXT
    );
    """)

    # 3. Aulas e Estudos (Base para os Vídeos Longos do YouTube)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estudos_aulas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trilha_id INTEGER REFERENCES trilhas_teologicas(id),
        codigo_aula TEXT, -- Ex: #A0001, #A0189
        titulo TEXT NOT NULL,
        texto_biblico TEXT,
        resumo_conteudo TEXT,
        video_youtube_url TEXT,
        status_estudo TEXT DEFAULT 'a_estudar', -- a_estudar, estudado, roteirizado, gravado
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 4. Cortes Curtos derivados dos Vídeos Longos (Reels / TikTok / Shorts)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cortes_videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        aula_id INTEGER REFERENCES estudos_aulas(id),
        titulo_corte TEXT NOT NULL,
        hook TEXT NOT NULL,
        timestamp_inicio TEXT,
        timestamp_fim TEXT,
        status TEXT DEFAULT 'planejado', -- planejado, renderizado, publicado
        video_path TEXT,
        publicado_em TIMESTAMP
    );
    """)

    # 5. Devocionais da Forja dos 90 Dias
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS devocionais_90d (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dia INTEGER UNIQUE NOT NULL,
        fase TEXT NOT NULL, -- O Resgatado, O Discipulo, O Guerreiro, O Sacerdote, O Patriarca
        titulo TEXT NOT NULL,
        versiculo TEXT NOT NULL,
        conteudo TEXT NOT NULL,
        ordem_missao TEXT,
        audio_path TEXT
    );
    """)

    # 6. Mural de Oração da Célula Digital
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pedidos_oracao (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome_solicitante TEXT NOT NULL,
        motivo TEXT NOT NULL,
        categoria TEXT DEFAULT 'geral', -- saude, familia, espiritual, financas
        anonimo BOOLEAN DEFAULT 0,
        status TEXT DEFAULT 'em_oracao', -- em_oracao, respondido
        intercessoes_count INTEGER DEFAULT 0,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 7. Células Digitais e Encontros Semanais
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS encontros_celula (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tema TEXT NOT NULL,
        data_hora TIMESTAMP NOT NULL,
        link_sala TEXT,
        material_apoio TEXT,
        resumo_pos_encontro TEXT,
        realizado BOOLEAN DEFAULT 0
    );
    """)

    # 8. Músicas & Louvores (Playlist Matheus & Repertório Ministerial)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS musicas_louvores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        artista TEXT NOT NULL,
        arquivo_nome TEXT NOT NULL UNIQUE,
        caminho_completo TEXT NOT NULL,
        tamanho_mb REAL DEFAULT 0,
        categoria TEXT DEFAULT 'Geral',
        tags TEXT DEFAULT '',
        favorito BOOLEAN DEFAULT 0,
        reproducoes_count INTEGER DEFAULT 0,
        cdn_url TEXT DEFAULT '',
        adicionado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Migração segura para garantir existência da coluna cdn_url
    try:
        cursor.execute("ALTER TABLE musicas_louvores ADD COLUMN cdn_url TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass

    # 9. Artigos do Blog Bíblico & Estudos da Palavra (Automated Blog Engine)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS artigos_blog (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE NOT NULL,
        titulo TEXT NOT NULL,
        subtitulo TEXT,
        categoria TEXT DEFAULT 'Teologia & Vida Cristã',
        tempo_leitura_min INTEGER DEFAULT 5,
        autor TEXT DEFAULT 'Matheus Barbosa // Comunidade Metanoia',
        conteudo_markdown TEXT NOT NULL,
        texto_biblico TEXT,
        visualizacoes INTEGER DEFAULT 0,
        publicado BOOLEAN DEFAULT 1,
        publicado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 10. Postagens Automáticas para Redes Sociais (Instagram, WhatsApp, Shorts, X)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS postagens_redes_sociais (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        artigo_slug TEXT NOT NULL,
        plataforma TEXT NOT NULL, -- instagram, whatsapp, shorts, twitter, telegram
        tipo TEXT DEFAULT 'carrossel', -- carrossel, legenda, roteiro_video, mensagem_grupo, thread
        titulo TEXT NOT NULL,
        conteudo TEXT NOT NULL,
        hashtags TEXT DEFAULT '',
        status TEXT DEFAULT 'pronto', -- pronto, agendado, publicado
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 11. Espaços / Canais da Rede Social Comunitária (Estilo Circle.so)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comunidade_espacos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        slug TEXT UNIQUE NOT NULL,
        nome TEXT NOT NULL,
        icone TEXT NOT NULL,
        descricao TEXT,
        ordem INTEGER DEFAULT 0
    );
    """)

    # 12. Publicações / Posts no Feed Social
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comunidade_posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        espaco_id INTEGER REFERENCES comunidade_espacos(id),
        autor_nome TEXT NOT NULL,
        autor_papel TEXT DEFAULT 'Discípulo',
        autor_avatar TEXT DEFAULT '🕊️',
        titulo TEXT,
        conteudo TEXT NOT NULL,
        anonimo BOOLEAN DEFAULT 0,
        fixado BOOLEAN DEFAULT 0,
        likes_count INTEGER DEFAULT 0,
        comentarios_count INTEGER DEFAULT 0,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 13. Comentários / Respostas aos Posts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comunidade_comentarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER REFERENCES comunidade_posts(id),
        autor_nome TEXT NOT NULL,
        autor_papel TEXT DEFAULT 'Discípulo',
        autor_avatar TEXT DEFAULT '🕊️',
        conteudo TEXT NOT NULL,
        anonimo BOOLEAN DEFAULT 0,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 14. Reações aos Posts (Estou Orando 🤍, Amém 🙏, Glória 🔥)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS comunidade_reacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER REFERENCES comunidade_posts(id),
        tipo TEXT DEFAULT 'orando',
        usuario_identificador TEXT,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Povoamento Inicial de Espaços e Posts da Comunidade se vazio
    cursor.execute("SELECT COUNT(*) as total FROM comunidade_espacos")
    if cursor.fetchone()["total"] == 0:
        espacos_iniciais = [
            ("geral-acolhimento", "Acolhimento & Boas-Vindas", "🕊️", "Apresente-se, conheça outros irmãos e receba as boas-vindas da família.", 1),
            ("pedidos-oracao", "Mural de Oração & Clamor", "🛡️", "Compartilhe suas lutas para intercedermos juntos diante do Pai.", 2),
            ("estudos-biblicos", "Estudos & Teologia Bíblica", "📖", "Insights das apostilas, reflexões bíblicas e dúvidas da Palavra.", 3),
            ("desabafos-sos", "Desabafo Seguro & SOS", "💬", "Espaço com acolhimento fraternal e opção de post anônimo para momentos de crise.", 4),
            ("testemunhos", "Testemunhos & Vitórias", "🏆", "Conte o que Deus realizou na sua vida para edificar toda a comunidade.", 5),
            ("louvores-adoracao", "Louvores & Adoração", "🎵", "Compartilhe louvores, playlists e momentos marcantes de louvor.", 6)
        ]
        cursor.executemany("""
        INSERT INTO comunidade_espacos (slug, nome, icone, descricao, ordem)
        VALUES (?, ?, ?, ?, ?)
        """, espacos_iniciais)

        # Inserir Posts Iniciais Inspiradores
        posts_iniciais = [
            (
                1, "Pastor Matheus // Metanoia", "👑 Pastor & Fundador", "👑",
                "Seja Bem-vindo à Comunidade Metanoia: Você Não Precisa Fingir Força Aqui!",
                "A paz do Senhor a todos os irmãos e irmãs! Criamos este espaço inspirado nas melhores comunidades do mundo para que nenhum servo de Deus lute sozinho no vale da ansiedade ou da solidão. Aqui você tem voz, acolhimento e irmãos fiéis de oração.\n\nSinta-se em casa para deixar um 'Amém' ou se apresentar nos comentários!",
                0, 1, 15, 2
            ),
            (
                2, "Irmão em Cristo", "Intercessor", "🛡️",
                "Clamor por cura e restauração na saúde da minha família",
                "Irmãos amados, peço que levantem um clamor de oração pela saúde da minha mãe que fará exames amanhã e por renovo espiritual para suportar esta semana. Creio no Deus do impossível!",
                0, 0, 9, 1
            ),
            (
                3, "Discípulo Matheus", "Aluno Teologia", "📖",
                "A Graça Imerecida: O que aprendi na Apostila 01 de Teologia",
                "Muitas vezes achamos que precisamos 'comprar' o favor de Deus com nosso esforço. Mas em Romanos aprendemos: 'Nenhuma condenação há para os que estão em Cristo Jesus'. A Graça nos liberta do medo e nos enche de amor.",
                0, 0, 7, 0
            )
        ]
        cursor.executemany("""
        INSERT INTO comunidade_posts (espaco_id, autor_nome, autor_papel, autor_avatar, titulo, conteudo, anonimo, fixado, likes_count, comentarios_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, posts_iniciais)

        # Comentários iniciais
        comentarios_iniciais = [
            (1, "Irmã Débora", "Membro", "🌸", "Amém, Pastor! Que alegria encontrar um lugar de refúgio tão acolhedor. Deus abençoe essa obra!", 0),
            (1, "Lucas Silva", "Membro", "🌱", "Glória a Deus! Chegando de Goiânia para somar no ministério e orar pelos irmãos.", 0),
            (2, "Equipe Pastoral Metanoia", "👑 Pastor & Fundador", "👑", "Colocando a vida da sua mãe no altar de oração hoje na vigília! Receba paz no coração.", 0)
        ]
        cursor.executemany("""
        INSERT INTO comunidade_comentarios (post_id, autor_nome, autor_papel, autor_avatar, conteudo, anonimo)
        VALUES (?, ?, ?, ?, ?, ?)
        """, comentarios_iniciais)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("Banco de dados SQLite inicializado com sucesso!")
