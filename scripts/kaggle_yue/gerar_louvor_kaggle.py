"""Gerenciador e CLI Local para o YuE no Kaggle (Ministério Metanoia).
Permite subir o kernel, monitorar o status e baixar as músicas geradas direto para a Playlist.
"""
import sys
import subprocess
import webbrowser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.core.config import MUSIC_PLAYLIST_DIR
from app.services.music_service import sync_music_playlist

KERNEL_ID = "omatheusbsilva/metanoia-yue-music-generator"
KERNEL_DIR = Path(__file__).resolve().parent
KAGGLE_URL = f"https://www.kaggle.com/code/{KERNEL_ID}"

def print_banner():
    print("=" * 65)
    print("  🎵 METANOIA YUE MUSIC GENERATOR // KAGGLE GPU 100% GRÁTIS")
    print("  Gere músicas completas (Vocais + Trap Gospel) na nuvem")
    print("=" * 65)

def subir_kernel():
    print("\n🚀 [1/2] Enviando Notebook e Metadados para o Kaggle...")
    try:
        resultado = subprocess.run(
            ["kaggle", "kernels", "push", "-p", str(KERNEL_DIR)],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Sucesso!")
        print(resultado.stdout)
        print(f"🔗 Link do Kernel: {KAGGLE_URL}")
        print("\nDICA: Abra o link no Kaggle, clique em 'Edit' ou ligue a GPU (T4/P100) para iniciar a geração!")
    except Exception as e:
        print(f"❌ Erro ao enviar kernel para o Kaggle: {e}")

def verificar_status():
    print(f"\n🔍 Verificando status do kernel {KERNEL_ID}...")
    try:
        resultado = subprocess.run(
            ["kaggle", "kernels", "status", KERNEL_ID],
            capture_output=True,
            text=True,
            check=True
        )
        print(resultado.stdout)
    except Exception as e:
        print(f"❌ Erro ao verificar status: {e}")

def baixar_musicas():
    print(f"\n📥 Baixando arquivos gerados do Kaggle para: {MUSIC_PLAYLIST_DIR}...")
    MUSIC_PLAYLIST_DIR.mkdir(parents=True, exist_ok=True)
    try:
        resultado = subprocess.run(
            ["kaggle", "kernels", "output", KERNEL_ID, "-p", str(MUSIC_PLAYLIST_DIR)],
            capture_output=True,
            text=True,
            check=True
        )
        print(resultado.stdout)
        print("🔄 Sincronizando com o Banco de Dados do Ministério Metanoia...")
        total = sync_music_playlist()
        print(f"✨ Concluído! {total} faixas sincronizadas e disponíveis no site e no app!")
    except Exception as e:
        print(f"❌ Erro ao baixar outputs: {e}")

def abrir_navegador():
    print(f"\n🌐 Abrindo {KAGGLE_URL} no seu navegador...")
    webbrowser.open(KAGGLE_URL)

def menu_principal():
    while True:
        print_banner()
        print("\nEscolha uma opção:")
        print("  1 - Subir/Atualizar Notebook no Kaggle (Push)")
        print("  2 - Verificar Status do Kernel no Kaggle")
        print("  3 - Baixar Músicas do Kaggle direto pra Playlist MATHEUS")
        print("  4 - Abrir Kernel no Navegador (Kaggle)")
        print("  0 - Sair")
        print("-" * 65)

        opcao = input("Digite a opção (0-4): ").strip()
        if opcao == "1":
            subir_kernel()
        elif opcao == "2":
            verificar_status()
        elif opcao == "3":
            baixar_musicas()
        elif opcao == "4":
            abrir_navegador()
        elif opcao == "0":
            print("\n🕊️ Até mais! Que Deus abençoe as suas composições.")
            break
        else:
            print("\n⚠️ Opção inválida. Tente novamente.")
        
        input("\nPressione ENTER para voltar ao menu...")
        print("\n" * 2)

if __name__ == "__main__":
    menu_principal()
