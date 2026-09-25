# 🗺️ MEGA PLANO DE IMPLEMENTAÇÃO // MINISTÉRIO METANOIA
### *Arquitetura Integrada: Reino, Discipulado, Audiovisual, Engenharia de Software & IA*

> *"Edifica a tua casa na rocha; vieram as chuvas, transbordaram os rios, sopraram os ventos e deram com ímpeto contra aquela casa, que não caiu, porque fora edificada sobre a rocha."*  
> — **Mateus 7:24-25**

---

## 🏛️ 1. A VISÃO INTEGRADA EM 360 GRAUS

O **Ministério Metanoia** não opera em silos isolados. Cada peça alimenta a outra num ciclo virtuoso de crescimento espiritual e tecnológico:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        O CICLO VIRTUOSO DO MINISTÉRIO METANOIA                         │
├────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                        │
│   1. ATRAÇÃO (Fronteira)          2. ACOLHIMENTO (Trincheira)                          │
│   ┌─────────────────────┐         ┌─────────────────────────┐                          │
│   │ Vídeos Curtos       │────────►│ A Célula Digital        │                          │
│   │ (Reels/TikTok/Shorts│         │ (Encontro semanal 60 min│                          │
│   │ Roteiros G.P.B.A.)  │         │ Google Meet / WhatsApp) │                          │
│   └─────────────────────┘         └────────────┬────────────┘                          │
│                                                │                                       │
│                                                ▼                                       │
│   4. MULTIPLICAÇÃO                3. DISCIPULADO DIÁRIO (O Altar)                      │
│   ┌─────────────────────┐         ┌─────────────────────────┐                          │
│   │ Novos Líderes de    │◄────────│ O App Metanoia          │                          │
│   │ Célula, Honra Local │         │ (Ordem Matinal, Manual  │                          │
│   │ na IBPMCR & Reino   │         │ da Vida Cristã, SOS)    │                          │
│   └─────────────────────┘         └─────────────────────────┘                          │
│                                                                                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 2. CRONOGRAMA GERAL DAS 5 FASES DE EXECUÇÃO

| Fase | Nome da Fase | Duração | Foco Principal | Entregável Chave |
| :---: | :--- | :---: | :--- | :--- |
| **01** | **Fundação do Altar & Voz** | Semanas 1 a 2 | Gravação dos primeiros vídeos + Setup do Backend | 5 vídeos gravados + Base FastAPI/SQLite |
| **02** | **Lançamento da Célula Digital**| Semanas 3 a 4 | 1º Encontro online + Pastoreio no WhatsApp | 1ª Célula realizada + Grupo de Intercessão |
| **03** | **O App Pastoral / Metanoia** | Mês 2 (Sem. 5-8) | Código do App (Flet/PWA) + Manual Interativo | App funcional com Ordem Matinal e SOS |
| **04** | **Automação & Fábrica de IA** | Mês 3 (Sem. 9-12)| Pipeline de vídeos automáticos + Esteira Social | Script Edge-TTS/FFmpeg + Upload Shorts |
| **05** | **Sustentabilidade & Expansão**| Mês 4 em diante| Multiplicação de Células + Apoio à Igreja Local | Área de Membros Pix + Novos Líderes |

---

## 📍 DETALHAMENTO FASE A FASE

---

### 🛡️ FASE 01: FUNDAÇÃO DO ALTAR & DA VOZ (Semanas 01 e 02)
*Objetivo: Estabelecer a rotina devocional pessoal, gravar os primeiros conteúdos e levantar a espinha dorsal do software.*

#### A. Frente Ministerial & Pessoal:
1. **Consagração Matinal:** Estabelecer a Ordem Matinal das 06h00 (leitura bíblica, oração secreta e 15 minutos de silêncio diante de Deus).
2. **Configuração dos Perfis Oficiais:**
   * Nome: **Matheus Barbosa // Metanoia**
   * Bio magnética com foco nos cansados, trabalhadores em escala e homens em busca de honra.
   * Link único na bio direcionando para o canal de WhatsApp da Célula Digital.

#### B. Frente Audiovisual (Gravação dos 5 Primeiros Vídeos):
* Utilizar os roteiros prontos em [`ROTEIROS_VIDEOS_MINISTERIAIS.md`](./ROTEIROS_VIDEOS_MINISTERIAIS.md):
  * **Vídeo 1:** *"Para quem não consegue ir à igreja por causa do trabalho"* (O chamado da Célula Digital).
  * **Vídeo 2:** *"Você tenta orar 5 minutos e sua mente vai pra 10 lugares?"* (Dopamina e Romanos 12:2).
  * **Vídeo 3:** *"Para quem caiu hoje e está com vergonha de Deus"* (1 João 2:1 — O Advogado dos quebrantados).
  * **Vídeo 4:** *"O celular na cama é a armadilha do covarde"* (Mudança radical de ambiente).
  * **Vídeo 5:** *"Perdão não é sentimento, é mandamento legal"* (Efésios 4:32).

#### C. Frente Técnica & Engenharia de Software:
* Inicialização da estrutura de pastas em `c:\Users\matheus\Desktop\ministerio\`:
  ```
  ministerio/
  ├── app/
  │   ├── core/          # Configurações, segurança e constantes
  │   ├── db/            # Conexão SQLite (ministerio.db) e migrations
  │   ├── models/        # Entidades: Membro, Celula, Oracao, Devocional
  │   ├── routers/       # Endpoints FastAPI REST
  │   ├── services/      # Lógica de negócio ministerial
  │   └── views/         # Interface gráfica (Flet)
  ├── scripts/           # Ferramentas auxiliares e automações
  ├── data/              # Banco de dados e mídias estáticas
  └── tests/             # Testes automatizados de integridade
  ```
* Implementação do modelo de dados inicial no SQLite:
  * Tabela `membros`: ID, nome, whatsapp, role (discípulo, intercessor, líder), data_cadastro.
  * Tabela `pedidos_oracao`: ID, membro_id, motivo, status (pendente, em_oracao, respondido), data.
  * Tabela `devocionais_90d`: ID, dia (1 a 90), fase, versiculo, texto, audio_path.

---

### 🌐 FASE 02: O LANÇAMENTO DA CÉLULA DIGITAL (Semanas 03 e 04)
*Objetivo: Abrir a primeira sala ao vivo para acolher pessoas que estão fora da igreja e ativar a comunidade no WhatsApp.*

#### A. Frente Ministerial & Pastoral:
1. **Agendamento do Encontro Piloto:**
   * Definir dia e horário estratégico (ex: Terça-feira ou Quinta-feira às 20h30).
   * Duração estrita: **60 minutos** (pelo Google Meet).
2. **Execução do Roteiro Piloto:**
   * Seguir linha a linha o [`ROTEIROS_CELULA_DIGITAL.md`](./ROTEIROS_CELULA_DIGITAL.md) (*O Deus que Visita o Quarto Escuro — Elias na Caverna*).
3. **Ativação da Comunhão Assíncrona no WhatsApp:**
   * **06h30:** Áudio devocional de 2 minutos gravado pelo Matheus.
   * **12h00:** Card visual do Versículo de Combate.
   * **21h30:** Mural de Intercessão: *"Quem precisa de oração urgente antes de dormir?"*

#### B. Frente Técnica:
1. **API de Pedidos de Oração:**
   * Endpoint `POST /api/oracao/pedir`: Recebe o pedido do membro via app ou formulário web leve.
   * Endpoint `GET /api/oracao/mural`: Exibe os pedidos anônimos ou nominais para os irmãos da célula intercederem.
2. **Bot Integrador WhatsApp (Webhook / URL Scheme):**
   * Geração automática de links `wa.me` para que os membros enviem seus testemunhos e relatórios diários de honra com 1 toque.

---

### 💻 FASE 03: O APP PASTORAL / METANOIA (Mês 02 // Semanas 05 a 08)
*Objetivo: Integrar as lições de 90 dias, o botão SOS e o Manual da Vida Cristã numa aplicação fluida (Desktop e Mobile PWA).*

#### A. Módulos da Aplicação:
1. **Módulo 1 // A Forja dos 90 Dias:**
   * Lições diárias estruturadas nos 5 Graus de Maturidade (O Resgatado, O Discípulo, O Guerreiro, O Sacerdote e O Patriarca).
   * Player Audio-First integrado para ouvir o devocional no trânsito ou ao acordar.
   * Teologia da Graça: método `zerar_contador_com_graca()` (sem humilhação neurótica, preservando o recorde histórico).
2. **Módulo 2 // O Protocolo Sentinela SOS 180s:**
   * Botão de pânico espiritual para momentos de forte tentação, ansiedade ou ataque de pânico.
   * Cronômetro regressivo com técnicas de choque vagal (água gelada no rosto, flexões de solo) e versículos de vitória imediata.
3. **Módulo 3 // O Manual Interativo da Vida Cristã:**
   * Navegação direta pelas fichas de [`MANUAL_DA_VIDA_CRISTA.md`](./MANUAL_DA_VIDA_CRISTA.md):
     * Ficha 01: Como orar quando não sinto vontade (Método A.C.A.S. de 15 min).
     * Ficha 02: Guerra contra dopamina e método H.A.L.T.
     * Ficha 03: Jejum passo a passo para iniciantes.
     * Ficha 04: O decreto do perdão legal e cura da amargura.
     * Ficha 05: Governo financeiro e primícias.

#### B. Entregável Técnico da Fase:
* App rodando localmente via `1_RODAR_APP.bat` (Flet Python) e exportável como Web App / PWA para celular.

---

### ⚡ FASE 04: AUTOMAÇÃO & FÁBRICA DE IA (Mês 03 // Semanas 09 a 12)
*Objetivo: Escalar a distribuição de mensagens bíblicas sem sobrecarregar a rotina ministerial.*

#### A. Pipeline Audiovisual Inteligente (Python):
1. **Geração de Áudio Neural Natural:**
   * Utilização do `edge-tts` com voz masculina solene e natural em português (`pt-BR-AntonioNeural` ou `pt-BR-FabioNeural`), calibrada sem eco ou pitch artificial.
2. **Montagem Automatizada de Vídeo (FFmpeg + MoviePy):**
   * Seleção dinâmica de vídeos de fundo de alta definição (cinematográficos: natureza, tempestade, homem orando, ferro forjando).
   * Cortes suaves a cada 2.5 a 3 segundos para manter alta retenção visual.
   * Legendas queimadas em padrão ASS (amarelo ouro com contorno preto grosso na zona segura do Shorts/Reels).
3. **Esteira de Agendamento:**
   * Módulo para agendar postagens automáticas no YouTube Shorts via YouTube Data API v3.
   * Integração de webhooks para Instagram Reels e TikTok.

---

### 🕊️ FASE 05: SUSTENTABILIDADE, MULTIPLICAÇÃO & HONRA LOCAL (Mês 04 em Diante)
*Objetivo: Consolidar o ministério, formar novos líderes e apoiar a igreja local com fruto maduro.*

#### A. Frente Ministerial & Eclesiástica:
1. **Multiplicação da Célula Digital:**
   * Quando o grupo ultrapassar 15 a 20 pessoas ativas na sala, formar o primeiro casal/irmão maduro para liderar a segunda Célula Digital (Célula 2).
2. **Honra e Alinhamento com a IBPMCR:**
   * Apresentar ao pastor presidente da igreja local o testemunho das vidas alcançadas (pessoas afastadas que voltaram a orar, trabalhadores noturnos acolhidos).
   * Conectar os membros da Célula que residem na região aos cultos presenciais de domingo e batismos.

#### B. Frente de Sustentabilidade Financeira:
1. **Apoio Voluntário & Assinatura Pix:**
   * Checkout Pix dinâmico integrado no app para apoiadores da obra (R$ 29,90/mês).
   * O recurso sustenta os custos de servidores, licenças de APIs, gravação de material e apoio a missões/famílias carentes da congregação.

---

## 🛠️ 3. MATRIZ DE RISCOS & CONTRAMEDIDAS

| Risco Potencial | Causa Raiz | Ação Preventiva (Contramedida) |
| :--- | :--- | :--- |
| **Sobrecarga do Líder** | Tentar fazer tudo ao mesmo tempo (vídeos, código, pastoreio). | Adotar a **Rotina de Produção em Lote** (gravação 1x por semana, 2h no sábado). |
| **Esfriamento da Célula** | Encontros longos, monótonos ou debates teológicos vazios. | Seguir rigidamente o teto de **60 minutos** e focar em acolhimento e dor real. |
| **Complexidade no Código** | Fazer arquitetura pesada antes de ter usuários. | Utilizar **SQLite + FastAPI + Flet**: simples, robusto, roda em qualquer máquina. |
| **Ataque de Culpa Espiritual**| Tropeçar em alguma disciplina e desistir de tudo. | Viver a **Teologia da Graça (Pv 24:16)**: o justo se levanta no mesmo segundo. |

---

## 🚀 4. OS PRIMEIROS PASSOS DE HOJE (CHECKLIST DE DECOLAGEM)

- [x] Manifesto do Ministério registrado em [`README.md`](./README.md)
- [x] Estratégia de Reino documentada em [`ESTRATEGIA_MINISTERIAL_METANOIA.md`](./ESTRATEGIA_MINISTERIAL_METANOIA.md)
- [x] Fichas operacionais de discipulado em [`MANUAL_DA_VIDA_CRISTA.md`](./MANUAL_DA_VIDA_CRISTA.md)
- [x] Calendário editorial de 52 semanas em [`PLANO_DE_CONTEUDO_1_ANO.md`](./PLANO_DE_CONTEUDO_1_ANO.md)
- [x] Manual e roteiro piloto da Célula Digital em [`ROTEIROS_CELULA_DIGITAL.md`](./ROTEIROS_CELULA_DIGITAL.md)
- [x] 5 roteiros completos em modo teleprompter em [`ROTEIROS_VIDEOS_MINISTERIAIS.md`](./ROTEIROS_VIDEOS_MINISTERIAIS.md)
- [x] Mega Plano de Implementação formalizado em [`MEGA_PLANO_DE_IMPLEMENTACAO.md`](./MEGA_PLANO_DE_IMPLEMENTACAO.md)
- [ ] **Próximo Passo Imediato:** Iniciar a codificação do Backend FastAPI e Banco SQLite (`app/`)
