"""Upload dos 50 Louvores para o GitHub Releases CDN // Ministério Metanoia.
Disponibiliza os áudios 24/7 na rede global de alta velocidade da Microsoft/GitHub/Azure,
permitindo reprodução contínua na Landing Page e no App mesmo com o computador desligado.
"""
import os
import sys
import httpx
from pathlib import Path
import urllib.parse

REPO_OWNER = "matheusbarbosatech"
REPO_NAME = "ministerio"
TAG_NAME = "v1.0.0-louvores"
RELEASE_NAME = "Acervo Oficial de Louvores & Adoração // Ministério Metanoia"

ORIGEM_LOCAL = Path(r"C:\Users\matheus\Music\Playlist MATHEUS")
ORIGEM_DRIVE = Path(r"G:\Meu Drive\PLAYLIST_MINISTERIAL_METANOIA")

def obter_pasta_audios() -> Path:
    if ORIGEM_LOCAL.exists() and len(list(ORIGEM_LOCAL.glob("*.mp3"))) > 0:
        return ORIGEM_LOCAL
    if ORIGEM_DRIVE.exists() and len(list(ORIGEM_DRIVE.glob("*.mp3"))) > 0:
        return ORIGEM_DRIVE
    return ORIGEM_LOCAL

def main():
    print("=" * 65)
    print("  MINISTÉRIO METANOIA // UPLOADER DE LOUVORES PARA O GITHUB CDN")
    print("=" * 65)
    print()

    pasta = obter_pasta_audios()
    if not pasta.exists():
        print(f"[ERRO] Pasta de áudios não encontrada: {pasta}")
        sys.exit(1)

    arquivos = list(pasta.glob("*.mp3"))
    print(f"[INFO] Pasta de origem: {pasta}")
    print(f"[INFO] Total de faixas localizadas: {len(arquivos)}")
    print()

    # Obter token do GitHub
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        print("Para enviar os 50 arquivos para o seu repositório oficial no GitHub,")
        print("é necessário um Token do GitHub (com permissão 'repo' ou 'contents:write').")
        print("Crie gratuitamente em: https://github.com/settings/tokens (Tokens classic)")
        print()
        token = input("Cole o seu GitHub Token aqui e aperte Enter: ").strip()

    if not token:
        print("[ERRO] Token do GitHub não fornecido. Operação cancelada.")
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    with httpx.Client(timeout=180.0) as client:
        # 1. Verificar ou Criar a Release
        print(f"\n[1/3] Verificando release '{TAG_NAME}' em {REPO_OWNER}/{REPO_NAME}...")
        url_get_release = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/tags/{TAG_NAME}"
        res = client.get(url_get_release, headers=headers)

        if res.status_code == 200:
            release_data = res.json()
            print(f"[OK] Release existente encontrada! ID: {release_data['id']}")
        else:
            print(f"[CRIANDO] Criando nova Release pública '{TAG_NAME}'...")
            payload_create = {
                "tag_name": TAG_NAME,
                "target_commitish": "main",
                "name": RELEASE_NAME,
                "body": "Acervo oficial de 50 canções e louvores em alta fidelidade para streaming contínuo da Rádio Web Ministério Metanoia.",
                "draft": False,
                "prerelease": False
            }
            res_create = client.post(f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases", headers=headers, json=payload_create)
            if res_create.status_code not in [200, 201]:
                print(f"[ERRO] Falha ao criar release: {res_create.status_code} - {res_create.text}")
                sys.exit(1)
            release_data = res_create.json()
            print(f"[OK] Release criada com sucesso! ID: {release_data['id']}")

        upload_url_template = release_data["upload_url"].split("{")[0]

        # 2. Listar arquivos já enviados para evitar reenvio
        assets_existentes = {a["name"]: a["id"] for a in release_data.get("assets", [])}
        print(f"[INFO] Faixas que já estão na nuvem: {len(assets_existentes)}/{len(arquivos)}")

        # 3. Upload das faixas restantes
        print(f"\n[2/3] Iniciando upload das faixas para a CDN do GitHub/Azure...")
        enviados = 0
        pulados = 0

        for idx, arq in enumerate(arquivos, 1):
            if arq.name in assets_existentes:
                print(f" [{idx}/{len(arquivos)}] Já presente na nuvem: {arq.name}")
                pulados += 1
                continue

            tamanho_mb = round(arq.stat().st_size / (1024 * 1024), 2)
            print(f" [{idx}/{len(arquivos)}] Enviando ({tamanho_mb} MB): {arq.name}...")

            encoded_name = urllib.parse.quote(arq.name)
            upload_url = f"{upload_url_template}?name={encoded_name}"
            upload_headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "audio/mpeg",
                "Accept": "application/vnd.github+json"
            }

            try:
                with open(arq, "rb") as f_audio:
                    file_bytes = f_audio.read()

                res_upload = client.post(upload_url, headers=upload_headers, content=file_bytes)
                if res_upload.status_code in [200, 201]:
                    print(f"        -> [OK] Upload concluído com sucesso!")
                    enviados += 1
                else:
                    print(f"        -> [FALHA] Status {res_upload.status_code}: {res_upload.text[:120]}")
            except Exception as up_err:
                print(f"        -> [ERRO] {up_err}")

        print("\n" + "=" * 65)
        print(f"  RESUMO DA SINCRONIZAÇÃO EM NUVEM:")
        print(f"   - Enviadas nesta execução: {enviados}")
        print(f"   - Já estavam na nuvem:    {pulados}")
        print(f"   - Total disponível:        {enviados + pulados}/{len(arquivos)}")
        print("=" * 65)
        print("\nPronto! Agora qualquer pessoa pode ouvir as músicas 24/7 com o seu PC desligado!")

if __name__ == "__main__":
    main()
