"""Robô de Transcrição Automática via Deepgram // Ministério Metanoia.
Transcreve em lote os áudios baixados das aulas (MP3, M4A, OGG, WAV) com o modelo Nova-2 em Português (pt-BR),
salva as transcrições em Markdown e indexa no banco SQLite para pesquisa ministerial rápida.
"""
import os
import sys
import json
import httpx
from pathlib import Path
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.db.database import get_connection, init_db

# Diretório padrão para salvar as transcrições
TRANSCRICOES_DIR = BASE_DIR / "data" / "transcricoes"
TRANSCRICOES_DIR.mkdir(parents=True, exist_ok=True)

# URL da API Deepgram
DEEPGRAM_URL = "https://api.deepgram.com/v1/listen?model=nova-2&language=pt-BR&smart_format=true&punctuate=true&paragraphs=true"

def transcrever_arquivo(audio_path: Path, api_key: str) -> Optional[dict]:
    """Envia um arquivo de áudio para o Deepgram Nova-2 e retorna a transcrição."""
    if not audio_path.exists():
        print(f"[ERRO] Arquivo não encontrado: {audio_path}")
        return None

    headers = {
        "Authorization": f"Token {api_key.strip()}",
        "Content-Type": "application/octet-stream"
    }

    print(f"\n[ENVIANDO] Transcrevendo: {audio_path.name}...")
    try:
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()

        with httpx.Client(timeout=300.0) as client:
            response = client.post(DEEPGRAM_URL, headers=headers, content=audio_bytes)

        if response.status_code != 200:
            print(f"[FALHA] Status {response.status_code}: {response.text}")
            return None

        data = response.json()
        canal = data.get("results", {}).get("channels", [{}])[0]
        alternativa = canal.get("alternatives", [{}])[0]

        texto_completo = alternativa.get("transcript", "")
        confianca = alternativa.get("confidence", 0.0)
        duracao_seg = data.get("metadata", {}).get("duration", 0)

        # Extrair parágrafos estruturados se disponíveis
        paragraphs_data = alternativa.get("paragraphs", {}).get("paragraphs", [])
        paragrafos_formatados = []
        for p in paragraphs_data:
            sentencas = [s.get("text", "") for s in p.get("sentences", [])]
            if sentencas:
                paragrafos_formatados.append(" ".join(sentencas))

        if not paragrafos_formatados and texto_completo:
            paragrafos_formatados = [texto_completo]

        return {
            "nome_arquivo": audio_path.name,
            "titulo": audio_path.stem.replace("_", " ").strip(),
            "texto_completo": texto_completo,
            "paragrafos": paragrafos_formatados,
            "confianca": confianca,
            "duracao_minutos": round(duracao_seg / 60, 2)
        }

    except Exception as exc:
        print(f"[ERRO] Falha na comunicação com o Deepgram: {exc}")
        return None

def salvar_transcricao(resultado: dict):
    """Salva a transcrição em arquivo Markdown e atualiza o SQLite."""
    titulo = resultado["titulo"]
    slug = "".join([c if c.isalnum() or c in " -_" else "_" for c in titulo])
    md_file = TRANSCRICOES_DIR / f"{slug}.md"

    # Montar Markdown formatado
    conteudo_md = f"""# 🎙️ TRANSCRIÇÃO OFICIAL // {titulo}
* **Arquivo de Origem:** `{resultado['nome_arquivo']}`
* **Duração Estimada:** {resultado['duracao_minutos']} minutos
* **Precisão Média do Modelo Nova-2:** {round(resultado['confianca'] * 100, 1)}%

---

### 📖 Transcrição Integral da Aula:

"""
    for p in resultado["paragrafos"]:
        conteudo_md += f"{p}\n\n"

    conteudo_md += f"""
---
*Transcrito automaticamente via Deepgram Nova-2 para o Ministério Metanoia.*
"""

    with open(md_file, "w", encoding="utf-8") as f:
        f.write(conteudo_md)

    print(f"[OK] Transcrição salva em: {md_file.name}")

    # Indexar no Banco de Dados
    try:
        init_db()
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM estudos_aulas WHERE titulo LIKE ?", (f"%{titulo[:30]}%",))
        row = cursor.fetchone()

        if row:
            cursor.execute("""
            UPDATE estudos_aulas 
            SET resumo_conteudo = ?, status_estudo = 'transcrito'
            WHERE id = ?
            """, (conteudo_md, row["id"]))
            print(f"[BANCO] Aula existente atualizada com a nova transcrição!")
        else:
            # Buscar primeira trilha disponível
            cursor.execute("SELECT id FROM trilhas_teologicas LIMIT 1")
            trilha_row = cursor.fetchone()
            trilha_id = trilha_row["id"] if trilha_row else 1

            cursor.execute("""
            INSERT INTO estudos_aulas (trilha_id, titulo, resumo_conteudo, status_estudo)
            VALUES (?, ?, ?, 'transcrito')
            """, (trilha_id, titulo, conteudo_md))
            print(f"[BANCO] Nova aula cadastrada e indexada com sucesso!")

        conn.commit()
        conn.close()
    except Exception as db_err:
        print(f"[AVISO] Não foi possível indexar no banco: {db_err}")

def processar_pasta(pasta_audios: Path, api_key: str):
    """Processa todos os áudios de uma pasta."""
    extensoes = ("*.mp3", "*.m4a", "*.ogg", "*.wav", "*.opus", "*.aac")
    arquivos = []
    for ext in extensoes:
        arquivos.extend(pasta_audios.glob(ext))

    if not arquivos:
        print(f"[INFO] Nenhum arquivo de áudio encontrado em: {pasta_audios}")
        return

    print(f"\n=======================================================")
    print(f"  MINISTÉRIO METANOIA // PROCESSADOR DE TRANSCRIÇÃO")
    print(f"  Total de áudios encontrados: {len(arquivos)}")
    print(f"=======================================================\n")

    for i, arq in enumerate(arquivos, 1):
        print(f"[{i}/{len(arquivos)}] Processando: {arq.name}")
        resultado = transcrever_arquivo(arq, api_key)
        if resultado and resultado["texto_completo"]:
            salvar_transcricao(resultado)
        else:
            print(f"[PULADO] Áudio sem transcrição retornada.")

    print("\n[SUCESSO] Processamento do lote finalizado com êxito!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Transcritor de Áudios Teológicos via Deepgram")
    parser.add_argument("caminho", nargs="?", default="", help="Caminho da pasta ou arquivo de áudio")
    parser.add_argument("--key", default="", help="Chave de API do Deepgram")
    args = parser.parse_args()

    api_key = args.key or os.environ.get("DEEPGRAM_API_KEY", "")
    
    if not api_key:
        api_key = input("Informe sua DEEPGRAM_API_KEY: ").strip()

    if not api_key:
        print("[ERRO] É necessário fornecer uma API Key do Deepgram.")
        sys.exit(1)

    caminho = Path(args.caminho) if args.caminho else (BASE_DIR / "data" / "audios_aulas")
    caminho.mkdir(parents=True, exist_ok=True)

    if caminho.is_file():
        res = transcrever_arquivo(caminho, api_key)
        if res:
            salvar_transcricao(res)
    elif caminho.is_dir():
        processar_pasta(caminho, api_key)
