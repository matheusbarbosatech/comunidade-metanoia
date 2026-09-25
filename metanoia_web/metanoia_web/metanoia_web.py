"""Comunidade Metanoia // Plataforma Web Oficial em Reflex (100% Python Puro).
"Ninguém luta sozinho" - Mural de Oração em Tempo Real, Escola Bíblica, SOS Madrugada e Louvores 24h.
"""
import reflex as rx
import sqlite3
from pathlib import Path
from rxconfig import config

DB_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "ministerio.db"

class MetanoiaState(rx.State):
    """Estado Reativo Global da Comunidade Metanoia (100% Python)."""
    nome: str = ""
    motivo: str = ""
    anonimo: bool = False
    intercessoes_hoje: int = 154
    orou_agora: bool = False
    pedidos_recentes: list[dict[str, str]] = [
        {"nome": "Irmão em crise", "motivo": "Ansiedade no trabalho e medo do futuro. Preciso de paz.", "intercessoes": "18"},
        {"nome": "Anônimo", "motivo": "Família passando por desentendimento e cansaço emocional.", "intercessoes": "24"},
        {"nome": "Membro da Célula", "motivo": "Agradecimento pela cura e renovo espiritual nesta semana.", "intercessoes": "31"},
    ]
    louvor_tocando: bool = True
    faixa_atual: str = "Bondade de Deus // Isaías Saad"

    def enviar_pedido_oracao(self):
        """Salva o pedido de oração direto no SQLite e atualiza a tela na hora."""
        if not self.motivo.strip():
            return rx.toast.error("Por favor, digite seu desabafo ou motivo de oração.")

        nome_final = "Anônimo" if self.anonimo or not self.nome.strip() else self.nome.strip()

        # Salvar no banco SQLite se existir
        if DB_PATH.exists():
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO pedidos_oracao (nome_solicitante, motivo, anonimo, status)
                VALUES (?, ?, ?, 'em_oracao')
                """, (nome_final, self.motivo, 1 if self.anonimo else 0))
                conn.commit()
                conn.close()
            except Exception as e:
                print(f"[Aviso DB] {e}")

        # Atualizar estado na tela
        self.pedidos_recentes.insert(0, {
            "nome": nome_final,
            "motivo": self.motivo,
            "intercessoes": "1"
        })
        self.intercessoes_hoje += 1
        self.orou_agora = True
        self.motivo = ""
        self.nome = ""

        return rx.toast.success("Seu pedido foi recebido. Nossa comunidade já está intercedendo por você!")

    def interceder(self, index: int):
        """Ação de orar por um irmão em 1 clique."""
        try:
            atual = int(self.pedidos_recentes[index]["intercessoes"])
            self.pedidos_recentes[index]["intercessoes"] = str(atual + 1)
            self.intercessoes_hoje += 1
            return rx.toast("🤍 Você orou por este irmão! Deus ouviu seu clamor.")
        except Exception:
            pass

    def toggle_louvor(self):
        self.louvor_tocando = not self.louvor_tocando


def navbar() -> rx.Component:
    """Barra de navegação da Comunidade Metanoia."""
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.heading("Comunidade Metanoia", size="5", weight="bold", color_scheme="amber"),
                rx.badge("Ninguém luta sozinho", variant="soft", color_scheme="amber", size="2"),
                spacing="3",
                align="center",
            ),
            rx.hstack(
                rx.link(rx.text("🕊️ Mural de Oração", size="2", weight="medium"), href="#oracao"),
                rx.link(rx.text("📖 Escola Bíblica", size="2", weight="medium"), href="#escola"),
                rx.link(rx.text("🌿 SOS Madrugada", size="2", weight="medium"), href="#sos"),
                rx.link(rx.text("🎶 Louvores 24h", size="2", weight="medium"), href="#louvores"),
                rx.color_mode.button(),
                spacing="5",
                align="center",
            ),
            justify="between",
            align="center",
            width="100%",
            padding_x="6",
            padding_y="4",
        ),
        background="rgba(11, 14, 23, 0.85)",
        backdrop_filter="blur(12px)",
        border_bottom="1px solid var(--gray-4)",
        position="sticky",
        top="0",
        z_index="50",
    )


def hero_section() -> rx.Component:
    """Seção de Acolhimento Fraterno."""
    return rx.vstack(
        rx.badge("🤍 Refúgio e Comunhão em Cristo", variant="surface", color_scheme="amber", size="3"),
        rx.heading(
            "Você Não Precisa Vencer Suas Batalhas Sozinho",
            size="9",
            text_align="center",
            max_width="850px",
            line_height="1.2",
        ),
        rx.text(
            "Um ministério digital acolhedor focado em cura emocional, comunhão de irmãos, louvores contínuos e formação bíblica sólida para transformar sua mente pela Palavra de Deus.",
            size="4",
            color="gray.400",
            text_align="center",
            max_width="680px",
        ),
        rx.hstack(
            rx.link(
                rx.button(
                    "🙏 Fazer um Pedido de Oração",
                    color_scheme="amber",
                    size="3",
                    radius="full",
                    variant="solid",
                ),
                href="#oracao",
            ),
            rx.link(
                rx.button(
                    "📖 Acessar Escola Bíblica",
                    variant="soft",
                    color_scheme="gray",
                    size="3",
                    radius="full",
                ),
                href="#escola",
            ),
            spacing="4",
            margin_top="3",
        ),
        spacing="5",
        align="center",
        padding_y="16",
        padding_x="4",
    )


def mural_oracao_section() -> rx.Component:
    """Mural de Oração Reativo em 100% Python."""
    return rx.vstack(
        rx.vstack(
            rx.badge("🕊️ Intercessão Comunitária", color_scheme="amber", variant="soft"),
            rx.heading("Mural de Oração da Célula Digital", size="7"),
            rx.text(
                "Desabafe o que está pesando no seu coração. Nossa comunidade se reúne em espírito para orar por você.",
                color="gray.400",
                text_align="center",
            ),
            spacing="2",
            align="center",
        ),
        # Formulário de Envio
        rx.card(
            rx.vstack(
                rx.input(
                    placeholder="Seu nome (ou deixe em branco para anônimo)",
                    value=MetanoiaState.nome,
                    on_change=MetanoiaState.set_nome,
                    width="100%",
                ),
                rx.text_area(
                    placeholder="Escreva seu motivo de oração ou desabafo...",
                    value=MetanoiaState.motivo,
                    on_change=MetanoiaState.set_motivo,
                    width="100%",
                    min_height="100px",
                ),
                rx.hstack(
                    rx.checkbox(
                        "Publicar como Anônimo",
                        checked=MetanoiaState.anonimo,
                        on_change=MetanoiaState.set_anonimo,
                    ),
                    rx.button(
                        "🕊️ Enviar Clamor",
                        on_click=MetanoiaState.enviar_pedido_oracao,
                        color_scheme="amber",
                        radius="full",
                    ),
                    justify="between",
                    width="100%",
                    align="center",
                ),
                spacing="4",
            ),
            width="100%",
            max_width="650px",
            padding="6",
        ),
        # Contador Geral
        rx.badge(
            f"🤍 {MetanoiaState.intercessoes_hoje} orações levantadas hoje",
            color_scheme="green",
            variant="soft",
            size="3",
        ),
        spacing="6",
        align="center",
        padding_y="12",
        id="oracao",
        width="100%",
    )


def escola_biblica_section() -> rx.Component:
    """Trilhas Teológicas da Escola Bíblica Metanoia."""
    trilhas = [
        {"titulo": "1. Bibliologia & Cânon", "desc": "Como a Bíblia foi formada, manuscritos antigos e as línguas originais.", "aulas": "51 páginas"},
        {"titulo": "2. Teologia da Graça", "desc": "Soteriologia aplicada: o amor incondicional de Deus que cura a ansiedade.", "aulas": "Módulo Central"},
        {"titulo": "3. Livros Poéticos & Salmos", "desc": "Como os homens de Deus lidavam com o medo, depressão e desabafos.", "aulas": "Estudo Prático"},
        {"titulo": "4. Os Evangelhos", "desc": "A vida de Jesus Cristo, Suas parábolas e o modelo perfeito de discipulado.", "aulas": "Fundamento"},
        {"titulo": "5. Epístolas Paulinas", "desc": "As cartas de Paulo: mente renovada (Metanoia), fé e liberdade em Cristo.", "aulas": "Doutrina Viva"},
    ]

    cards = [
        rx.card(
            rx.vstack(
                rx.badge("Academia Teológica", color_scheme="amber", size="1"),
                rx.heading(t["titulo"], size="4"),
                rx.text(t["desc"], size="2", color="gray.400"),
                rx.hstack(
                    rx.text(f"📖 {t['aulas']}", size="1", color="gray.500"),
                    rx.button("Ler Estudo ➔", size="1", variant="ghost", color_scheme="amber"),
                    justify="between",
                    width="100%",
                    align="center",
                ),
                spacing="3",
            ),
            width="100%",
        )
        for t in trilhas
    ]

    return rx.vstack(
        rx.vstack(
            rx.badge("📖 Formação Bíblica Sólida", color_scheme="amber", variant="soft"),
            rx.heading("Escola Bíblica Metanoia", size="7"),
            rx.text("Aprofunde suas raízes nas Escrituras com os 13 módulos completos de teologia.", color="gray.400"),
            spacing="2",
            align="center",
        ),
        rx.grid(
            *cards,
            columns=rx.breakpoints(initial="1", sm="2", lg="3"),
            spacing="4",
            width="100%",
            max_width="1100px",
        ),
        spacing="6",
        align="center",
        padding_y="12",
        id="escola",
        width="100%",
    )


def sos_madrugada_section() -> rx.Component:
    """Área SOS Madrugada com respiração guiada e acolhimento."""
    return rx.card(
        rx.vstack(
            rx.badge("🌿 SOS Madrugada", color_scheme="teal", size="2"),
            rx.heading("Momento de Paz: Acalme Sua Mente", size="6"),
            rx.text(
                "\"Vinde a mim, todos os que estais cansados e sobrecarregados, e eu vos aliviarei.\" (Mateus 11:28)",
                font_style="italic",
                color="amber.300",
                text_align="center",
            ),
            rx.box(
                rx.text("Puxe o ar... segure... solte devagar...", color="gray.300", size="3"),
                padding="8",
                border_radius="full",
                border="2px dashed var(--teal-7)",
                background="rgba(20, 184, 166, 0.08)",
                text_align="center",
            ),
            spacing="4",
            align="center",
        ),
        max_width="700px",
        margin_x="auto",
        margin_y="8",
        id="sos",
    )


def index() -> rx.Component:
    """Página Principal da Comunidade Metanoia em Reflex."""
    return rx.box(
        navbar(),
        rx.container(
            hero_section(),
            sos_madrugada_section(),
            mural_oracao_section(),
            escola_biblica_section(),
            max_width="1200px",
        ),
        rx.box(
            rx.text(
                "Comunidade Metanoia // \"Ninguém luta sozinho\" • 100% Python • Todos os direitos reservados à Graça de Deus.",
                size="2",
                color="gray.500",
                text_align="center",
            ),
            padding="8",
            border_top="1px solid var(--gray-4)",
            margin_top="16",
        ),
        min_height="100vh",
        background="var(--gray-1)",
    )


app = rx.App(
    theme=rx.theme(
        appearance="dark",
        accent_color="amber",
        gray_color="slate",
        radius="large",
    )
)
app.add_page(index, title="Comunidade Metanoia // Ninguém Luta Sozinho")
