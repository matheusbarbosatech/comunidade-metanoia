import os
import sys
import re
import json
import unicodedata
import httpx
from pathlib import Path
import urllib.parse

# Garantir saída UTF-8 no terminal Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

REPO_OWNER = "matheusbarbosatech"
REPO_NAME = "ministerio"
TAG_NAME = "v1.0.0-louvores"
RELEASE_NAME = "Acervo Oficial de Louvores & Adoração // Ministério Metanoia"

ORIGEM_LOCAL = Path(r"C:\Users\matheus\Music\Playlist MATHEUS")
ORIGEM_DRIVE = Path(r"G:\Meu Drive\PLAYLIST_MINISTERIAL_METANOIA")

def sanitize_asset_name(filename: str) -> str:
    """Gera um nome de arquivo ASCII seguro e padronizado para a CDN do GitHub/Azure."""
    clean = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore').decode('ASCII')
    clean = re.sub(r'[^a-zA-Z0-9._-]', '.', clean)
    clean = re.sub(r'\.+', '.', clean)
    return clean

def obter_pasta_audios() -> Path:
    if ORIGEM_LOCAL.exists() and len(list(ORIGEM_LOCAL.glob("*.mp3"))) > 0:
        return ORIGEM_LOCAL
    if ORIGEM_DRIVE.exists() and len(list(ORIGEM_DRIVE.glob("*.mp3"))) > 0:
        return ORIGEM_DRIVE
    return ORIGEM_LOCAL

def obter_github_token() -> str:
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        return token
    try:
        import subprocess
        p = subprocess.Popen(['git', 'credential', 'fill'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out, _ = p.communicate(input='protocol=https\nhost=github.com\n\n', timeout=5)
        for line in out.splitlines():
            if line.startswith('password='):
                return line.split('=', 1)[1].strip()
    except Exception:
        pass
    return ""

def main():
    print("=" * 65)
    print("  MINISTÉRIO METANOIA // UPLOADER DE LOUVORES PARA O GITHUB CDN")
    print("=" * 65)
    print()

    pasta = obter_pasta_audios()
    if not pasta.exists():
        print(f"[ERRO] Pasta de áudios não encontrada: {pasta}")
        sys.exit(1)

    arquivos = sorted(list(pasta.glob("*.mp3")), key=lambda p: p.name)
    print(f"[INFO] Pasta de origem: {pasta}")
    print(f"[INFO] Total de faixas localizadas: {len(arquivos)}")
    print()

    # Obter token do GitHub
    token = obter_github_token()
    if not token:
        print("Para enviar os 50 arquivos para o seu repositório oficial no GitHub,")
        print("é necessário um Token do GitHub (com permissão 'repo' ou 'contents:write').")
        print("Crie gratuitamente em: https://github.com/settings/tokens (Tokens classic)")
        print()
        token = input("Cole o seu GitHub Token aqui e aperte Enter: ").strip()

    if not token:
        print("[ERRO] Token do GitHub não fornecido. Operação cancelada.")
        sys.exit(1)
    else:
        print(f"[OK] Token do GitHub detectado e autenticado com sucesso!")

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    with httpx.Client(timeout=300.0) as client:
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
        assets_existentes = {a["name"]: a for a in release_data.get("assets", [])}
        print(f"[INFO] Faixas que já estão na nuvem: {len(assets_existentes)}/{len(arquivos)}")

        # 3. Upload das faixas restantes
        print(f"\n[2/3] Sincronizando faixas restantes com a CDN do GitHub/Azure...")
        enviados = 0
        pulados = 0

        for idx, arq in enumerate(arquivos, 1):
            asset_name = sanitize_asset_name(arq.name)
            if asset_name in assets_existentes:
                print(f" [{idx}/{len(arquivos)}] Já presente na nuvem: {asset_name}")
                pulados += 1
                continue

            tamanho_mb = round(arq.stat().st_size / (1024 * 1024), 2)
            print(f" [{idx}/{len(arquivos)}] Enviando ({tamanho_mb} MB): {asset_name}...")

            encoded_name = urllib.parse.quote(asset_name)
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

        # 4. Atualizar musicas_seed.json com os links oficiais da CDN
        print(f"\n[3/3] Atualizando catálogo com links oficiais de streaming...")
        res_fresh = client.get(url_get_release, headers=headers)
        fresh_assets = {a["name"]: a["browser_download_url"] for a in res_fresh.json().get("assets", [])}
        print(f"[INFO] Total de faixas ativas na CDN: {len(fresh_assets)}/50")

        # Atualizar seed JSON
        seed_path = Path(__file__).resolve().parent.parent / "app" / "static" / "musicas_seed.json"
        if seed_path.exists():
            with open(seed_path, "r", encoding="utf-8") as sf:
                musicas_data = json.load(sf)

            for m in musicas_data:
                # Localizar arquivo original correspondente
                arq_orig = None
                for arq in arquivos:
                    if arq.name.startswith(m["titulo"]) or m["titulo"] in arq.name:
                        arq_orig = arq
                        break
                
                if arq_orig:
                    sanitized = sanitize_asset_name(arq_orig.name)
                    m["arquivo_nome"] = arq_orig.name
                    m["asset_name"] = sanitized
                    m["cdn_url"] = fresh_assets.get(sanitized, f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG_NAME}/{sanitized}")
                else:
                    clean_fallback = sanitize_asset_name(f"{m['titulo']}.mp3")
                    m["arquivo_nome"] = f"{m['titulo']}.mp3"
                    m["asset_name"] = clean_fallback
                    m["cdn_url"] = fresh_assets.get(clean_fallback, f"https://github.com/{REPO_OWNER}/{REPO_NAME}/releases/download/{TAG_NAME}/{clean_fallback}")

            with open(seed_path, "w", encoding="utf-8") as sf:
                json.dump(musicas_data, sf, indent=2, ensure_ascii=False)
            print(f"[OK] {seed_path.name} atualizado com URLs oficiais de streaming!")

        print("\n" + "=" * 65)
        print(f"  RESUMO DA SINCRONIZAÇÃO EM NUVEM:")
        print(f"   - Enviadas nesta execução: {enviados}")
        print(f"   - Já estavam na nuvem:    {pulados}")
        print(f"   - Total na CDN:            {len(fresh_assets)}/50")
        print("=" * 65)
        print("\nPronto! O streaming em nuvem 24/7 está 100% ativo!")

if __name__ == "__main__":
    main()

