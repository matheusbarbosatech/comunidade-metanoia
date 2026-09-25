"""Robô de Estudos Teológicos // Ministério Metanoia.
Lê as apostilas em PDF da Academia de Pregadores, extrai sumários e pontos-chave,
e gera resumos didáticos para estudos e pregações salvos no SQLite.
"""
import sys
import re
from pathlib import Path

# Ajustar sys.path para importar o app
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import pymupdf
from app.db.database import get_connection

ACADEMIA_DIR = Path(r"C:\Users\matheus\Desktop\ACADEMIA DE PREGADORES\ACADEMIA DE PREGADORES\BÁSICO EM TEOLOGIA")
RESUMOS_DIR = BASE_DIR / "data" / "resumos_estudos"
RESUMOS_DIR.mkdir(parents=True, exist_ok=True)

def extrair_resumo_pdf(pdf_path: Path) -> dict:
    """Extrai sumário e conceitos fundamentais do PDF."""
    doc = pymupdf.open(pdf_path)
    total_paginas = len(doc)
    
    # Coletar primeiras 10 páginas para capturar sumário e introdução
    texto_inicial = ""
    for p in range(min(12, total_paginas)):
        texto_inicial += doc[p].get_text() + "\n"
        
    # Identificar capítulos pelo padrão "CAPÍTULO X" ou linhas em caixa alta
    capitulos = []
    for linha in texto_inicial.split("\n"):
        linha_strip = linha.strip()
        if re.match(r"^(CAP[IÍ]TULO\s+\d+|[0-9]+\.\s+[A-ZÁÉÍÓÚÂÊÔÃÕ]+)", linha_strip, re.IGNORECASE):
            if len(linha_strip) < 60 and linha_strip not in capitulos:
                capitulos.append(linha_strip)

    # Identificar versículos bíblicos citados
    versiculos = re.findall(r"([1-3]?\s?[A-Z][a-zçãõáéíóúâêô]+\s+\d+:\d+(?:-\d+)?)", texto_inicial)
    versiculos_unicos = list(dict.fromkeys(versiculos))[:6]

    resumo_md = f"""# 📚 RESUMO EXECUTIVO // {pdf_path.stem.replace('_', ' ').strip()}
**Total de Páginas na Apostila Original:** {total_paginas} páginas.

---

### 📖 Estrutura da Matéria (Sumário Mapeado):
"""
    if capitulos:
        for cap in capitulos:
            resumo_md += f"* **{cap}**\n"
    else:
        resumo_md += "* Módulo introdutório com fundamentos bíblicos e teologia aplicada.\n"

    resumo_md += "\n### 📜 Versículos-Chave Identificados no Texto:\n"
    for v in versiculos_unicos:
        resumo_md += f"* 📖 **{v}**\n"

    resumo_md += f"""
---

### 🎯 Sugestões de Roteiros de Vídeo (Para Gravar no YouTube):
1. **Vídeo 1 (Introdução):** *"O que você precisa saber sobre {pdf_path.stem.split('.')[-1].replace('_', ' ').strip()} antes de abrir a Bíblia."*
2. **Vídeo 2 (Confronto):** *"O maior erro de interpretação cometido nesta matéria."*
3. **Vídeo 3 (Aplicação):** *"Como aplicar essa doutrina na sua vida diária e na sua família."*
"""
    return {
        "titulo": pdf_path.stem.replace("_Apostila_Modulo_", "").replace("_", " ").strip(),
        "resumo_md": resumo_md,
        "capitulos_count": len(capitulos),
        "total_paginas": total_paginas
    }

def processar_todas_apostilas():
    if not ACADEMIA_DIR.exists():
        print(f"Diretório não encontrado: {ACADEMIA_DIR}")
        return

    conn = get_connection()
    cursor = conn.cursor()

    pdfs = list(ACADEMIA_DIR.glob("*.pdf"))
    print(f"Encontradas {len(pdfs)} apostilas em PDF para estudar...")

    for pdf in pdfs:
        try:
            dados = extrair_resumo_pdf(pdf)
            arquivo_saida = RESUMOS_DIR / f"{pdf.stem}.md"
            with open(arquivo_saida, "w", encoding="utf-8") as f:
                f.write(dados["resumo_md"])
            
            # Atualizar no banco de dados SQLite
            cursor.execute("""
            UPDATE estudos_aulas 
            SET resumo_conteudo = ? 
            WHERE titulo LIKE ?
            """, (dados["resumo_md"][:1000], f"%{dados['titulo'][:15]}%"))

            print(f"[OK] Estudada: {dados['titulo']} ({dados['total_paginas']} págs)")
        except Exception as e:
            print(f"[ERRO] Falha ao processar {pdf.name}: {e}")

    conn.commit()
    conn.close()
    print("\n[SUCESSO] Todas as apostilas foram resumidas e salvas em data/resumos_estudos/!")

if __name__ == "__main__":
    processar_todas_apostilas()
