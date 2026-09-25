"""Robô de Testes Automatizados End-to-End // Ministério Metanoia.
Executa uma bateria exaustiva de testes simulando o comportamento de:
1. Usuário Final / Discípulo / Pessoa em Crise (Acolhimento, Oração, Célula, Louvores)
2. Matheus / Liderança ADM (Gestão Pastoral, Planejamento de Vídeos, Trilhas Teológicas, Cortes)
3. Infraestrutura & Banco SQLite (Schema, Integridade, Endpoints REST, Web Flet, Landing Page)
"""
import os
import sys
import time
import json
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from fastapi.testclient import TestClient
from app.main import app
from app.db.database import get_connection, init_db

class TesteResultado:
    def __init__(self, categoria: str, nome: str):
        self.categoria = categoria
        self.nome = nome
        self.passou = False
        self.detalhes = ""
        self.duracao_ms = 0.0

class RoboTestesMetanoia:
    def __init__(self):
        self.client = TestClient(app)
        self.resultados = []
        self.inicio_tempo = None

    def registrar(self, categoria: str, nome: str, condicao: bool, detalhes: str = "", duracao_ms: float = 0.0):
        t = TesteResultado(categoria, nome)
        t.passou = bool(condicao)
        t.detalhes = detalhes
        t.duracao_ms = round(duracao_ms, 2)
        self.resultados.append(t)
        
        status_ico = "[PASS]" if t.passou else "[FAIL]"
        print(f" {status_ico} [{categoria}] {nome} ({t.duracao_ms}ms)")
        if not t.passou and detalhes:
            print(f"       -> Erro: {detalhes}")

    # =========================================================================
    # BATERIA 1: BANCO DE DADOS & INTEGRIDADE ESTRUTURAL
    # =========================================================================
    def testar_banco_dados(self):
        print("\n=== [BATERIA 1] BANCO DE DADOS SQLITE & INTEGRIDADE ESTRUTURAL ===")
        t0 = time.time()
        try:
            init_db()
            conn = get_connection()
            cursor = conn.cursor()

            # 1.1 Verificar tabelas essenciais
            tabelas_esperadas = [
                "membros", "trilhas_teologicas", "estudos_aulas", 
                "cortes_videos", "devocionais_90d", "pedidos_oracao", 
                "encontros_celula", "musicas_louvores"
            ]
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tabelas_existentes = [row[0] for row in cursor.fetchall()]
            
            todas_existem = all(tab in tabelas_existentes for tab in tabelas_esperadas)
            self.registrar("Banco de Dados", "Tabelas Essenciais Criadas", todas_existem, 
                           f"Esperadas: {tabelas_esperadas}. Encontradas: {tabelas_existentes}", (time.time()-t0)*1000)

            # 1.2 Verificar Trilhas Teológicas Cadastradas
            t0 = time.time()
            cursor.execute("SELECT COUNT(*) as total FROM trilhas_teologicas")
            total_trilhas = cursor.fetchone()["total"]
            self.registrar("Banco de Dados", "Trilhas Teológicas Pré-Cadastradas", total_trilhas >= 5,
                           f"Total de trilhas: {total_trilhas} (esperado >= 5)", (time.time()-t0)*1000)

            # 1.3 Verificar Integridade e Resumos de Estudos Gerados
            t0 = time.time()
            resumos_dir = BASE_DIR / "data" / "resumos_estudos"
            total_resumos = len(list(resumos_dir.glob("*.md"))) if resumos_dir.exists() else 0
            self.registrar("Banco de Dados", "Acervo de Apostilas & Resumos Markdown", total_resumos >= 10,
                           f"Total de resumos em data/resumos_estudos/: {total_resumos}", (time.time()-t0)*1000)

            conn.close()
        except Exception as e:
            self.registrar("Banco de Dados", "Conexão e Integridade SQLite", False, str(e))

    # =========================================================================
    # BATERIA 2: JORNADA DO DISCÍPULO / PESSOA EM CRISE (USUÁRIO FINAL)
    # =========================================================================
    def testar_jornada_usuario_final(self):
        print("\n=== [BATERIA 2] JORNADA DO DISCÍPULO & USUÁRIO FINAL (ACOLHIMENTO) ===")
        
        # 2.1 Acessar a Landing Page de Acolhimento
        t0 = time.time()
        res = self.client.get("/")
        html = res.text
        elementos_acolhimento = [
            "Ministério Metanoia",
            "Isaías 42:3",
            "188", # CVV
            "Célula Digital",
            "Mural de Oração",
            "secao-louvores"
        ]
        conteudo_ok = res.status_code == 200 and all(el in html for el in elementos_acolhimento)
        self.registrar("Usuário Final", "Acesso à Landing Page & Elementos Emocionais", conteudo_ok,
                       f"Status: {res.status_code}. Contém todos os blocos acolhedores.", (time.time()-t0)*1000)

        # 2.2 Cenário: Ana Clara (23 anos), crise de ansiedade na madrugada, enviando desabafo
        t0 = time.time()
        payload_oracao = {
            "nome_solicitante": "Ana Clara",
            "motivo": "Estou com uma crise de ansiedade muito forte e falta de ar. Não consigo orar, só chorar. Preciso de um abraço de Deus.",
            "categoria": "ansiedade_depressao",
            "anonimo": False
        }
        res_oracao = self.client.post("/api/v1/oracao/pedir", json=payload_oracao)
        pedido_id = res_oracao.json().get("id") if res_oracao.status_code == 200 else None
        self.registrar("Usuário Final", "Envio de Pedido de Oração / Desabafo de Ansiedade", 
                       res_oracao.status_code == 200 and pedido_id is not None,
                       f"ID retornado: {pedido_id}, Status: {res_oracao.status_code}", (time.time()-t0)*1000)

        # 2.3 Cenário: Usuário anônimo com pensamentos de desespero
        t0 = time.time()
        payload_anonimo = {
            "nome_solicitante": "Anônimo",
            "motivo": "Perdi meu emprego essa semana e o desespero bateu à porta. Peço oração por uma porta aberta e paz na mente.",
            "categoria": "desemprego_familia",
            "anonimo": True
        }
        res_anonimo = self.client.post("/api/v1/oracao/pedir", json=payload_anonimo)
        self.registrar("Usuário Final", "Envio de Pedido Anônimo (Desemprego)", 
                       res_anonimo.status_code == 200, f"Status: {res_anonimo.status_code}", (time.time()-t0)*1000)

        # 2.4 Cenário: Outro irmão acessando o Mural e orando pela Ana Clara
        t0 = time.time()
        res_mural = self.client.get("/api/v1/oracao/mural")
        mural_lista = res_mural.json() if res_mural.status_code == 200 else []
        achou_ana = any(p.get("nome_solicitante") == "Ana Clara" for p in mural_lista)
        self.registrar("Usuário Final", "Mural Público Exibe Pedidos Ativos", 
                       res_mural.status_code == 200 and achou_ana,
                       f"Total de pedidos no mural: {len(mural_lista)}", (time.time()-t0)*1000)

        if pedido_id:
            t0 = time.time()
            res_interceder = self.client.post(f"/api/v1/oracao/interceder/{pedido_id}")
            interceder_ok = res_interceder.status_code == 200 and "sucesso" in res_interceder.text
            self.registrar("Usuário Final", "Ação de Intercessão Comunitária ('Orar por este irmão')",
                           interceder_ok, f"Resposta: {res_interceder.text}", (time.time()-t0)*1000)

        # 2.5 Cenário: Usuário buscando refúgio na Célula Digital (Horário e Link do Meet)
        t0 = time.time()
        res_celula = self.client.get("/api/v1/celula/proximo")
        # Pode retornar 200 com encontro ou 404 se não houver agendamento
        celula_ok = res_celula.status_code in [200, 404]
        self.registrar("Usuário Final", "Consulta ao Próximo Encontro da Célula Digital", 
                       celula_ok, f"Status: {res_celula.status_code}", (time.time()-t0)*1000)

        # 2.6 Cenário: Usuário ouvindo Louvor para Acalmar a Tempestade Interior
        t0 = time.time()
        res_musicas = self.client.get("/api/v1/musicas/")
        musicas_data = res_musicas.json() if res_musicas.status_code == 200 else {}
        total_faixas = musicas_data.get("total", 0)
        faixas = musicas_data.get("faixas", [])
        self.registrar("Usuário Final", "Listagem do Acervo de Louvores & Adoração", 
                       res_musicas.status_code == 200 and total_faixas > 0,
                       f"Total de faixas disponíveis: {total_faixas}", (time.time()-t0)*1000)

        # 2.7 Filtro por Categoria e Busca
        t0 = time.time()
        res_filtro = self.client.get("/api/v1/musicas/?categoria=Guerra Espiritual & Fé")
        self.registrar("Usuário Final", "Filtro Musical por Categoria (Guerra & Fé)", 
                       res_filtro.status_code == 200, f"Faixas filtradas: {res_filtro.json().get('total', 0)}", (time.time()-t0)*1000)

        # 2.8 Favoritar e Reproduzir Faixa
        if faixas:
            primeira_faixa_id = faixas[0]["id"]
            t0 = time.time()
            res_fav = self.client.post(f"/api/v1/musicas/{primeira_faixa_id}/favorito")
            self.registrar("Usuário Final", "Favoritar Faixa no Player", 
                           res_fav.status_code == 200, f"Favorito: {res_fav.json().get('favorito')}", (time.time()-t0)*1000)

            t0 = time.time()
            res_play = self.client.post(f"/api/v1/musicas/{primeira_faixa_id}/play")
            self.registrar("Usuário Final", "Registrar Reprodução de Louvor", 
                           res_play.status_code == 200, f"Resposta: {res_play.json()}", (time.time()-t0)*1000)

    # =========================================================================
    # BATERIA 3: JORNADA DA LIDERANÇA / ADM (MATHEUS NO PAINEL)
    # =========================================================================
    def testar_jornada_lideranca(self):
        print("\n=== [BATERIA 3] JORNADA DA LIDERANÇA & ADM (GESTÃO MINISTERIAL) ===")

        # 3.1 Consultar Trilhas Teológicas da Academia
        t0 = time.time()
        res_trilhas = self.client.get("/api/v1/estudos/trilhas")
        trilhas = res_trilhas.json() if res_trilhas.status_code == 200 else []
        self.registrar("Liderança ADM", "Consulta às 5 Trilhas da Escola Teológica", 
                       res_trilhas.status_code == 200 and len(trilhas) >= 5,
                       f"Trilhas mapeadas: {len(trilhas)}", (time.time()-t0)*1000)

        # 3.2 Planejar Gravação de um Novo Vídeo Longo no YouTube
        t0 = time.time()
        trilha_id = trilhas[0]["id"] if trilhas else 1
        payload_aula = {
            "trilha_id": trilha_id,
            "codigo_aula": "MET-YOUTUBE-01",
            "titulo": "A Bíblia é Confiável? Como Ela Chegou até Nós",
            "texto_biblico": "2 Timóteo 3:16-17",
            "resumo_conteudo": "Aula expositiva completa sobre manuscritologia bíblica, inspiração divina e cânon do Antigo e Novo Testamento.",
            "video_youtube_url": "https://youtube.com/@metanoia",
            "status_estudo": "planejado"
        }
        res_aula = self.client.post("/api/v1/estudos/aulas", json=payload_aula)
        aula_id = res_aula.json().get("id") if res_aula.status_code == 200 else None
        self.registrar("Liderança ADM", "Cadastrar Estudo / Vídeo Planejado para YouTube", 
                       res_aula.status_code == 200 and aula_id is not None,
                       f"Aula ID criada: {aula_id}", (time.time()-t0)*1000)

        # 3.3 Mapear Corte de Ouro da Aula Longa para Shorts / Reels / TikTok
        if aula_id:
            t0 = time.time()
            payload_corte = {
                "aula_id": aula_id,
                "titulo_corte": "Por que a Bíblia tem 66 livros e não 73?",
                "hook": "Você sabe por que a Bíblia protestante tem 7 livros a menos que a católica?",
                "timestamp_inicio": "12:40",
                "timestamp_fim": "13:35",
                "status": "a_editar"
            }
            res_corte = self.client.post("/api/v1/estudos/cortes", json=payload_corte)
            self.registrar("Liderança ADM", "Mapear Corte de Ouro para Redes Sociais", 
                           res_corte.status_code == 200, f"Corte ID: {res_corte.json().get('id')}", (time.time()-t0)*1000)

        # 3.4 Agendar Encontro da Célula Digital pelo Painel do Líder
        t0 = time.time()
        payload_encontro = {
            "tema": "Elias na Caverna: Quando o Profeta Deseja a Morte",
            "data_hora": "Toda Quinta-feira às 20h00",
            "link_sala": "https://meet.google.com/xyz-metanoia",
            "material_apoio": "1 Reis 19 e as 4 curas de Deus para o esgotamento emocional."
        }
        res_agendamento = self.client.post("/api/v1/celula/encontros", json=payload_encontro)
        self.registrar("Liderança ADM", "Agendamento de Encontro da Célula Digital", 
                       res_agendamento.status_code == 200, f"Encontro ID: {res_agendamento.json().get('id')}", (time.time()-t0)*1000)

        # 3.5 Verificar se o Próximo Encontro foi Atualizado Automaticamente
        t0 = time.time()
        res_prox = self.client.get("/api/v1/celula/proximo")
        tema_ok = res_prox.status_code == 200 and "Elias" in res_prox.json().get("tema", "")
        self.registrar("Liderança ADM", "Próximo Encontro Refletido na Célula Digital", 
                       tema_ok, f"Tema retornado: {res_prox.json().get('tema')}", (time.time()-t0)*1000)

        # 3.6 Consultar Métricas do Acervo de Músicas
        t0 = time.time()
        res_stats = self.client.get("/api/v1/musicas/stats")
        self.registrar("Liderança ADM", "Painel de Métricas do Acervo Musical", 
                       res_stats.status_code == 200, f"Métricas: {res_stats.json()}", (time.time()-t0)*1000)

    # =========================================================================
    # BATERIA 4: PLATAFORMA FLET WEB & ESTRUTURA VISUAL
    # =========================================================================
    def testar_plataforma_flet_e_ui(self):
        print("\n=== [BATERIA 4] PLATAFORMA FLET & ESTRUTURA VISUAL ===")

        # 4.1 Testar se a rota /plataforma responde
        t0 = time.time()
        res_flet = self.client.get("/plataforma")
        # Flet pode redirecionar para /plataforma/ ou retornar 200
        flet_ok = res_flet.status_code in [200, 307, 308]
        self.registrar("Plataforma Flet", "Endpoint Flet ASGI Web (/plataforma)", 
                       flet_ok, f"Status code retornado: {res_flet.status_code}", (time.time()-t0)*1000)

        # 4.2 Testar se a documentação Swagger OpenAPI está ativa
        t0 = time.time()
        res_docs = self.client.get("/docs")
        self.registrar("Documentação API", "Swagger UI Ativo (/docs)", 
                       res_docs.status_code == 200 and "Swagger UI" in res_docs.text,
                       f"Status: {res_docs.status_code}", (time.time()-t0)*1000)

        # 4.3 Testar Integridade do Arquivo Desktop/Flet Nativo
        t0 = time.time()
        flet_script = BASE_DIR / "app" / "flet_app.py"
        self.registrar("Plataforma Desktop", "Script Nativo app/flet_app.py Presente", 
                       flet_script.exists() and flet_script.stat().st_size > 10000,
                       f"Tamanho do arquivo: {flet_script.stat().st_size} bytes", (time.time()-t0)*1000)

        # 4.4 Testar Entrada Mobile main.py
        t0 = time.time()
        main_entry = BASE_DIR / "main.py"
        self.registrar("Mobile APK/AAB", "Ponto de Entrada Nativo main.py Presente", 
                       main_entry.exists(), f"Localizado em: {main_entry}", (time.time()-t0)*1000)

    # =========================================================================
    # BATERIA 5: PIPELINES DE IA & AUTOMAÇÃO (DEEPGRAM & TELEGRAM)
    # =========================================================================
    def testar_pipelines_ia(self):
        print("\n=== [BATERIA 5] PIPELINES DE IA & TRANSCRIÇÃO (DEEPGRAM) ===")
        
        t0 = time.time()
        script_transcritor = BASE_DIR / "scripts" / "transcritor_deepgram.py"
        transcritor_ok = script_transcritor.exists()
        self.registrar("Automação IA", "Script Deepgram Nova-2 (transcritor_deepgram.py)", 
                       transcritor_ok, f"Localizado em: {script_transcritor}", (time.time()-t0)*1000)

        t0 = time.time()
        bat_transcritor = BASE_DIR / "3_TRANSCREVER_AUDIOS_DEEPGRAM.bat"
        self.registrar("Automação IA", "Atalho Executável .bat Deepgram Presente", 
                       bat_transcritor.exists(), f"Localizado em: {bat_transcritor}", (time.time()-t0)*1000)

    # =========================================================================
    # GERAÇÃO DO RELATÓRIO CONSOLIDADO
    # =========================================================================
    def gerar_relatorio(self):
        total = len(self.resultados)
        passaram = sum(1 for r in self.resultados if r.passou)
        falharam = total - passaram
        duracao_total = round(time.time() - self.inicio_tempo, 2)
        taxa_sucesso = round((passaram / total) * 100, 1) if total > 0 else 0

        print("\n" + "="*65)
        print(f"      RELATÓRIO OFICIAL DE AUDITORIA // MINISTÉRIO METANOIA")
        print("="*65)
        print(f"  Total de Testes Executados:  {total}")
        print(f"  Testes com Sucesso:          {passaram}  [OK]")
        print(f"  Testes com Falha:            {falharam}  {'[ATENÇÃO]' if falharam > 0 else ''}")
        print(f"  Taxa de Conformidade:        {taxa_sucesso}%")
        print(f"  Tempo Total de Execução:     {duracao_total}s")
        print("="*65)

        # Salvar JSON estruturado
        relatorio_dir = BASE_DIR / "data" / "relatorios_testes"
        relatorio_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_file = relatorio_dir / f"relatorio_auditoria_{timestamp}.json"
        
        dados_json = {
            "timestamp": datetime.now().isoformat(),
            "total_testes": total,
            "passaram": passaram,
            "falharam": falharam,
            "taxa_sucesso": taxa_sucesso,
            "duracao_segundos": duracao_total,
            "testes": [
                {
                    "categoria": r.categoria,
                    "nome": r.nome,
                    "passou": r.passou,
                    "detalhes": r.detalhes,
                    "duracao_ms": r.duracao_ms
                }
                for r in self.resultados
            ]
        }

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(dados_json, f, indent=2, ensure_ascii=False)

        # Salvar Markdown Executivo
        md_file = BASE_DIR / "data" / "RELATORIO_AUDITORIA_TESTES.md"
        conteudo_md = f"""# 🛡️ RELATÓRIO OFICIAL DE AUDITORIA & TESTES E2E
> **Ministério Metanoia // Plataforma Pastoral, Escola Teológica & Landing Page**  
> **Data da Auditoria:** {datetime.now().strftime("%d/%m/%Y às %H:%M:%S")}  
> **Taxa de Sucesso:** {taxa_sucesso}% ({passaram}/{total} testes aprovados)  
> **Tempo de Execução:** {duracao_total} segundos  

---

### 📊 Resumo Executivo por Bateria

| Bateria / Domínio | Testes Avaliados | Status |
| :--- | :---: | :---: |
| **1. Banco de Dados SQLite & Schema** | 3 testes | {'✅ 100% OK' if all(r.passou for r in self.resultados if r.categoria == 'Banco de Dados') else '⚠️ Revisar'} |
| **2. Jornada do Discípulo (Acolhimento & Oração)** | 8 testes | {'✅ 100% OK' if all(r.passou for r in self.resultados if r.categoria == 'Usuário Final') else '⚠️ Revisar'} |
| **3. Jornada da Liderança (Vídeos & Trilhas)** | 6 testes | {'✅ 100% OK' if all(r.passou for r in self.resultados if r.categoria == 'Liderança ADM') else '⚠️ Revisar'} |
| **4. Plataforma Flet Web, UI & Mobile** | 4 testes | {'✅ 100% OK' if all(r.passou for r in self.resultados if 'Plataforma' in r.categoria or 'Mobile' in r.categoria or 'API' in r.categoria) else '⚠️ Revisar'} |
| **5. Automações de IA & Deepgram** | 2 testes | {'✅ 100% OK' if all(r.passou for r in self.resultados if r.categoria == 'Automação IA') else '⚠️ Revisar'} |

---

### 🔍 Detalhamento dos Testes Executados

"""
        for r in self.resultados:
            ico = "✅" if r.passou else "❌"
            conteudo_md += f"- {ico} **[{r.categoria}]** {r.nome} — *{r.duracao_ms}ms*\n"
            if r.detalhes:
                conteudo_md += f"  > *Detalhes:* `{r.detalhes}`\n"

        conteudo_md += f"""
---
*Auditoria gerada automaticamente pelo Robô de Testes do Ministério Metanoia.*
"""
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(conteudo_md)

        print(f"\n[ARQUIVOS GERADOS]")
        print(f" -> Relatório Detalhado JSON:     {json_file.name}")
        print(f" -> Relatório Executivo Markdown: data/RELATORIO_AUDITORIA_TESTES.md")
        return falharam == 0

    def executar_tudo(self):
        self.inicio_tempo = time.time()
        print("===================================================================")
        print("   MINISTÉRIO METANOIA // INICIANDO BATERIA COMPLETA DE TESTES")
        print("===================================================================")
        self.testar_banco_dados()
        self.testar_jornada_usuario_final()
        self.testar_jornada_lideranca()
        self.testar_plataforma_flet_e_ui()
        self.testar_pipelines_ia()
        return self.gerar_relatorio()

if __name__ == "__main__":
    robo = RoboTestesMetanoia()
    sucesso = robo.executar_tudo()
    sys.exit(0 if sucesso else 1)
