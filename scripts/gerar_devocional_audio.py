"""Gerador de Devocional em Áudio com Voz Neural de IA.
Comunidade Metanoia // "Ninguém luta sozinho"
Gera o primeiro devocional em áudio com voz neural brasileira suave e acolhedora (pt-BR-AntonioNeural)
e cadastra diretamente no acervo da Rádio Web (SQLite).
"""
import sys
import asyncio
from pathlib import Path

# Suporte a Unicode no Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import edge_tts
from app.db.database import get_connection

OUTPUT_DIR = BASE_DIR / "data" / "devocionais"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TEXTO_DEVOCIONAL = """
A paz do Senhor, meu irmão, minha irmã. Aqui é a Comunidade Metanoia.

Eu não sei em que momento do dia essa mensagem te encontra. Talvez seja na calada da madrugada, quando o quarto está escuro e os seus pensamentos gritam. Talvez você esteja no meio de um dia exaustivo, sentindo que a sua força chegou ao fim.

E a pergunta que muitas vezes a gente tem medo de fazer é: Deus, e quando eu não tenho mais forças nem para orar? Quando as palavras simplesmente acabam?

Respira fundo agora por três segundos... solta o ar devagar... e deixa eu te dizer uma verdade que liberta: você não precisa fingir força aqui.

Nos estudos clássicos da Espiritualidade Cristã, aprendemos que os primeiros discípulos e os pais da fé conheciam uma disciplina que o mundo moderno esqueceu: o mistério da solitude e do silêncio diante de Deus.

Nós fomos ensinados por uma religiosidade barulhenta que, para Deus nos ouvir, nós precisamos gritar, barganhar ou fazer orações perfeitas com palavras difíceis.

Mas Jesus nos alertou em Mateus, capítulo 6: Não useis de vãs repetições, como os gentios; porque pensam que pelo muito falar serão ouvidos. Porque o vosso Pai sabe o que vos é necessário, antes mesmo que lho pedirdes.

A Graça de Deus não depende da sua eloquência. O silêncio do seu quarto não é ausência de fé; muitas vezes, é o lugar onde a fé mais genuína nasce: a fé que descansa nos braços do Pai.

O apóstolo Paulo, escrevendo aos Romanos no capítulo 8, versículo 26, deixou uma das frases mais consoladoras de toda a Escritura Sagrada:

E da mesma maneira também o Espírito ajuda as nossas fraquezas; porque não sabemos o que havemos de pedir como convém, mas o mesmo Espírito intercede por nós com gemidos inexprimíveis.

Olhe que revelação profunda:
Quando você não sabe o que pedir...
Quando você chora sem conseguir falar uma frase completa...
Aquele choro, aquele silêncio cansado, não é desprezado no céu.

O próprio Espírito Santo recolhe o seu gemido, traduz diante do Trono da Graça e diz ao Pai: Eu sei o que ele está sentindo. Eu estou sustentando ele agora.

Vamos orar juntos agora? Onde você estiver, se puder, feche os olhos por um instante:

Senhor Deus... nós silenciamos o barulho das cobranças, do medo e da ansiedade neste instante. Recebe o coração deste Teu filho e desta Tua filha. Cura o cansaço da alma. Lembra a eles hoje que a Tua Graça é suficiente e que o Teu poder se aperfeiçoa exatamente na nossa fraqueza. Nós não precisamos carregar o mundo nos ombros, porque o mundo está nas Tuas mãos de amor. Em nome de Jesus, amém.

Guarde isso no seu coração hoje: você não está abandonado e você não está esquecido. Na Comunidade Metanoia, ninguém luta sozinho.

Continue conectado com a nossa rádio web e com a nossa comunidade. Que o Senhor te abençoe e te guarde na Sua perfeita paz.
""".strip()

async def gerar_audio():
    nome_arquivo = "devocional_01_quando_as_palavras_acabam.mp3"
    caminho_arquivo = OUTPUT_DIR / nome_arquivo

    print(f"🎙️ Gerando áudio com Voz Neural (pt-BR-AntonioNeural)...")
    print(f"Arquivo de saída: {caminho_arquivo}")

    # pt-BR-AntonioNeural com ritmo pausado (-6%) e tom ligeiramente aquecido (-2Hz) para tom devocional
    communicate = edge_tts.Communicate(
        text=TEXTO_DEVOCIONAL,
        voice="pt-BR-AntonioNeural",
        rate="-6%",
        pitch="-2Hz"
    )
    await communicate.save(str(caminho_arquivo))
    print(f"✅ Áudio devocional gerado com sucesso!")

    # Cadastrar no SQLite na tabela musicas_louvores (para tocar na Rádio Web)
    conn = get_connection()
    cursor = conn.cursor()
    tamanho_mb = round(caminho_arquivo.stat().st_size / (1024 * 1024), 2)

    cursor.execute("""
    INSERT INTO musicas_louvores (
        titulo, artista, arquivo_nome, caminho_completo, tamanho_mb, categoria, tags, favorito
    ) VALUES (?, ?, ?, ?, ?, 'Pregação & Devocional', 'devocional,oracao,silencio,graca', 1)
    ON CONFLICT(arquivo_nome) DO UPDATE SET
        titulo = excluded.titulo,
        categoria = excluded.categoria
    """, (
        "Devocional #01 // Quando as Palavras Acabam",
        "Comunidade Metanoia // Matheus Barbosa",
        nome_arquivo,
        str(caminho_arquivo),
        tamanho_mb
    ))
    conn.commit()
    conn.close()

    print(f"📻 Devocional cadastrado no acervo da Rádio Web (SQLite) com sucesso! ({tamanho_mb} MB)")
    return caminho_arquivo

if __name__ == "__main__":
    asyncio.run(gerar_audio())
