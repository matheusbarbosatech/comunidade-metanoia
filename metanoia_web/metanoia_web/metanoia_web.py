"""Comunidade Metanoia // Plataforma Web Oficial em Reflex (100% Python Puro).
O Copiloto da Vida Cristã - Rotina Guiada de 10 min, Mural de Oração Comunitário, Cadastro e Checkout.
"""
import reflex as rx
import sqlite3
from pathlib import Path
from rxconfig import config

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "ministerio.db"

class MetanoiaState(rx.State):
    """Estado Reativo Global do Metanoia (100% Python)."""

    # --- Estado: Mural de Oração ---
    nome_oracao: str = ""
    motivo_oracao: str = ""
    anonimo: bool = False
    intercessoes_hoje: int = 168
    pedidos_recentes: list[dict[str, str]] = [
        {"nome": "Irmão em Cristo", "motivo": "Sensação de estar perdido na fé e ansiedade com o trabalho. Buscando paz.", "intercessoes": "23"},
        {"nome": "Anônimo", "motivo": "Dificuldade de manter a disciplina para ler a Bíblia e orar diariamente.", "intercessoes": "35"},
        {"nome": "Novo na Fé", "motivo": "Agradecendo pelo recomeço e pedindo sabedoria para lidar com a família.", "intercessoes": "19"},
    ]

    # --- Estado: Rotina Diária de 10 Minutos ---
    habito_feito_hoje: bool = False
    dias_constancia: int = 4
    oracao_pessoal: str = ""
    oracao_salva: bool = False

    # --- Estado: Cadastro de Membros ---
    cad_nome: str = ""
    cad_email: str = ""
    cad_whatsapp: str = ""
    cad_momento: str = "Novo convertido (dando os primeiros passos)"
    cad_concluido: bool = False

    def enviar_pedido_oracao(self):
        """Salva o pedido de oração no SQLite e atualiza o feed."""
        if not self.motivo_oracao.strip():
            return rx.toast.error("Por favor, digite seu desabafo ou motivo de oração.")

        nome_final = "Anônimo" if self.anonimo or not self.nome_oracao.strip() else self.nome_oracao.strip()

        if DB_PATH.exists():
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO pedidos_oracao (nome_solicitante, motivo, anonimo, status)
                VALUES (?, ?, ?, 'em_oracao')
                """, (nome_final, self.motivo_oracao, 1 if self.anonimo else 0))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"[Aviso DB Pedidos] {e}")

        self.pedidos_recentes.insert(0, {
            "nome": nome_final,
            "motivo": self.motivo_oracao,
            "intercessoes": "1"
        })
        self.intercessoes_hoje += 1
        self.motivo_oracao = ""
        self.nome_oracao = ""
        return rx.toast.success("Seu clamor foi publicado no mural. Nossos irmãos já estão orando por você!")

    def interceder(self, index: int):
        """Ação de orar por um irmão em 1 clique."""
        try:
            atual = int(self.pedidos_recentes[index]["intercessoes"])
            self.pedidos_recentes[index]["intercessoes"] = str(atual + 1)
            self.intercessoes_hoje += 1
            return rx.toast("🤍 Você orou por este irmão! Deus ouve cada clamor sincero.")
        except Exception:
            pass

    def marcar_rotina_concluida(self):
        """Marca o devocional de hoje como concluído."""
        self.habito_feito_hoje = not self.habito_feito_hoje
        if self.habito_feito_hoje:
            self.dias_constancia += 1
            return rx.toast.success("Glória a Deus! 10 minutos de conexão cumpridos com sucesso hoje. 🔥")
        else:
            self.dias_constancia = max(0, self.dias_constancia - 1)

    def salvar_oracao_diaria(self):
        """Salva a oração/gratidão pessoal do usuário."""
        if not self.oracao_pessoal.strip():
            return rx.toast.error("Escreva pelo menos uma frase de gratidão ou pedido a Deus.")
        self.oracao_salva = True
        return rx.toast.success("Sua oração foi registrada no seu diário espiritual.")

    def registrar_membro(self):
        """Cadastra o novo membro no banco SQLite e prepara acesso."""
        if not self.cad_nome.strip():
            return rx.toast.error("Por favor, preencha seu nome.")
        if not self.cad_email.strip() and not self.cad_whatsapp.strip():
            return rx.toast.error("Informe seu e-mail ou WhatsApp para receber os devocionais.")

        if DB_PATH.exists():
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO membros (nome, email, whatsapp, papel, ativo)
                VALUES (?, ?, ?, 'membro', 1)
                """, (self.cad_nome.strip(), self.cad_email.strip(), self.cad_whatsapp.strip()))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"[Aviso DB Membros] {e}")

        self.cad_concluido = True
        return rx.toast.success(f"Conta criada com sucesso! Seja bem-vindo à família, {self.cad_nome}!")


# ==============================================================================
# COMPONENTES COMPARTILHADOS (NAVBAR E FOOTER)
# ==============================================================================

def navbar() -> rx.Component:
    """Barra de navegação moderna, limpa e focada."""
    return rx.box(
        rx.hstack(
            rx.link(
                rx.hstack(
                    rx.heading("METANOIA", size="5", weight="bold", color_scheme="amber"),
                    rx.badge("Copiloto Cristão", variant="soft", color_scheme="amber", size="2"),
                    spacing="2",
                    align="center",
                ),
                href="/",
            ),
            rx.hstack(
                rx.link(rx.text("Rotina Diária", size="2", weight="medium"), href="/#rotina"),
                rx.link(rx.text("Mural de Oração", size="2", weight="medium"), href="/#mural"),
                rx.link(rx.text("Como Funciona", size="2", weight="medium"), href="/#como-funciona"),
                rx.link(
                    rx.button("Planos & Assinatura", variant="outline", color_scheme="amber", size="2", radius="full"),
                    href="/checkout",
                ),
                rx.link(
                    rx.button("Criar Conta Grátis", variant="solid", color_scheme="amber", size="2", radius="full"),
                    href="/cadastro",
                ),
                rx.color_mode.button(),
                spacing="4",
                align="center",
            ),
            justify="between",
            align="center",
            width="100%",
            padding_x="6",
            padding_y="4",
        ),
        background="rgba(11, 14, 23, 0.90)",
        backdrop_filter="blur(16px)",
        border_bottom="1px solid var(--gray-4)",
        position="sticky",
        top="0",
        z_index="50",
    )


def footer() -> rx.Component:
    """Rodapé limpo e elegante."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.heading("METANOIA", size="4", weight="bold", color_scheme="amber"),
                rx.text("•", color="gray.500"),
                rx.text("Transformando a mente através de hábitos diários com Deus.", size="2", color="gray.400"),
                spacing="3",
                align="center",
            ),
            rx.text(
                "Feito com carinho para quem não quer mais caminhar sozinho na fé. Todos os direitos reservados.",
                size="1",
                color="gray.600",
            ),
            spacing="2",
            align="center",
        ),
        padding="8",
        border_top="1px solid var(--gray-4)",
        margin_top="16",
        background="var(--gray-2)",
    )


# ==============================================================================
# PÁGINA 1: HOME (ROTINA DE 10 MIN + MURAL + CONVITE)
# ==============================================================================

def hero_section() -> rx.Component:
    """Hero section com proposta de valor clara e sem rodeios."""
    return rx.vstack(
        rx.badge("🤍 O fim do sentimento de estar perdido na fé", variant="surface", color_scheme="amber", size="3"),
        rx.heading(
            "Construa uma Vida com Deus em 10 Minutos por Dia",
            size="9",
            text_align="center",
            max_width="850px",
            line_height="1.15",
        ),
        rx.text(
            "Sem linguagem complicada e sem hipocrisia. Um copiloto prático para guiar sua leitura bíblica, organizar suas orações e conectar você a uma comunidade que ora de verdade por você.",
            size="4",
            color="gray.400",
            text_align="center",
            max_width="660px",
        ),
        rx.hstack(
            rx.link(
                rx.button(
                    "🚀 Começar Minha Jornada Grátis",
                    color_scheme="amber",
                    size="4",
                    radius="full",
                    variant="solid",
                ),
                href="/cadastro",
            ),
            rx.link(
                rx.button(
                    "💎 Ver Planos e Benefícios",
                    variant="soft",
                    color_scheme="gray",
                    size="4",
                    radius="full",
                ),
                href="/checkout",
            ),
            spacing="4",
            margin_top="3",
        ),
        spacing="5",
        align="center",
        padding_y="14",
        padding_x="4",
    )


def rotina_diaria_preview() -> rx.Component:
    """Demonstração da rotina diária de 10 minutos (O Core do SaaS)."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.badge("☀️ Sua Rotina Guiada de Hoje", color_scheme="amber", variant="soft", size="2"),
                rx.badge(
                    f"🔥 {MetanoiaState.dias_constancia} Dias de Constância",
                    color_scheme="orange",
                    variant="solid",
                    size="2",
                ),
                justify="between",
                width="100%",
                align="center",
            ),
            rx.heading("1. A Palavra do Dia (Em Linguagem Direta)", size="5"),
            rx.card(
                rx.vstack(
                    rx.text(
                        "\"Não andeis ansiosos de coisa alguma; em tudo, porém, sejam conhecidas diante de Deus as vossas petições, pela oração e pela súplica, com ações de graças.\"",
                        size="3",
                        font_style="italic",
                        color="amber.300",
                    ),
                    rx.text("— Filipenses 4:6", size="2", weight="bold", color="gray.400"),
                    spacing="1",
                ),
                width="100%",
                background="rgba(245, 158, 11, 0.05)",
                border_left="3px solid var(--amber-9)",
                padding="4",
            ),
            rx.heading("2. Aplicação Prática no Seu Dia", size="4"),
            rx.text(
                "Ansiedade é a tentativa da nossa mente de controlar o que só Deus pode resolver. Antes de começar seu trabalho hoje, entregue sua maior preocupação em uma oração curta e sincera. Você não está no controle de tudo, e tudo bem.",
                size="3",
                color="gray.300",
            ),
            rx.heading("3. Seu Diário de Oração em 3 Linhas", size="4"),
            rx.vstack(
                rx.text_area(
                    placeholder="Pelo que você é grato hoje? O que você precisa entregar nas mãos de Deus?",
                    value=MetanoiaState.oracao_pessoal,
                    on_change=MetanoiaState.set_oracao_pessoal,
                    width="100%",
                    min_height="80px",
                ),
                rx.hstack(
                    rx.button(
                        "💾 Salvar Oração Pessoal",
                        on_click=MetanoiaState.salvar_oracao_diaria,
                        variant="soft",
                        color_scheme="gray",
                        size="2",
                    ),
                    rx.button(
                        rx.cond(
                            MetanoiaState.habito_feito_hoje,
                            "✅ 10 Minutos Cumpridos Hoje!",
                            "⏳ Concluir Rotina de Hoje",
                        ),
                        on_click=MetanoiaState.marcar_rotina_concluida,
                        color_scheme=rx.cond(MetanoiaState.habito_feito_hoje, "green", "amber"),
                        variant="solid",
                        size="2",
                        radius="full",
                    ),
                    justify="between",
                    width="100%",
                    align="center",
                ),
                spacing="3",
                width="100%",
            ),
            spacing="5",
            width="100%",
        ),
        width="100%",
        max_width="780px",
        padding="8",
        margin_x="auto",
        id="rotina",
    )


def como_funciona_section() -> rx.Component:
    """3 passos simples de como o Metanoia transforma a rotina."""
    passos = [
        ("1️⃣", "10 Minutos Pela Manhã", "Abra o Metanoia ao acordar. Leia o versículo selecionado e a explicação prática para o seu dia a dia."),
        ("2️⃣", "Diário & Oração Guiada", "Escreva seu clamor e suas gratidões. Chega de travar sem saber o que falar com Deus."),
        ("3️⃣", "Mural & Acolhimento", "Quando as lutas apertarem, peça oração no mural. Irmãos reais vão interceder por você em tempo real."),
    ]
    return rx.vstack(
        rx.badge("💡 Passo a Passo Descomplicado", color_scheme="amber", variant="soft"),
        rx.heading("Como o Metanoia te ajuda a não desistir", size="7", text_align="center"),
        rx.text("Criado especialmente para quem sente que não tem tempo ou se perde na rotina da fé.", color="gray.400", text_align="center"),
        rx.grid(
            *[
                rx.card(
                    rx.vstack(
                        rx.text(icone, size="7"),
                        rx.heading(titulo, size="4"),
                        rx.text(desc, size="2", color="gray.400"),
                        spacing="2",
                    ),
                    padding="6",
                )
                for icone, titulo, desc in passos
            ],
            columns=rx.breakpoints(initial="1", sm="3"),
            spacing="4",
            width="100%",
            max_width="950px",
        ),
        spacing="6",
        align="center",
        padding_y="12",
        id="como-funciona",
        width="100%",
    )


def mural_oracao_section() -> rx.Component:
    """Mural de oração comunitário e acolhedor."""
    return rx.vstack(
        rx.vstack(
            rx.badge("🕊️ Intercessão Comunitária", color_scheme="amber", variant="soft"),
            rx.heading("Mural de Oração: Ninguém Luta Sozinho", size="7"),
            rx.text(
                "Desabafe o que está pesando no seu coração. Nossa comunidade se une para orar por você.",
                color="gray.400",
                text_align="center",
            ),
            spacing="2",
            align="center",
        ),
        rx.card(
            rx.vstack(
                rx.input(
                    placeholder="Seu nome (ou deixe em branco para publicar como Anônimo)",
                    value=MetanoiaState.nome_oracao,
                    on_change=MetanoiaState.set_nome_oracao,
                    width="100%",
                ),
                rx.text_area(
                    placeholder="Escreva seu motivo de oração ou desabafo sincero...",
                    value=MetanoiaState.motivo_oracao,
                    on_change=MetanoiaState.set_motivo_oracao,
                    width="100%",
                    min_height="90px",
                ),
                rx.hstack(
                    rx.checkbox(
                        "Publicar como Anônimo",
                        checked=MetanoiaState.anonimo,
                        on_change=MetanoiaState.set_anonimo,
                    ),
                    rx.button(
                        "🕊️ Enviar Clamor ao Mural",
                        on_click=MetanoiaState.enviar_pedido_oracao,
                        color_scheme="amber",
                        radius="full",
                    ),
                    justify="between",
                    width="100%",
                    align="center",
                ),
                spacing="3",
            ),
            width="100%",
            max_width="680px",
            padding="6",
        ),
        rx.badge(
            f"🤍 {MetanoiaState.intercessoes_hoje} orações já levantadas pelos irmãos hoje",
            color_scheme="green",
            variant="soft",
            size="3",
        ),
        rx.vstack(
            rx.foreach(
                MetanoiaState.pedidos_recentes,
                lambda pedido, index: rx.card(
                    rx.hstack(
                        rx.vstack(
                            rx.hstack(
                                rx.text(f"👤 {pedido['nome']}", weight="bold", size="2", color="amber.300"),
                                rx.badge("Em oração", variant="surface", color_scheme="amber", size="1"),
                                spacing="2",
                                align="center",
                            ),
                            rx.text(pedido["motivo"], size="3", color="gray.200"),
                            spacing="1",
                        ),
                        rx.button(
                            f"🙏 Orei ({pedido['intercessoes']})",
                            on_click=lambda: MetanoiaState.interceder(index),
                            variant="soft",
                            color_scheme="amber",
                            size="2",
                            radius="full",
                        ),
                        justify="between",
                        align="center",
                        width="100%",
                    ),
                    width="100%",
                    padding="4",
                ),
            ),
            spacing="3",
            width="100%",
            max_width="680px",
        ),
        spacing="6",
        align="center",
        padding_y="12",
        id="mural",
        width="100%",
    )


def index() -> rx.Component:
    """Página inicial minimalista e transformadora."""
    return rx.box(
        navbar(),
        rx.container(
            hero_section(),
            rotina_diaria_preview(),
            como_funciona_section(),
            mural_oracao_section(),
            max_width="1100px",
        ),
        footer(),
        min_height="100vh",
        background="var(--gray-1)",
    )


# ==============================================================================
# PÁGINA 2: CADASTRO (/cadastro)
# ==============================================================================

def cadastro_page() -> rx.Component:
    """Página de Inscrição e Onboarding do Novo Membro."""
    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                rx.badge("🌱 Comece sua Caminhada", color_scheme="amber", variant="surface", size="3"),
                rx.heading("Crie Sua Conta Gratuita no Metanoia", size="8", text_align="center"),
                rx.text(
                    "Dê o primeiro passo para uma vida espiritual constante. Preencha seus dados abaixo para acessar sua rotina diária.",
                    color="gray.400",
                    text_align="center",
                    max_width="560px",
                ),
                rx.card(
                    rx.vstack(
                        rx.cond(
                            MetanoiaState.cad_concluido,
                            rx.callout(
                                "🎉 Sua conta foi criada com sucesso! Você já pode acessar a rotina e o mural, ou escolher um plano para desbloquear a mentoria completa.",
                                icon="check_check",
                                color_scheme="green",
                                size="3",
                            ),
                            rx.fragment(),
                        ),
                        rx.vstack(
                            rx.text("Nome Completo", size="2", weight="bold"),
                            rx.input(
                                placeholder="Ex: Matheus Barbosa",
                                value=MetanoiaState.cad_nome,
                                on_change=MetanoiaState.set_cad_nome,
                                width="100%",
                                size="3",
                            ),
                            spacing="1",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.text("Seu Melhor E-mail", size="2", weight="bold"),
                            rx.input(
                                placeholder="seuemail@exemplo.com",
                                type="email",
                                value=MetanoiaState.cad_email,
                                on_change=MetanoiaState.set_cad_email,
                                width="100%",
                                size="3",
                            ),
                            spacing="1",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.text("WhatsApp (com DDD)", size="2", weight="bold"),
                            rx.input(
                                placeholder="Ex: (11) 98765-4321",
                                value=MetanoiaState.cad_whatsapp,
                                on_change=MetanoiaState.set_cad_whatsapp,
                                width="100%",
                                size="3",
                            ),
                            rx.text("Opcional: para você receber a rotina e versículo diário direto no seu WhatsApp.", size="1", color="gray.500"),
                            spacing="1",
                            width="100%",
                        ),
                        rx.vstack(
                            rx.text("Qual é o seu momento espiritual hoje?", size="2", weight="bold"),
                            rx.select(
                                [
                                    "Novo convertido (dando os primeiros passos)",
                                    "Voltando para os caminhos de Deus agora",
                                    "Já sou cristão, mas luto contra a inconstância",
                                    "Quero me aprofundar e ajudar outras pessoas",
                                ],
                                value=MetanoiaState.cad_momento,
                                on_change=MetanoiaState.set_cad_momento,
                                width="100%",
                                size="3",
                            ),
                            spacing="1",
                            width="100%",
                        ),
                        rx.button(
                            "✨ Concluir Cadastro Gratuito",
                            on_click=MetanoiaState.registrar_membro,
                            color_scheme="amber",
                            size="3",
                            radius="full",
                            width="100%",
                            margin_top="3",
                        ),
                        rx.hstack(
                            rx.text("Já conhece nossos planos completos?", size="2", color="gray.400"),
                            rx.link(rx.text("Conhecer o Metanoia Pro ➔", size="2", weight="bold", color="amber.300"), href="/checkout"),
                            justify="center",
                            width="100%",
                            spacing="2",
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    width="100%",
                    max_width="520px",
                    padding="8",
                ),
                spacing="5",
                align="center",
                padding_y="12",
            ),
            max_width="700px",
        ),
        footer(),
        min_height="100vh",
        background="var(--gray-1)",
    )


# ==============================================================================
# PÁGINA 3: CHECKOUT E PLANOS (/checkout)
# ==============================================================================

def checkout_page() -> rx.Component:
    """Página de Planos, Benefícios e Checkout."""
    return rx.box(
        navbar(),
        rx.container(
            rx.vstack(
                rx.badge("💎 Invista na sua Vida Espiritual", color_scheme="amber", variant="surface", size="3"),
                rx.heading("Escolha o Plano Ideal para a Sua Caminhada", size="8", text_align="center"),
                rx.text(
                    "Menos que o valor de um café por dia para você ter clareza diária, suporte de oração e nunca mais se sentir perdido.",
                    color="gray.400",
                    text_align="center",
                    max_width="620px",
                ),
                rx.grid(
                    # CARD PLANO MENSAL
                    rx.card(
                        rx.vstack(
                            rx.badge("Plano Mensal", variant="soft", color_scheme="gray", size="2"),
                            rx.heading("R$ 19,90", size="8", color_scheme="amber"),
                            rx.text("Cobrado mensalmente. Cancele quando quiser.", size="2", color="gray.400"),
                            rx.separator(width="100%"),
                            rx.vstack(
                                rx.text("✓ Rotina diária de 10 min guiada", size="2"),
                                rx.text("✓ Mural de oração comunitário ilimitado", size="2"),
                                rx.text("✓ Diário de orações e gratidões", size="2"),
                                rx.text("✓ Devocionais diários no WhatsApp", size="2"),
                                rx.text("✓ Sem fidelidade: cancele em 1 clique", size="2"),
                                spacing="2",
                                width="100%",
                            ),
                            rx.link(
                                rx.button(
                                    "Assinar Plano Mensal",
                                    variant="outline",
                                    color_scheme="amber",
                                    size="3",
                                    radius="full",
                                    width="100%",
                                ),
                                href="https://pay.kiwify.com.br/SEU_LINK_MENSAL",
                                is_external=True,
                                width="100%",
                            ),
                            spacing="4",
                            align="start",
                        ),
                        padding="6",
                    ),
                    # CARD PLANO ANUAL (DESTAQUE)
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.badge("🔥 Mais Escolhido", variant="solid", color_scheme="orange", size="2"),
                                rx.badge("Economize 38%", variant="soft", color_scheme="green", size="2"),
                                justify="between",
                                width="100%",
                                align="center",
                            ),
                            rx.heading("12x R$ 14,70", size="8", color="amber.300"),
                            rx.text("ou R$ 147 à vista por 1 ano inteiro de acesso.", size="2", color="gray.400"),
                            rx.separator(width="100%"),
                            rx.vstack(
                                rx.text("✓ Tudo do Plano Mensal incluído", size="2", weight="bold"),
                                rx.text("✓ Acesso ao Grupo Fechado de Membros", size="2"),
                                rx.text("✓ Trilha de 21 dias para Novos Convertidos", size="2"),
                                rx.text("✓ Acesso a todas as novas funções e atualizações", size="2"),
                                rx.text("✓ Suporte prioritário via WhatsApp", size="2"),
                                spacing="2",
                                width="100%",
                            ),
                            rx.link(
                                rx.button(
                                    "⭐ Garantir Plano Anual com Desconto",
                                    variant="solid",
                                    color_scheme="amber",
                                    size="3",
                                    radius="full",
                                    width="100%",
                                ),
                                href="https://pay.kiwify.com.br/SEU_LINK_ANUAL",
                                is_external=True,
                                width="100%",
                            ),
                            spacing="4",
                            align="start",
                        ),
                        padding="6",
                        border="2px solid var(--amber-8)",
                        background="rgba(245, 158, 11, 0.03)",
                    ),
                    columns=rx.breakpoints(initial="1", sm="2"),
                    spacing="6",
                    width="100%",
                    max_width="850px",
                ),
                # GARANTIA 7 DIAS
                rx.card(
                    rx.hstack(
                        rx.text("🛡️", size="6"),
                        rx.vstack(
                            rx.heading("Garantia Incondicional de 7 Dias", size="3"),
                            rx.text(
                                "Experimente o Metanoia por 7 dias. Se você não sentir sua vida espiritual mais organizada e com mais paz, devolvemos 100% do seu dinheiro na hora. Sem perguntas.",
                                size="2",
                                color="gray.400",
                            ),
                            spacing="1",
                        ),
                        spacing="4",
                        align="center",
                    ),
                    max_width="750px",
                    width="100%",
                    padding="5",
                    margin_top="4",
                ),
                spacing="6",
                align="center",
                padding_y="12",
            ),
            max_width="950px",
        ),
        footer(),
        min_height="100vh",
        background="var(--gray-1)",
    )


# ==============================================================================
# INICIALIZAÇÃO DA APLICAÇÃO REFLEX
# ==============================================================================

app = rx.App(
    theme=rx.theme(
        appearance="dark",
        accent_color="amber",
        gray_color="slate",
        radius="large",
    )
)

app.add_page(index, route="/", title="Metanoia // O Copiloto da Vida Cristã")
app.add_page(cadastro_page, route="/cadastro", title="Criar Conta // Metanoia")
app.add_page(checkout_page, route="/checkout", title="Planos de Assinatura // Metanoia")
