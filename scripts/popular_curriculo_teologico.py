"""Script para escanear a pasta 'ACADEMIA DE PREGADORES' e popular o banco SQLite."""
import os
import sys
from pathlib import Path

# Garantir importação do módulo app raiz
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.db.database import get_connection, init_db

ACADEMIA_PATH = Path(r"C:\Users\matheus\Desktop\ACADEMIA DE PREGADORES")

def popular_catalogo():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()

    if not ACADEMIA_PATH.exists():
        print(f"Diretório não encontrado: {ACADEMIA_PATH}")
        return

    # Escanear e cadastrar as Trilhas
    trilhas = [
        ("Básico", "BÁSICO EM TEOLOGIA", 188, "Visão panorâmica de toda a Bíblia, Bibliologia, Pentateuco, Profetas e Evangelhos."),
        ("Médio", "MÉDIO EM TEOLOGIA", 236, "Aprofundamento sistemático, Hermenêutica, Exegese, Cristologia e Homilética."),
        ("Bacharel", "BACHAREL EM TEOLOGIA", 209, "Nível acadêmico superior com Grego, Hebraico, Teologia Bíblica e Liderança."),
        ("Especialização", "ESPECIALIZAÇÃO EM ESCATOLOGIA", 164, "Doutrina das Últimas Coisas, Profecias de Daniel e Apocalipse."),
        ("Especialização", "ONOMATOLOGIA BÍBLICA", 35, "Estudo dos Nomes Bíblicos, Teofanias e Nomes de Deus no hebraico e aramaico.")
    ]

    for nivel, materia, aulas, desc in trilhas:
        cursor.execute("SELECT id FROM trilhas_teologicas WHERE materia = ?", (materia,))
        row = cursor.fetchone()
        if not row:
            cursor.execute("""
            INSERT INTO trilhas_teologicas (nivel, materia, total_aulas, descricao)
            VALUES (?, ?, ?, ?)
            """, (nivel, materia, aulas, desc))
            print(f"[OK] Trilha cadastrada: {materia}")

    conn.commit()

    # Mapear os PDFs de apostilas encontrados no Básico
    basico_dir = ACADEMIA_PATH / "ACADEMIA DE PREGADORES" / "BÁSICO EM TEOLOGIA"
    if basico_dir.exists():
        cursor.execute("SELECT id FROM trilhas_teologicas WHERE materia = 'BÁSICO EM TEOLOGIA'")
        trilha_basico = cursor.fetchone()["id"]

        for item in basico_dir.glob("*.pdf"):
            nome_limpo = item.stem.replace("_Apostila_Modulo_", "").replace("_", " ").strip()
            cursor.execute("SELECT id FROM estudos_aulas WHERE titulo = ?", (nome_limpo,))
            if not cursor.fetchone():
                cursor.execute("""
                INSERT INTO estudos_aulas (trilha_id, titulo, resumo_conteudo, status_estudo)
                VALUES (?, ?, ?, 'a_estudar')
                """, (trilha_basico, nome_limpo, f"Apostila oficial localizada em: {item.name}"))
                print(f"[OK] Aula planejada adicionada: {nome_limpo}")

    conn.commit()
    conn.close()
    print("Catalogação teológica concluída com sucesso no banco de dados!")

if __name__ == "__main__":
    popular_catalogo()
