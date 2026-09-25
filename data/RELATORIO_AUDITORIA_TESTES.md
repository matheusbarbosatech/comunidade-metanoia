# 🛡️ RELATÓRIO OFICIAL DE AUDITORIA & TESTES E2E
> **Ministério Metanoia // Plataforma Pastoral, Escola Teológica & Landing Page**  
> **Data da Auditoria:** 25/09/2026 às 19:04:50  
> **Taxa de Sucesso:** 100.0% (26/26 testes aprovados)  
> **Tempo de Execução:** 7.16 segundos  

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

- ✅ **[Banco de Dados]** Tabelas Essenciais Criadas — *949.56ms*
  > *Detalhes:* `Esperadas: ['membros', 'trilhas_teologicas', 'estudos_aulas', 'cortes_videos', 'devocionais_90d', 'pedidos_oracao', 'encontros_celula', 'musicas_louvores']. Encontradas: ['membros', 'sqlite_sequence', 'trilhas_teologicas', 'estudos_aulas', 'cortes_videos', 'devocionais_90d', 'pedidos_oracao', 'encontros_celula', 'musicas_louvores', 'artigos_blog', 'postagens_redes_sociais', 'comunidade_espacos', 'comunidade_posts', 'comunidade_comentarios', 'comunidade_reacoes']`
- ✅ **[Banco de Dados]** Trilhas Teológicas Pré-Cadastradas — *0.0ms*
  > *Detalhes:* `Total de trilhas: 5 (esperado >= 5)`
- ✅ **[Banco de Dados]** Acervo de Apostilas & Resumos Markdown — *0.99ms*
  > *Detalhes:* `Total de resumos em data/resumos_estudos/: 13`
- ✅ **[Usuário Final]** Acesso à Landing Page & Elementos Emocionais — *617.48ms*
  > *Detalhes:* `Status: 200. Contém todos os blocos acolhedores.`
- ✅ **[Usuário Final]** Envio de Pedido de Oração / Desabafo de Ansiedade — *1690.97ms*
  > *Detalhes:* `ID retornado: 33, Status: 200`
- ✅ **[Usuário Final]** Envio de Pedido Anônimo (Desemprego) — *381.57ms*
  > *Detalhes:* `Status: 200`
- ✅ **[Usuário Final]** Mural Público Exibe Pedidos Ativos — *65.4ms*
  > *Detalhes:* `Total de pedidos no mural: 34`
- ✅ **[Usuário Final]** Ação de Intercessão Comunitária ('Orar por este irmão') — *367.18ms*
  > *Detalhes:* `Resposta: {"status":"sucesso","mensagem":"Oração computada! Ninguém luta sozinho."}`
- ✅ **[Usuário Final]** Consulta ao Próximo Encontro da Célula Digital — *277.95ms*
  > *Detalhes:* `Status: 200`
- ✅ **[Usuário Final]** Listagem do Acervo de Louvores & Adoração — *210.86ms*
  > *Detalhes:* `Total de faixas disponíveis: 51`
- ✅ **[Usuário Final]** Filtro Musical por Categoria (Guerra & Fé) — *25.9ms*
  > *Detalhes:* `Faixas filtradas: 0`
- ✅ **[Usuário Final]** Favoritar Faixa no Player — *328.09ms*
  > *Detalhes:* `Favorito: True`
- ✅ **[Usuário Final]** Registrar Reprodução de Louvor — *265.68ms*
  > *Detalhes:* `Resposta: {'sucesso': True}`
- ✅ **[Liderança ADM]** Consulta às 5 Trilhas da Escola Teológica — *46.41ms*
  > *Detalhes:* `Trilhas mapeadas: 5`
- ✅ **[Liderança ADM]** Cadastrar Estudo / Vídeo Planejado para YouTube — *618.84ms*
  > *Detalhes:* `Aula ID criada: 30`
- ✅ **[Liderança ADM]** Mapear Corte de Ouro para Redes Sociais — *279.35ms*
  > *Detalhes:* `Corte ID: 17`
- ✅ **[Liderança ADM]** Agendamento de Encontro da Célula Digital — *477.34ms*
  > *Detalhes:* `Encontro ID: 17`
- ✅ **[Liderança ADM]** Próximo Encontro Refletido na Célula Digital — *7.0ms*
  > *Detalhes:* `Tema retornado: Elias na Caverna: Quando o Profeta Deseja a Morte`
- ✅ **[Liderança ADM]** Painel de Métricas do Acervo Musical — *9.0ms*
  > *Detalhes:* `Métricas: {'total_faixas': 51, 'total_mb': 338.3, 'favoritos': 2, 'por_categoria': {'Graça & Restauração': 10, 'Guerra Espiritual & Fé': 13, 'Oração & Adoração': 9, 'Pentecostal & Celebração': 3, 'Pregação & Devocional': 1, 'Trap Gospel & Edificação': 15}}`
- ✅ **[Plataforma Flet]** Endpoint Flet ASGI Web (/plataforma) — *389.07ms*
  > *Detalhes:* `Status code retornado: 200`
- ✅ **[Documentação API]** Swagger UI Ativo (/docs) — *4.0ms*
  > *Detalhes:* `Status: 200`
- ✅ **[Plataforma Desktop]** Script Nativo app/flet_app.py Presente — *0.0ms*
  > *Detalhes:* `Tamanho do arquivo: 35980 bytes`
- ✅ **[Mobile APK/AAB]** Ponto de Entrada Nativo main.py Presente — *0.0ms*
  > *Detalhes:* `Localizado em: C:\Users\matheus\Desktop\ministerio\main.py`
- ✅ **[Identidade Visual]** Favicon & Ícones Oficiais do Site (/favicon.ico, SVG e Apple) — *141.72ms*
  > *Detalhes:* `Favicon: 200, SVG: 200, Apple: 200`
- ✅ **[Automação IA]** Script Deepgram Nova-2 (transcritor_deepgram.py) — *0.0ms*
  > *Detalhes:* `Localizado em: C:\Users\matheus\Desktop\ministerio\scripts\transcritor_deepgram.py`
- ✅ **[Automação IA]** Atalho Executável .bat Deepgram Presente — *0.0ms*
  > *Detalhes:* `Localizado em: C:\Users\matheus\Desktop\ministerio\3_TRANSCREVER_AUDIOS_DEEPGRAM.bat`

---
*Auditoria gerada automaticamente pelo Robô de Testes do Ministério Metanoia.*
