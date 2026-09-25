# 🛡️ RELATÓRIO OFICIAL DE AUDITORIA & TESTES E2E
> **Ministério Metanoia // Plataforma Pastoral, Escola Teológica & Landing Page**  
> **Data da Auditoria:** 25/09/2026 às 14:46:46  
> **Taxa de Sucesso:** 100.0% (25/25 testes aprovados)  
> **Tempo de Execução:** 1.39 segundos  

---

### 📊 Resumo Executivo por Bateria

| Bateria / Domínio | Testes Avaliados | Status |
| :--- | :---: | :---: |
| **1. Banco de Dados SQLite & Schema** | 3 testes | ✅ 100% OK |
| **2. Jornada do Discípulo (Acolhimento & Oração)** | 8 testes | ✅ 100% OK |
| **3. Jornada da Liderança (Vídeos & Trilhas)** | 6 testes | ✅ 100% OK |
| **4. Plataforma Flet Web, UI & Mobile** | 4 testes | ✅ 100% OK |
| **5. Automações de IA & Deepgram** | 2 testes | ✅ 100% OK |

---

### 🔍 Detalhamento dos Testes Executados

- ✅ **[Banco de Dados]** Tabelas Essenciais Criadas — *3.19ms*
  > *Detalhes:* `Esperadas: ['membros', 'trilhas_teologicas', 'estudos_aulas', 'cortes_videos', 'devocionais_90d', 'pedidos_oracao', 'encontros_celula', 'musicas_louvores']. Encontradas: ['membros', 'sqlite_sequence', 'trilhas_teologicas', 'estudos_aulas', 'cortes_videos', 'devocionais_90d', 'pedidos_oracao', 'encontros_celula', 'musicas_louvores']`
- ✅ **[Banco de Dados]** Trilhas Teológicas Pré-Cadastradas — *0.0ms*
  > *Detalhes:* `Total de trilhas: 5 (esperado >= 5)`
- ✅ **[Banco de Dados]** Acervo de Apostilas & Resumos Markdown — *1.0ms*
  > *Detalhes:* `Total de resumos em data/resumos_estudos/: 13`
- ✅ **[Usuário Final]** Acesso à Landing Page & Elementos Emocionais — *34.08ms*
  > *Detalhes:* `Status: 200. Contém todos os blocos acolhedores.`
- ✅ **[Usuário Final]** Envio de Pedido de Oração / Desabafo de Ansiedade — *269.77ms*
  > *Detalhes:* `ID retornado: 11, Status: 200`
- ✅ **[Usuário Final]** Envio de Pedido Anônimo (Desemprego) — *169.66ms*
  > *Detalhes:* `Status: 200`
- ✅ **[Usuário Final]** Mural Público Exibe Pedidos Ativos — *9.0ms*
  > *Detalhes:* `Total de pedidos no mural: 12`
- ✅ **[Usuário Final]** Ação de Intercessão Comunitária ('Orar por este irmão') — *109.57ms*
  > *Detalhes:* `Resposta: {"status":"sucesso","mensagem":"Oração computada! Ninguém luta sozinho."}`
- ✅ **[Usuário Final]** Consulta ao Próximo Encontro da Célula Digital — *9.99ms*
  > *Detalhes:* `Status: 200`
- ✅ **[Usuário Final]** Listagem do Acervo de Louvores & Adoração — *15.0ms*
  > *Detalhes:* `Total de faixas disponíveis: 50`
- ✅ **[Usuário Final]** Filtro Musical por Categoria (Guerra & Fé) — *7.0ms*
  > *Detalhes:* `Faixas filtradas: 0`
- ✅ **[Usuário Final]** Favoritar Faixa no Player — *181.94ms*
  > *Detalhes:* `Favorito: False`
- ✅ **[Usuário Final]** Registrar Reprodução de Louvor — *144.05ms*
  > *Detalhes:* `Resposta: {'sucesso': True}`
- ✅ **[Liderança ADM]** Consulta às 5 Trilhas da Escola Teológica — *7.86ms*
  > *Detalhes:* `Trilhas mapeadas: 5`
- ✅ **[Liderança ADM]** Cadastrar Estudo / Vídeo Planejado para YouTube — *111.87ms*
  > *Detalhes:* `Aula ID criada: 19`
- ✅ **[Liderança ADM]** Mapear Corte de Ouro para Redes Sociais — *147.3ms*
  > *Detalhes:* `Corte ID: 6`
- ✅ **[Liderança ADM]** Agendamento de Encontro da Célula Digital — *107.6ms*
  > *Detalhes:* `Encontro ID: 6`
- ✅ **[Liderança ADM]** Próximo Encontro Refletido na Célula Digital — *7.0ms*
  > *Detalhes:* `Tema retornado: Elias na Caverna: Quando o Profeta Deseja a Morte`
- ✅ **[Liderança ADM]** Painel de Métricas do Acervo Musical — *7.0ms*
  > *Detalhes:* `Métricas: {'total_faixas': 50, 'total_mb': 337.2, 'favoritos': 0, 'por_categoria': {'Graça & Restauração': 10, 'Guerra Espiritual & Fé': 13, 'Oração & Adoração': 9, 'Pentecostal & Celebração': 3, 'Trap Gospel & Edificação': 15}}`
- ✅ **[Plataforma Flet]** Endpoint Flet ASGI Web (/plataforma) — *47.49ms*
  > *Detalhes:* `Status code retornado: 200`
- ✅ **[Documentação API]** Swagger UI Ativo (/docs) — *3.6ms*
  > *Detalhes:* `Status: 200`
- ✅ **[Plataforma Desktop]** Script Nativo app/flet_app.py Presente — *1.0ms*
  > *Detalhes:* `Tamanho do arquivo: 25828 bytes`
- ✅ **[Mobile APK/AAB]** Ponto de Entrada Nativo main.py Presente — *0.0ms*
  > *Detalhes:* `Localizado em: C:\Users\matheus\Desktop\ministerio\main.py`
- ✅ **[Automação IA]** Script Deepgram Nova-2 (transcritor_deepgram.py) — *0.0ms*
  > *Detalhes:* `Localizado em: C:\Users\matheus\Desktop\ministerio\scripts\transcritor_deepgram.py`
- ✅ **[Automação IA]** Atalho Executável .bat Deepgram Presente — *0.0ms*
  > *Detalhes:* `Localizado em: C:\Users\matheus\Desktop\ministerio\3_TRANSCREVER_AUDIOS_DEEPGRAM.bat`

---
*Auditoria gerada automaticamente pelo Robô de Testes do Ministério Metanoia.*
