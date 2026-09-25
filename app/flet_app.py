import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import flet as ft

# Camada de Compatibilidade Universal Flet (0.8x, 0.86+ e 1.0+)
def _make_compatible_button(orig_cls):
    if orig_cls is None:
        return object
    class CompatibleButton(orig_cls):
        def __init__(self, *args, **kwargs):
            text_val = kwargs.pop("text", None)
            if text_val is not None and "content" not in kwargs:
                kwargs["content"] = text_val
            super().__init__(*args, **kwargs)

        @property
        def text(self):
            if isinstance(self.content, str):
                return self.content
            elif hasattr(self.content, "value"):
                return self.content.value
            return ""

        @text.setter
        def text(self, val):
            if isinstance(self.content, str) or self.content is None:
                self.content = val
            elif hasattr(self.content, "value"):
                self.content.value = str(val)
            else:
                self.content = val

    return CompatibleButton

ft.ElevatedButton = _make_compatible_button(getattr(ft, "ElevatedButton", None) or getattr(ft, "Button", object))
ft.FilledButton = _make_compatible_button(getattr(ft, "FilledButton", None) or getattr(ft, "Button", object))
ft.OutlinedButton = _make_compatible_button(getattr(ft, "OutlinedButton", None) or getattr(ft, "Button", object))
ft.TextButton = _make_compatible_button(getattr(ft, "TextButton", None) or getattr(ft, "Button", object))

# Compatibilidade para Border, Padding e Margin minúsculos vs maiúsculos
if hasattr(ft, "Border"):
    ft.border.only = ft.Border.only
    ft.border.all = ft.Border.all
    ft.border.symmetric = ft.Border.symmetric

if hasattr(ft, "Padding"):
    ft.padding.all = ft.Padding.all
    ft.padding.only = ft.Padding.only
    ft.padding.symmetric = ft.Padding.symmetric

if hasattr(ft, "Margin"):
    ft.margin.all = ft.Margin.all
    ft.margin.only = ft.Margin.only
    ft.margin.symmetric = ft.Margin.symmetric

if hasattr(ft, "Alignment"):
    ft.alignment.center = getattr(ft.Alignment, "CENTER", ft.alignment.Alignment(0, 0))
    ft.alignment.top_left = getattr(ft.Alignment, "TOP_LEFT", ft.alignment.Alignment(-1, -1))
    ft.alignment.top_center = getattr(ft.Alignment, "TOP_CENTER", ft.alignment.Alignment(0, -1))
    ft.alignment.top_right = getattr(ft.Alignment, "TOP_RIGHT", ft.alignment.Alignment(1, -1))
    ft.alignment.bottom_left = getattr(ft.Alignment, "BOTTOM_LEFT", ft.alignment.Alignment(-1, 1))
    ft.alignment.bottom_center = getattr(ft.Alignment, "BOTTOM_CENTER", ft.alignment.Alignment(0, 1))
    ft.alignment.bottom_right = getattr(ft.Alignment, "BOTTOM_RIGHT", ft.alignment.Alignment(1, 1))
    ft.alignment.center_left = getattr(ft.Alignment, "CENTER_LEFT", ft.alignment.Alignment(-1, 0))
    ft.alignment.center_right = getattr(ft.Alignment, "CENTER_RIGHT", ft.alignment.Alignment(1, 0))

# Compatibilidade para ft.Page.dialog e ft.Page.show_snack_bar
if not hasattr(ft.Page, "dialog"):
    def _get_page_dialog(self):
        dialogs = getattr(self, "_dialogs", None)
        if dialogs and hasattr(dialogs, "controls"):
            return next((dlg for dlg in reversed(dialogs.controls) if getattr(dlg, "open", False)), None)
        return getattr(self, "_active_dialog", None)

    def _set_page_dialog(self, dlg):
        self._active_dialog = dlg
        if dlg:
            if hasattr(self, "show_dialog"):
                try:
                    self.show_dialog(dlg)
                except Exception:
                    pass
            elif hasattr(self, "overlay"):
                if dlg not in self.overlay:
                    self.overlay.append(dlg)
                dlg.open = True
                self.update()

    ft.Page.dialog = property(_get_page_dialog, _set_page_dialog)

if not hasattr(ft.Page, "show_snack_bar"):
    def _show_snack_bar(self, snack_bar):
        if hasattr(self, "overlay"):
            if snack_bar not in self.overlay:
                self.overlay.append(snack_bar)
            snack_bar.open = True
            self.update()
        elif hasattr(self, "snack_bar"):
            self.snack_bar = snack_bar
            self.snack_bar.open = True
            self.update()

    ft.Page.show_snack_bar = _show_snack_bar

from app.db.database import get_connection
from app.services import comunidade_service
from app.services.music_service import (
    get_all_musicas,
    get_musicas_stats,
    toggle_favorito,
    increment_play_count
)

# Paleta Dark Obsidian & Ouro Imperial
COLOR_BG = "#08080A"
COLOR_CARD = "#121217"
COLOR_CARD_HOVER = "#1A1A23"
COLOR_ACCENT = "#F59E0B"
COLOR_FLAME = "#EA580C"
COLOR_BORDER = "#272732"
COLOR_TEXT = "#F8FAFC"
COLOR_MUTED = "#94A3B8"

def main(page: ft.Page):
    page.title = "Comunidade Metanoia // Ninguém Luta Sozinho"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = COLOR_BG
    page.padding = 0

    # Estado da Aplicação
    estado = {
        "usuario_role": "admin", # "admin" (Pastor) ou "aluno" (Discípulo)
        "aba_atual": "comunidade", # Comunidade Circle como espaço principal
        "resumo_selecionado": None,
        "filtro_musica_cat": "Todos",
        "busca_musica": "",
        "espaco_comunidade_id": None,
        "busca_comunidade": ""
    }

    # Container dinâmico central
    conteudo_view = ft.Container(expand=True, padding=24)

    def alternar_papel(e):
        estado["usuario_role"] = "aluno" if estado["usuario_role"] == "admin" else "admin"
        btn_role.text = f"Modo: {'👑 Liderança (ADM)' if estado['usuario_role'] == 'admin' else '🐑 Discípulo (Aluno)'}"
        btn_role.update()
        atualizar_tela()

    btn_role = ft.ElevatedButton(
        text="Modo: 👑 Liderança (ADM)",
        bgcolor=COLOR_CARD,
        color=COLOR_ACCENT,
        on_click=alternar_papel
    )

    # --- TELAS DO PAINEL DO PASTOR (ADMIN) ---

    def render_admin_estudos():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM estudos_aulas ORDER BY id ASC")
        aulas = cursor.fetchall()
        conn.close()

        cards_aulas = []
        for aula in aulas:
            titulo = aula["titulo"]
            resumo = aula["resumo_conteudo"] or "Clique para ver os tópicos da apostila."

            cards_aulas.append(
                ft.Container(
                    bgcolor=COLOR_CARD,
                    border=ft.border.all(1, COLOR_BORDER),
                    border_radius=12,
                    padding=16,
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.BOOK_ROUNDED, color=COLOR_ACCENT, size=24),
                            ft.Text(titulo, size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT, expand=True),
                            ft.Container(
                                bgcolor="#1E293B",
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=6,
                                content=ft.Text(aula["status_estudo"].upper(), size=10, color=COLOR_ACCENT, weight=ft.FontWeight.BOLD)
                            )
                        ]),
                        ft.Text(resumo[:160] + "...", size=13, color=COLOR_MUTED),
                        ft.Row([
                            ft.ElevatedButton(
                                "📖 Ver Resumo & Tópicos",
                                bgcolor="#2A2A38",
                                color=COLOR_TEXT,
                                on_click=lambda e, a=aula: abrir_detalhe_aula(a)
                            ),
                            ft.OutlinedButton(
                                "🎬 Gravar Vídeo do YouTube",
                                style=ft.ButtonStyle(color=COLOR_ACCENT),
                                on_click=lambda e, t=titulo: page.show_snack_bar(ft.SnackBar(ft.Text(f"Roteiro de '{t}' aberto para gravação!")))
                            )
                        ], alignment=ft.MainAxisAlignment.END)
                    ], spacing=10)
                )
            )

        return ft.Column([
            ft.Row([
                ft.Text("📚 Minhas Apostilas & Estudos (Academia de Pregadores)", size=22, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                ft.Container(
                    bgcolor=COLOR_CARD,
                    border_radius=8,
                    padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    content=ft.Text(f"{len(aulas)} Apostilas Estudadas", color=COLOR_ACCENT, weight=ft.FontWeight.BOLD)
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text("Todo o seu acervo teológico estudado pelo robô, pronto para gravação de vídeos longos e aulas.", size=14, color=COLOR_MUTED),
            ft.Divider(color=COLOR_BORDER),
            ft.ListView(controls=cards_aulas, spacing=16, expand=True)
        ], expand=True, spacing=12)

    def abrir_detalhe_aula(aula):
        def fechar(e=None):
            if hasattr(page, "pop_dialog"):
                page.pop_dialog()
            else:
                dialog.open = False
                page.update()

        dialog = ft.AlertDialog(
            title=ft.Text(aula["titulo"], color=COLOR_ACCENT, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=600,
                height=450,
                content=ft.ListView([
                    ft.Markdown(aula["resumo_conteudo"] or "Sem resumo disponível.")
                ])
            ),
            actions=[
                ft.TextButton("Fechar", on_click=fechar)
            ]
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def render_admin_oracoes():
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pedidos_oracao ORDER BY id DESC")
        pedidos = cursor.fetchall()
        conn.close()

        lista_pedidos = []
        if not pedidos:
            lista_pedidos.append(ft.Text("Nenhum pedido de oração pendente no momento.", color=COLOR_MUTED))
        else:
            for p in pedidos:
                nome = "Irmão Anônimo" if p["anonimo"] else p["nome_solicitante"]
                lista_pedidos.append(
                    ft.Container(
                        bgcolor=COLOR_CARD,
                        border=ft.border.all(1, COLOR_BORDER),
                        border_radius=10,
                        padding=16,
                        content=ft.Row([
                            ft.Icon(ft.Icons.FAVORITE_ROUNDED, color=COLOR_FLAME, size=28),
                            ft.Column([
                                ft.Text(f"Pedido de: {nome}", size=15, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                                ft.Text(p["motivo"], size=13, color=COLOR_MUTED),
                                ft.Text(f"Intercessões recebidas: {p['intercessoes_count']} irmãos orando", size=11, color=COLOR_ACCENT)
                            ], expand=True),
                            ft.ElevatedButton(
                                "Orar Agora",
                                bgcolor="#1E293B",
                                color=COLOR_TEXT,
                                on_click=lambda e, pid=p["id"]: registrar_intercessao(pid)
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    )
                )

        return ft.Column([
            ft.Text("🛡️ Mural Pastoral de Intercessão", size=22, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
            ft.Text("Pedidos de oração enviados pelas ovelhas da Célula e espectadores do YouTube.", size=14, color=COLOR_MUTED),
            ft.Divider(color=COLOR_BORDER),
            ft.ListView(controls=lista_pedidos, spacing=12, expand=True)
        ], expand=True, spacing=12)

    # --- TELAS DO PAINEL DO DISCÍPULO (ALUNO) ---

    def render_aluno_home():
        return ft.Column([
            ft.Container(
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_left,
                    end=ft.alignment.bottom_right,
                    colors=["#1E2235", "#10131E"]
                ),
                border=ft.border.all(1, "rgba(245, 158, 11, 0.25)"),
                border_radius=16,
                padding=24,
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.VOLUNTEER_ACTIVISM_ROUNDED, color=COLOR_ACCENT, size=32),
                        ft.Text("UM REFÚGIO SEGURO PARA A SUA ALMA", size=18, weight=ft.FontWeight.BOLD, color=COLOR_TEXT)
                    ]),
                    ft.Text('"Perto está o Senhor dos que têm o coração quebrantado e salva os de espírito abatido." — Salmo 34:18', size=14, italic=True, color=COLOR_ACCENT),
                    ft.Text("Se hoje você só consegue chorar, se o desespero do desemprego, a angústia da depressão ou o peso da ansiedade tiraram o seu chão... você não precisa fingir força aqui. Deus se apresenta a você hoje não como um juiz, mas como um Pai amoroso que te abraça em silêncio.", size=14, color=COLOR_TEXT),
                    ft.Row([
                        ft.ElevatedButton("🤍 Só Preciso de um Abraço e Oração", bgcolor=COLOR_FLAME, color=COLOR_TEXT, on_click=lambda e: abrir_modal_desabafo()),
                        ft.OutlinedButton("🎧 Áudio de Alívio e Paz (3 min)", style=ft.ButtonStyle(color=COLOR_ACCENT), on_click=lambda e: tocar_audio_alivio())
                    ], spacing=12)
                ], spacing=14)
            ),
            ft.Row([
                ft.Container(
                    expand=True,
                    bgcolor=COLOR_CARD,
                    border=ft.border.all(1, COLOR_BORDER),
                    border_radius=14,
                    padding=20,
                    content=ft.Column([
                        ft.Icon(ft.Icons.PEOPLE_ALT_ROUNDED, color=COLOR_ACCENT, size=28),
                        ft.Text("Célula Digital (Hospital de Almas)", size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                        ft.Text("Encontro ao vivo semanal. Você não precisa abrir a câmera nem falar se faltarem forças. Apenas ouça e receba oração.", size=13, color=COLOR_MUTED),
                        ft.ElevatedButton("Entrar na Sala Google Meet", bgcolor="#1E293B", color=COLOR_TEXT, url="https://meet.google.com")
                    ], spacing=10)
                ),
                ft.Container(
                    expand=True,
                    bgcolor=COLOR_CARD,
                    border=ft.border.all(1, "#DC2626"),
                    border_radius=14,
                    padding=20,
                    content=ft.Column([
                        ft.Icon(ft.Icons.FAVORITE_ROUNDED, color="#EF4444", size=28),
                        ft.Text("Socorro Imediato (Ansiedade / Desespero)", size=16, weight=ft.FontWeight.BOLD, color="#EF4444"),
                        ft.Text("O peito está apertado ou pensamentos de desistir da vida? Clique agora.", size=13, color=COLOR_MUTED),
                        ft.ElevatedButton(
                            "Receber Socorro e Oração",
                            bgcolor="#7F1D1D",
                            color=COLOR_TEXT,
                            on_click=lambda e: abrir_modal_sos()
                        )
                    ], spacing=10)
                )
            ], spacing=16)
        ], spacing=20, expand=True)

    def abrir_modal_desabafo():
        campo_nome = ft.TextField(label="Seu Nome ou 'Anônimo'", bgcolor="#1E293B", border_color=COLOR_BORDER)
        campo_desabafo = ft.TextField(label="Como está o seu coração hoje? (Desabafe)", multiline=True, min_lines=3, bgcolor="#1E293B", border_color=COLOR_BORDER)

        def fechar(e=None):
            if hasattr(page, "pop_dialog"):
                page.pop_dialog()
            else:
                dialog.open = False
                page.update()

        def enviar_desabafo(e):
            if campo_desabafo.value:
                conn = get_connection()
                conn.execute("""
                INSERT INTO pedidos_oracao (nome_solicitante, motivo, categoria, anonimo)
                VALUES (?, ?, 'desabafo_acolhimento', ?)
                """, (campo_nome.value or "Alguém que precisa de um abraço", campo_desabafo.value, 1 if not campo_nome.value else 0))
                conn.commit()
                conn.close()
                fechar()
                page.show_snack_bar(ft.SnackBar(ft.Text("Seu desabafo foi acolhido. Nossa equipe e grupo de oração já estão intercedendo por você!")))

        dialog = ft.AlertDialog(
            title=ft.Text("🤍 Você Não Está Sozinho", color=COLOR_ACCENT, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=500,
                height=300,
                content=ft.Column([
                    ft.Text("Coloque aqui o peso que está no seu peito. Ninguém vai te julgar. Vamos levar sua causa diante do Pai.", size=13, color=COLOR_MUTED),
                    campo_nome,
                    campo_desabafo
                ], spacing=12)
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: fechar()),
                ft.ElevatedButton("Entregar nas Mãos de Deus", bgcolor=COLOR_FLAME, color=COLOR_TEXT, on_click=enviar_desabafo)
            ]
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def abrir_modal_sos():
        def fechar(e=None):
            if hasattr(page, "pop_dialog"):
                page.pop_dialog()
            else:
                dialog.open = False
                page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("🕊️ PARE POR UM SEGUNDO. DEUS ESTÁ AQUI.", color=COLOR_ACCENT, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=500,
                height=320,
                content=ft.Column([
                    ft.Text("1. Respire fundo devagar: puxe o ar em 4 segundos, segure 4 segundos e solte em 6 segundos.", color=COLOR_TEXT),
                    ft.Text("2. Coloque a mão no seu peito. O seu coração está batendo porque Deus ainda tem um propósito sagrado com a sua história.", color=COLOR_TEXT, weight=ft.FontWeight.BOLD),
                    ft.Text('"Não temas, porque eu sou contigo; não te assombres, porque eu sou o teu Deus; eu te fortaleço, e te ajudo, e te sustento com a destra da minha justiça." — Isaías 41:10', color=COLOR_ACCENT, italic=True),
                    ft.Text("3. Se o desespero estiver extremo ou pensamentos de morte vierem, lembre-se: a sua dor tem cura. Ligue gratuitamente para o 188 (CVV) e nos mande uma mensagem. Nós amamos a sua vida!", color="#FDA4AF", size=13),
                    ft.Text("Você vai sair desse vale. Essa noite escura não é o fim da sua história!", color=COLOR_TEXT)
                ], spacing=14)
            ),
            actions=[ft.ElevatedButton("Recebi esse Abraço de Paz", bgcolor=COLOR_FLAME, color=COLOR_TEXT, on_click=fechar)]
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def registrar_intercessao(pid):
        conn = get_connection()
        conn.execute("UPDATE pedidos_oracao SET intercessoes_count = intercessoes_count + 1 WHERE id = ?", (pid,))
        conn.commit()
        conn.close()
        page.show_snack_bar(ft.SnackBar(ft.Text("Oração registrada! Deus ouve o clamor dos santos.")))
        atualizar_tela()

    # --- SEÇÃO MÚSICA & LOUVOR (PLAYLIST MATHEUS) ---

    def tocar_faixa_audio(musica):
        increment_play_count(musica["id"])
        caminho = musica["caminho_completo"]
        if os.path.exists(caminho):
            try:
                os.startfile(caminho)
                page.show_snack_bar(ft.SnackBar(ft.Text(f"🎶 Tocando: {musica['titulo']} — {musica['artista']}")))
            except Exception:
                stream_url = musica.get("cdn_url") or f"/api/v1/musicas/{musica['id']}/stream"
                page.launch_url(stream_url)
        else:
            stream_url = musica.get("cdn_url") or f"/api/v1/musicas/{musica['id']}/stream"
            page.launch_url(stream_url)

    def tocar_audio_alivio():
        musicas_oracao = get_all_musicas(categoria="Oração & Adoração")
        if musicas_oracao:
            faixa = musicas_oracao[0]
            tocar_faixa_audio(faixa)
            page.show_snack_bar(ft.SnackBar(ft.Text(f"🕊️ Louvor de Alívio e Oração iniciado: '{faixa['titulo']}'. Respire em paz.")))
        else:
            page.show_snack_bar(ft.SnackBar(ft.Text("Iniciando momento devocional de oração...")))

    def render_louvores():
        stats = get_musicas_stats()
        musicas = get_all_musicas(
            categoria=estado.get("filtro_musica_cat"),
            busca=estado.get("busca_musica")
        )

        def filtrar_cat(cat):
            estado["filtro_musica_cat"] = cat
            atualizar_tela()

        def on_busca_submit(e):
            estado["busca_musica"] = e.control.value
            atualizar_tela()

        def toggle_fav(m):
            novo = toggle_favorito(m["id"])
            page.show_snack_bar(ft.SnackBar(ft.Text(f"{'⭐ Adicionado aos favoritos' if novo else 'Removido dos favoritos'}: {m['titulo']}")))
            atualizar_tela()

        def usar_na_celula(m):
            page.show_snack_bar(ft.SnackBar(ft.Text(f"🕊️ Louvor selecionado para a Célula Digital: '{m['titulo']}'!")))

        categorias = [
            "Todos",
            "Oração & Adoração",
            "Guerra Espiritual & Fé",
            "Trap Gospel & Edificação",
            "Graça & Restauração",
            "Pentecostal & Celebração"
        ]
        botoes_cat = []
        for c in categorias:
            selecionado = (estado.get("filtro_musica_cat", "Todos") == c)
            botoes_cat.append(
                ft.ElevatedButton(
                    c,
                    bgcolor=COLOR_ACCENT if selecionado else COLOR_CARD,
                    color="#000" if selecionado else COLOR_TEXT,
                    on_click=lambda e, cat=c: filtrar_cat(cat)
                )
            )

        cards_musicas = []
        if not musicas:
            cards_musicas.append(ft.Text("Nenhuma música encontrada para os filtros selecionados.", color=COLOR_MUTED))
        else:
            for m in musicas:
                cor_cat = "#38BDF8" if "Oração" in m["categoria"] else (
                    "#F59E0B" if "Guerra" in m["categoria"] else (
                        "#10B981" if "Graça" in m["categoria"] else (
                            "#A855F7" if "Trap" in m["categoria"] else COLOR_FLAME
                        )
                    )
                )
                icone = ft.Icons.VOLUNTEER_ACTIVISM_ROUNDED if "Oração" in m["categoria"] else (
                    ft.Icons.SHIELD_ROUNDED if "Guerra" in m["categoria"] else (
                        ft.Icons.FAVORITE_ROUNDED if "Graça" in m["categoria"] else ft.Icons.GRAPHIC_EQ_ROUNDED
                    )
                )

                cards_musicas.append(
                    ft.Container(
                        bgcolor=COLOR_CARD,
                        border=ft.border.all(1, COLOR_BORDER),
                        border_radius=12,
                        padding=16,
                        content=ft.Row([
                            ft.Icon(icone, color=cor_cat, size=30),
                            ft.Column([
                                ft.Row([
                                    ft.Text(m["titulo"], size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                                    ft.Container(
                                        bgcolor="#1E293B",
                                        padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                        border_radius=6,
                                        content=ft.Text(m["categoria"], size=11, color=cor_cat, weight=ft.FontWeight.BOLD)
                                    )
                                ], spacing=10),
                                ft.Text(f"👤 {m['artista']} • 💾 {m['tamanho_mb']} MB • 🏷️ {m['tags']}", size=12, color=COLOR_MUTED)
                            ], expand=True, spacing=4),
                            ft.Row([
                                ft.IconButton(
                                    ft.Icons.STAR_ROUNDED if m["favorito"] else ft.Icons.STAR_BORDER_ROUNDED,
                                    icon_color=COLOR_ACCENT if m["favorito"] else COLOR_MUTED,
                                    tooltip="Favoritar",
                                    on_click=lambda e, musica=m: toggle_fav(musica)
                                ),
                                ft.ElevatedButton(
                                    "🕊️ Célula",
                                    bgcolor="#1E293B",
                                    color=COLOR_TEXT,
                                    tooltip="Definir para o Louvor da Célula",
                                    on_click=lambda e, musica=m: usar_na_celula(musica)
                                ),
                                ft.ElevatedButton(
                                    "▶️ Tocar",
                                    bgcolor=COLOR_FLAME,
                                    color=COLOR_TEXT,
                                    on_click=lambda e, musica=m: tocar_faixa_audio(musica)
                                )
                            ], spacing=8)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    )
                )

        campo_busca = ft.TextField(
            hint_text="Buscar por título, artista ou tema bíblico (ex: Hebreus, Davi, Oração)...",
            prefix_icon=ft.Icons.SEARCH_ROUNDED,
            bgcolor="#1E293B",
            border_color=COLOR_BORDER,
            value=estado.get("busca_musica", ""),
            on_submit=on_busca_submit,
            expand=True
        )

        return ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("🎶 Estação de Louvor & Adoração (Playlist Matheus)", size=22, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                    ft.Text("50 faixas catalogadas de Trap Gospel, Oração & Batalha Espiritual (2metro, Nesk Only e Adoração).", size=14, color=COLOR_MUTED)
                ], spacing=4),
                ft.Container(
                    bgcolor=COLOR_CARD,
                    border_radius=8,
                    padding=ft.padding.symmetric(horizontal=14, vertical=8),
                    content=ft.Row([
                        ft.Text(f"{stats['total_faixas']} Faixas", color=COLOR_ACCENT, weight=ft.FontWeight.BOLD),
                        ft.Text("•", color=COLOR_MUTED),
                        ft.Text(f"{stats['total_mb']} MB", color=COLOR_TEXT, size=12)
                    ], spacing=6)
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([campo_busca]),
            ft.Row(botoes_cat, scroll=ft.ScrollMode.AUTO),
            ft.Divider(color=COLOR_BORDER),
            ft.ListView(controls=cards_musicas, spacing=12, expand=True)
        ], expand=True, spacing=14)

    # --- REDE SOCIAL / COMUNIDADE (ESTILO CIRCLE.SO) ---

    def abrir_modal_novo_post():
        espacos = comunidade_service.get_espacos()
        options = [ft.dropdown.Option(key=str(e["id"]), text=f"{e['icone']} {e['nome']}") for e in espacos]
        dropdown_espaco = ft.Dropdown(
            label="Escolha o Canal / Espaço",
            options=options,
            value=str(espacos[0]["id"]) if espacos else "1",
            bgcolor="#1E293B",
            border_color=COLOR_BORDER
        )
        campo_titulo = ft.TextField(label="Título (Opcional)", bgcolor="#1E293B", border_color=COLOR_BORDER)
        campo_conteudo = ft.TextField(
            label="O que Deus colocou no seu coração? (Desabafo, Oração, Testemunho)",
            multiline=True,
            min_lines=4,
            bgcolor="#1E293B",
            border_color=COLOR_BORDER
        )
        campo_autor = ft.TextField(label="Seu Nome (ou deixe vazio para postar como Anônimo)", bgcolor="#1E293B", border_color=COLOR_BORDER)

        def fechar(e=None):
            if hasattr(page, "pop_dialog"):
                page.pop_dialog()
            else:
                dialog.open = False
                page.update()

        def salvar_post(e):
            if not campo_conteudo.value:
                return
            comunidade_service.criar_post(
                espaco_id=int(dropdown_espaco.value),
                autor_nome=campo_autor.value or "Discípulo Metanoia",
                titulo=campo_titulo.value or None,
                conteudo=campo_conteudo.value,
                autor_papel="👑 Pastor & Fundador" if estado["usuario_role"] == "admin" else "Discípulo",
                autor_avatar="👑" if estado["usuario_role"] == "admin" else "🕊️",
                anonimo=not bool(campo_autor.value)
            )
            fechar()
            page.show_snack_bar(ft.SnackBar(ft.Text("🎉 Publicação enviada com sucesso para a comunidade!")))
            atualizar_tela()

        dialog = ft.AlertDialog(
            title=ft.Text("✍️ Nova Publicação na Comunidade", color=COLOR_ACCENT, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=550,
                height=380,
                content=ft.Column([
                    dropdown_espaco,
                    campo_titulo,
                    campo_conteudo,
                    campo_autor
                ], spacing=10)
            ),
            actions=[
                ft.TextButton("Cancelar", on_click=fechar),
                ft.ElevatedButton("Publicar Agora", bgcolor=COLOR_FLAME, color=COLOR_TEXT, on_click=salvar_post)
            ]
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def abrir_modal_comentarios_post(post):
        detalhes = comunidade_service.get_post_com_detalhes(post["id"])
        comentarios = detalhes["comentarios"] if detalhes else []

        campo_comentario = ft.TextField(hint_text="Escreva uma palavra de bênção ou resposta...", bgcolor="#1E293B", border_color=COLOR_BORDER, expand=True)
        campo_autor_com = ft.TextField(hint_text="Seu nome (vazio = Anônimo)", bgcolor="#1E293B", border_color=COLOR_BORDER, width=170)

        lista_comentarios_controls = []
        if not comentarios:
            lista_comentarios_controls.append(ft.Text("Nenhum comentário ainda. Deixe a primeira resposta!", color=COLOR_MUTED, italic=True))
        else:
            for c in comentarios:
                lista_comentarios_controls.append(
                    ft.Container(
                        bgcolor="#1E293B",
                        border_radius=8,
                        padding=10,
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"{c['autor_avatar']} {c['autor_nome']}", size=12, weight=ft.FontWeight.BOLD, color=COLOR_ACCENT),
                                ft.Text(c['autor_papel'], size=10, color=COLOR_MUTED)
                            ], spacing=6),
                            ft.Text(c["conteudo"], size=13, color=COLOR_TEXT)
                        ], spacing=4)
                    )
                )

        def fechar(e=None):
            if hasattr(page, "pop_dialog"):
                page.pop_dialog()
            else:
                dialog.open = False
                page.update()

        def enviar_com(e):
            if not campo_comentario.value:
                return
            comunidade_service.adicionar_comentario(
                post_id=post["id"],
                autor_nome=campo_autor_com.value or "Discípulo",
                conteudo=campo_comentario.value,
                autor_papel="👑 Liderança" if estado["usuario_role"] == "admin" else "Membro",
                autor_avatar="👑" if estado["usuario_role"] == "admin" else "🕊️",
                anonimo=not bool(campo_autor_com.value)
            )
            fechar()
            page.show_snack_bar(ft.SnackBar(ft.Text("Comentário adicionado!")))
            atualizar_tela()

        dialog = ft.AlertDialog(
            title=ft.Text(f"💬 Comentários // {post.get('titulo') or post['espaco_nome']}", color=COLOR_ACCENT, weight=ft.FontWeight.BOLD, size=16),
            content=ft.Container(
                width=550,
                height=420,
                content=ft.Column([
                    ft.Container(
                        bgcolor="#121217",
                        padding=10,
                        border_radius=8,
                        content=ft.Text(post["conteudo"][:200] + ("..." if len(post["conteudo"]) > 200 else ""), size=12, color=COLOR_MUTED)
                    ),
                    ft.Divider(color=COLOR_BORDER),
                    ft.ListView(controls=lista_comentarios_controls, spacing=8, expand=True),
                    ft.Row([campo_autor_com, campo_comentario, ft.ElevatedButton("Enviar", bgcolor=COLOR_FLAME, color=COLOR_TEXT, on_click=enviar_com)], spacing=8)
                ], spacing=8)
            ),
            actions=[ft.TextButton("Fechar", on_click=fechar)]
        )
        page.dialog = dialog
        dialog.open = True
        page.update()

    def render_comunidade():
        espacos = comunidade_service.get_espacos()
        posts = comunidade_service.get_posts(
            espaco_id=estado.get("espaco_comunidade_id"),
            busca=estado.get("busca_comunidade")
        )

        def filtrar_espaco(esp_id):
            estado["espaco_comunidade_id"] = esp_id
            atualizar_tela()

        def buscar_comunidade(e):
            estado["busca_comunidade"] = e.control.value
            atualizar_tela()

        # Botões de Canais / Espaços (Pills estilo Circle)
        botoes_espacos = []
        is_todos = (estado.get("espaco_comunidade_id") is None)
        botoes_espacos.append(
            ft.ElevatedButton(
                "🌐 Todos os Espaços",
                bgcolor=COLOR_ACCENT if is_todos else COLOR_CARD,
                color="#000" if is_todos else COLOR_TEXT,
                on_click=lambda e: filtrar_espaco(None)
            )
        )
        for esp in espacos:
            ativo = (estado.get("espaco_comunidade_id") == esp["id"])
            botoes_espacos.append(
                ft.ElevatedButton(
                    f"{esp['icone']} {esp['nome']} ({esp['total_posts']})",
                    bgcolor=COLOR_ACCENT if ativo else COLOR_CARD,
                    color="#000" if ativo else COLOR_TEXT,
                    on_click=lambda e, sid=esp["id"]: filtrar_espaco(sid)
                )
            )

        cards_posts = []
        if not posts:
            cards_posts.append(
                ft.Container(
                    bgcolor=COLOR_CARD,
                    border=ft.border.all(1, COLOR_BORDER),
                    border_radius=12,
                    padding=32,
                    content=ft.Column([
                        ft.Icon(ft.Icons.FORUM_OUTLINED, size=40, color=COLOR_MUTED),
                        ft.Text("Nenhuma publicação neste canal ainda.", size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                        ft.Text("Seja o primeiro a compartilhar uma palavra, pedido de oração ou testemunho com os irmãos!", size=13, color=COLOR_MUTED),
                        ft.ElevatedButton("✍️ Escrever Primeira Publicação", bgcolor=COLOR_FLAME, color=COLOR_TEXT, on_click=lambda e: abrir_modal_novo_post())
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10)
                )
            )
        else:
            for p in posts:
                def on_reagir(pid=p["id"]):
                    comunidade_service.reagir_post(pid, tipo="orando")
                    page.show_snack_bar(ft.SnackBar(ft.Text("🤍 Oração registrada! Que Deus ouça o clamor dos santos.")))
                    atualizar_tela()

                pin_badge = ft.Container(
                    bgcolor="rgba(245, 158, 11, 0.15)",
                    padding=ft.padding.symmetric(horizontal=8, vertical=3),
                    border_radius=6,
                    content=ft.Text("📌 FIXADO", size=10, weight=ft.FontWeight.BOLD, color=COLOR_ACCENT)
                ) if p["fixado"] else ft.Container()

                elementos_post = [
                    ft.Row([
                        ft.Row([
                            ft.Container(
                                width=36, height=36, border_radius=18, bgcolor="#1E293B",
                                content=ft.Text(p["autor_avatar"] or "🕊️", size=18),
                                alignment=ft.alignment.center
                            ),
                            ft.Column([
                                ft.Row([
                                    ft.Text(p["autor_nome"], size=14, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                                    ft.Container(
                                        bgcolor="rgba(245, 158, 11, 0.12)",
                                        padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                        border_radius=4,
                                        content=ft.Text(p["autor_papel"] or "Discípulo", size=10, color=COLOR_ACCENT, weight=ft.FontWeight.BOLD)
                                    )
                                ], spacing=6),
                                ft.Text(f"{p['espaco_icone']} {p['espaco_nome']}", size=11, color=COLOR_MUTED)
                            ], spacing=2)
                        ], spacing=10),
                        pin_badge
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ]

                if p.get("titulo"):
                    elementos_post.append(ft.Text(p["titulo"], size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT))

                elementos_post.append(ft.Text(p["conteudo"], size=13.5, color="#CBD5E1"))

                elementos_post.append(
                    ft.Row([
                        ft.ElevatedButton(
                            f"🤍 Estou Orando ({p['likes_count']})",
                            bgcolor="#1E293B",
                            color=COLOR_TEXT,
                            on_click=lambda e, pid=p["id"]: on_reagir(pid)
                        ),
                        ft.ElevatedButton(
                            f"💬 Comentários ({p['comentarios_count']})",
                            bgcolor="#2A2A38",
                            color=COLOR_TEXT,
                            on_click=lambda e, post_obj=p: abrir_modal_comentarios_post(post_obj)
                        ),
                        ft.OutlinedButton(
                            "🌐 Abrir no Hub Web",
                            style=ft.ButtonStyle(color=COLOR_ACCENT),
                            on_click=lambda e, pid=p["id"]: page.launch_url(f"/comunidade#post-{pid}")
                        )
                    ], spacing=10)
                )

                cards_posts.append(
                    ft.Container(
                        bgcolor=COLOR_CARD,
                        border=ft.border.all(1, COLOR_BORDER),
                        border_radius=12,
                        padding=18,
                        content=ft.Column(elementos_post, spacing=10)
                    )
                )

        campo_busca_com = ft.TextField(
            hint_text="Buscar publicações, testemunhos ou reflexões da comunidade...",
            prefix_icon=ft.Icons.SEARCH_ROUNDED,
            bgcolor="#1E293B",
            border_color=COLOR_BORDER,
            value=estado.get("busca_comunidade", ""),
            on_submit=buscar_comunidade,
            expand=True
        )

        return ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("🌐 Rede Social // Comunidade Metanoia (Circle Hub)", size=22, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                    ft.Text("Espaços temáticos de convivência, partilha bíblica, intercessão e acolhimento.", size=14, color=COLOR_MUTED)
                ], spacing=4),
                ft.Row([
                    ft.ElevatedButton(
                        "✍️ Nova Publicação",
                        bgcolor=COLOR_FLAME,
                        color=COLOR_TEXT,
                        on_click=lambda e: abrir_modal_novo_post()
                    ),
                    ft.OutlinedButton(
                        "🌐 Abrir Portal Circle",
                        style=ft.ButtonStyle(color=COLOR_ACCENT),
                        on_click=lambda e: page.launch_url("/comunidade")
                    )
                ], spacing=8)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([campo_busca_com]),
            ft.Row(botoes_espacos, scroll=ft.ScrollMode.AUTO),
            ft.Divider(color=COLOR_BORDER),
            ft.ListView(controls=cards_posts, spacing=14, expand=True)
        ], expand=True, spacing=14)

    # --- BARRA DE NAVEGAÇÃO LATERAL / HEADER ---
    def atualizar_tela():
        conteudo_view.content = None
        if estado["aba_atual"] == "comunidade":
            conteudo_view.content = render_comunidade()
        elif estado["aba_atual"] == "musica":
            conteudo_view.content = render_louvores()
        elif estado["usuario_role"] == "admin":
            if estado["aba_atual"] == "estudos":
                conteudo_view.content = render_admin_estudos()
            elif estado["aba_atual"] == "oracao":
                conteudo_view.content = render_admin_oracoes()
            else:
                conteudo_view.content = render_comunidade()
        else:
            conteudo_view.content = render_aluno_home()
        page.update()

    def navegar_para(aba):
        estado["aba_atual"] = aba
        atualizar_tela()

    header = ft.Container(
        bgcolor=COLOR_CARD,
        border=ft.border.only(bottom=ft.BorderSide(1, COLOR_BORDER)),
        padding=ft.padding.symmetric(horizontal=24, vertical=12),
        content=ft.Row([
            ft.Row([
                ft.Icon(ft.Icons.LOCAL_FIRE_DEPARTMENT_ROUNDED, color=COLOR_FLAME, size=28),
                ft.Text("METANOIA", size=20, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                ft.Text("MINISTÉRIO & ESCOLA", size=12, color=COLOR_ACCENT, weight=ft.FontWeight.BOLD)
            ], alignment=ft.MainAxisAlignment.START),
            ft.Row([
                btn_role,
                ft.IconButton(ft.Icons.FORUM_ROUNDED, tooltip="🌐 Rede Social // Comunidade Circle", on_click=lambda e: navegar_para("comunidade")),
                ft.IconButton(ft.Icons.BOOK_ROUNDED, tooltip="Estudos & Apostilas", on_click=lambda e: navegar_para("estudos")),
                ft.IconButton(ft.Icons.VOLUNTEER_ACTIVISM_ROUNDED, tooltip="Mural de Oração", on_click=lambda e: navegar_para("oracao")),
                ft.IconButton(ft.Icons.MUSIC_NOTE_ROUNDED, tooltip="Louvores & Playlist Matheus", on_click=lambda e: navegar_para("musica")),
                ft.IconButton(ft.Icons.PEOPLE_ROUNDED, tooltip="Célula Digital", on_click=lambda e: navegar_para("celula")),
            ], spacing=12)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    )

    page.add(
        ft.Column([
            header,
            conteudo_view
        ], expand=True, spacing=0)
    )

    atualizar_tela()

if __name__ == "__main__":
    ft.app(target=main)

