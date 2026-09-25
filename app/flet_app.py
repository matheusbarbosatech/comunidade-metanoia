import os
import sys
import urllib.parse
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
from app.services import comunidade_service, gamificacao_service

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
        "espaco_comunidade_id": None,
        "busca_comunidade": "",
        "modo_estudos": "gamificado" # "gamificado" (Duolingo) ou "grade" (Catálogo Tradicional)
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

    # --- TELAS DO PAINEL DE ESTUDOS & TEOLOGIA ---

    def tocar_aula_audio(caminho, titulo):
        if caminho and os.path.exists(caminho):
            try:
                os.startfile(caminho)
                page.show_snack_bar(ft.SnackBar(ft.Text(f"▶️ Reproduzindo aula: {titulo}")))
            except Exception as ex:
                page.show_snack_bar(ft.SnackBar(ft.Text(f"Erro ao abrir áudio: {ex}")))
        else:
            page.show_snack_bar(ft.SnackBar(ft.Text(f"Arquivo localizado em: {caminho or 'Pasta Desktop'}")))

    def abrir_apostila_pdf(caminho):
        if caminho and os.path.exists(caminho):
            try:
                os.startfile(caminho)
                page.show_snack_bar(ft.SnackBar(ft.Text("📑 Abrindo Apostila Oficial em PDF...")))
            except Exception as ex:
                page.show_snack_bar(ft.SnackBar(ft.Text(f"Erro ao abrir PDF: {ex}")))
        else:
            page.show_snack_bar(ft.SnackBar(ft.Text(f"Apostila localizada em: {caminho or 'Pasta Desktop'}")))

    def abrir_quiz_modal(aula_g):
        def fechar_quiz(e=None):
            if hasattr(page, "pop_dialog"):
                page.pop_dialog()
            else:
                dialog_quiz.open = False
                page.update()

        def selecionar_resposta(opcao_texto):
            resultado = gamificacao_service.responder_quiz(aula_g["codigo_aula"], opcao_texto)
            fechar_quiz()
            if resultado.get("acertou"):
                page.show_snack_bar(ft.SnackBar(
                    ft.Text(f"🎉 {resultado['mensagem']} Total: {resultado['novo_xp']} XP!"),
                    bgcolor="#065F46"
                ))
            else:
                page.show_snack_bar(ft.SnackBar(
                    ft.Text(f"{resultado['mensagem']}\n{resultado['explicacao']}"),
                    bgcolor="#991B1B"
                ))
            atualizar_tela()

        botoes_opcoes = []
        for idx, op in enumerate(aula_g.get("quiz_opcoes", [])):
            letra = chr(65 + idx)
            botoes_opcoes.append(
                ft.ElevatedButton(
                    f"{letra}) {op}",
                    bgcolor="#1E293B",
                    color=COLOR_TEXT,
                    on_click=lambda e, o=op: selecionar_resposta(o)
                )
            )

        dialog_quiz = ft.AlertDialog(
            title=ft.Row([
                ft.Text(f"⚡ Desafio Bereano: #{aula_g['codigo_aula']}"),
                ft.Container(
                    bgcolor="rgba(245, 158, 11, 0.2)",
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    border_radius=6,
                    content=ft.Text("+50 XP", color=COLOR_ACCENT, size=12, weight=ft.FontWeight.BOLD)
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            content=ft.Column([
                ft.Text(aula_g["quiz_pergunta"], size=15, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                ft.Divider(color=COLOR_BORDER),
                ft.Column(botoes_opcoes, spacing=8)
            ], tight=True, width=480),
            actions=[
                ft.TextButton("Cancelar", on_click=fechar_quiz)
            ]
        )

        if hasattr(page, "open"):
            page.open(dialog_quiz)
        else:
            page.dialog = dialog_quiz
            dialog_quiz.open = True
            page.update()

    def render_admin_estudos():
        modo_estudos = estado.get("modo_estudos", "gamificado")

        def alternar_modo(novo_modo):
            estado["modo_estudos"] = novo_modo
            atualizar_tela()

        botoes_modo = ft.Row([
            ft.ElevatedButton(
                "⚡ Trilha Gamificada Duolingo (Módulo 01)",
                bgcolor=COLOR_ACCENT if modo_estudos == "gamificado" else COLOR_CARD,
                color="#000" if modo_estudos == "gamificado" else COLOR_TEXT,
                on_click=lambda e: alternar_modo("gamificado")
            ),
            ft.ElevatedButton(
                "📑 Grade Tradicional de Aulas",
                bgcolor=COLOR_ACCENT if modo_estudos == "grade" else COLOR_CARD,
                color="#000" if modo_estudos == "grade" else COLOR_TEXT,
                on_click=lambda e: alternar_modo("grade")
            )
        ], spacing=10)

        if modo_estudos == "gamificado":
            dados_g = gamificacao_service.get_modulo1_data()
            perfil = dados_g["perfil"]
            mundos = dados_g["mundos"]

            hud_container = ft.Container(
                bgcolor="#0E1320",
                border=ft.border.all(1, "rgba(245, 158, 11, 0.35)"),
                border_radius=16,
                padding=ft.padding.symmetric(horizontal=20, vertical=16),
                content=ft.Row([
                    ft.Row([
                        ft.Container(
                            bgcolor="rgba(234, 88, 12, 0.2)",
                            padding=ft.padding.symmetric(horizontal=12, vertical=8),
                            border_radius=10,
                            content=ft.Row([
                                ft.Text("🔥", size=20),
                                ft.Column([
                                    ft.Text(f"{perfil['streak_dias']} Dias", weight=ft.FontWeight.BOLD, size=14, color=COLOR_TEXT),
                                    ft.Text("Ofensiva Ativa", size=10, color=COLOR_MUTED)
                                ], spacing=0)
                            ], spacing=8)
                        ),
                        ft.Container(
                            bgcolor="rgba(245, 158, 11, 0.2)",
                            padding=ft.padding.symmetric(horizontal=12, vertical=8),
                            border_radius=10,
                            content=ft.Row([
                                ft.Text("⚡", size=20),
                                ft.Column([
                                    ft.Text(f"{perfil['xp_total']} XP", weight=ft.FontWeight.BOLD, size=14, color=COLOR_ACCENT),
                                    ft.Text("Experiência", size=10, color=COLOR_MUTED)
                                ], spacing=0)
                            ], spacing=8)
                        ),
                        ft.Container(
                            bgcolor="rgba(56, 189, 248, 0.15)",
                            padding=ft.padding.symmetric(horizontal=12, vertical=8),
                            border_radius=10,
                            content=ft.Row([
                                ft.Text("🛡️", size=20),
                                ft.Column([
                                    ft.Text(f"{perfil['nivel']}", weight=ft.FontWeight.BOLD, size=14, color="#38BDF8"),
                                    ft.Text("Patente Bereana", size=10, color=COLOR_MUTED)
                                ], spacing=0)
                            ], spacing=8)
                        )
                    ], wrap=True, spacing=12),
                    ft.Column([
                        ft.Row([
                            ft.Text(f"Progresso: {perfil['aulas_concluidas']} / {perfil['total_aulas']} Aulas", size=12, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                            ft.Text(f"{perfil['porcentagem']}%", size=12, weight=ft.FontWeight.BOLD, color=COLOR_ACCENT)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.ProgressBar(
                            value=perfil["porcentagem"] / 100.0,
                            color=COLOR_ACCENT,
                            bgcolor="#1E293B",
                            width=220,
                            height=8
                        )
                    ], spacing=4)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, wrap=True)
            )

            lista_mundos_controls = []
            for m in mundos:
                cards_mundo = []
                for a in m["aulas"]:
                    concluida = bool(a.get("concluida"))
                    card_borda = "#10B981" if concluida else COLOR_BORDER
                    status_badge = ft.Container(
                        bgcolor="rgba(16, 185, 129, 0.2)" if concluida else "rgba(245, 158, 11, 0.15)",
                        padding=ft.padding.symmetric(horizontal=10, vertical=4),
                        border_radius=20,
                        content=ft.Text(
                            "✓ Concluída (+50 XP)" if concluida else "⚡ +50 XP Disponíveis",
                            color="#10B981" if concluida else COLOR_ACCENT,
                            size=11,
                            weight=ft.FontWeight.BOLD
                        )
                    )

                    botoes_aula = [
                        ft.ElevatedButton(
                            "▶️ Áudio MP3",
                            bgcolor=COLOR_FLAME,
                            color=COLOR_TEXT,
                            on_click=lambda e, p=a["audio_path"], t=a["titulo"]: tocar_aula_audio(p, t)
                        ),
                        ft.ElevatedButton(
                            "📑 Apostila PDF",
                            bgcolor="#1E293B",
                            color=COLOR_TEXT,
                            on_click=lambda e, p=a["apostila_path"]: abrir_apostila_pdf(p)
                        ),
                        ft.ElevatedButton(
                            "⚡ Desafio (Quiz)" if not concluida else "✓ Refazer Quiz",
                            bgcolor=COLOR_ACCENT if not concluida else "#065F46",
                            color="#000" if not concluida else "#FFF",
                            on_click=lambda e, ag=a: abrir_quiz_modal(ag)
                        )
                    ]

                    cards_mundo.append(
                        ft.Container(
                            bgcolor=COLOR_CARD,
                            border=ft.border.all(1, card_borda),
                            border_radius=14,
                            padding=18,
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(a.get("icone", "📖"), size=26),
                                    ft.Column([
                                        ft.Text(a["titulo"], size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                                        ft.Text(f"📖 {a['texto_biblico']}", size=12, color="#38BDF8")
                                    ], spacing=2, expand=True),
                                    status_badge
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Text(a["resumo"], size=13, color=COLOR_MUTED),
                                ft.Row(botoes_aula, alignment=ft.MainAxisAlignment.END, spacing=10, wrap=True)
                            ], spacing=10)
                        )
                    )

                lista_mundos_controls.append(
                    ft.Container(
                        bgcolor="#0B0E17",
                        border=ft.border.all(1, "rgba(245, 158, 11, 0.25)"),
                        border_radius=18,
                        padding=18,
                        content=ft.Column([
                            ft.Row([
                                ft.Container(
                                    bgcolor="rgba(245, 158, 11, 0.15)",
                                    padding=ft.padding.symmetric(horizontal=10, vertical=4),
                                    border_radius=8,
                                    content=ft.Text(f"MUNDO 0{m['id']}", size=11, color=COLOR_ACCENT, weight=ft.FontWeight.BOLD)
                                ),
                                ft.Text(m["nome"], size=17, weight=ft.FontWeight.BOLD, color=COLOR_TEXT)
                            ], spacing=10),
                            ft.Divider(color=COLOR_BORDER),
                            ft.Column(cards_mundo, spacing=12)
                        ], spacing=12)
                    )
                )

            return ft.Column([
                ft.Row([
                    ft.Column([
                        ft.Text("⚡ Trilha Gamificada Bíblica // Módulo 01", size=22, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                        ft.Text("Aprenda Introdução à Teologia com o método gamificado do Duolingo: áudios, apostilas e ganho de XP.", size=14, color=COLOR_MUTED)
                    ], spacing=4),
                    botoes_modo
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, wrap=True),
                hud_container,
                ft.Divider(color=COLOR_BORDER),
                ft.ListView(controls=lista_mundos_controls, spacing=20, expand=True)
            ], expand=True, spacing=14)

        # MODO GRADE TRADICIONAL
        conn = get_connection()
        cursor = conn.cursor()

        filtro = estado.get("filtro_estudos", "todos")
        if filtro == "teologia_15":
            cursor.execute("SELECT * FROM estudos_aulas WHERE codigo_aula BETWEEN 'A0001' AND 'A0015' ORDER BY codigo_aula ASC")
        elif filtro == "bibliologia_4":
            cursor.execute("SELECT * FROM estudos_aulas WHERE codigo_aula BETWEEN 'A0016' AND 'A0019' ORDER BY codigo_aula ASC")
        elif filtro == "apostilas":
            cursor.execute("SELECT * FROM estudos_aulas WHERE codigo_aula IS NULL ORDER BY id ASC")
        else:
            cursor.execute("SELECT * FROM estudos_aulas ORDER BY id ASC")

        aulas = cursor.fetchall()
        cursor.execute("SELECT COUNT(*) as tot FROM estudos_aulas")
        total_aulas = cursor.fetchone()["tot"]
        conn.close()

        def set_filtro(f):
            estado["filtro_estudos"] = f
            atualizar_tela()

        botoes_filtro = [
            ft.ElevatedButton(
                f"Todos ({total_aulas})",
                bgcolor=COLOR_ACCENT if filtro == "todos" else COLOR_CARD,
                color="#000" if filtro == "todos" else COLOR_TEXT,
                on_click=lambda e: set_filtro("todos")
            ),
            ft.ElevatedButton(
                "🔥 Introdução à Teologia (15 Aulas)",
                bgcolor=COLOR_ACCENT if filtro == "teologia_15" else COLOR_CARD,
                color="#000" if filtro == "teologia_15" else COLOR_TEXT,
                on_click=lambda e: set_filtro("teologia_15")
            ),
            ft.ElevatedButton(
                "📜 Bibliologia (4 Aulas)",
                bgcolor=COLOR_ACCENT if filtro == "bibliologia_4" else COLOR_CARD,
                color="#000" if filtro == "bibliologia_4" else COLOR_TEXT,
                on_click=lambda e: set_filtro("bibliologia_4")
            ),
            ft.ElevatedButton(
                "📑 Apostilas Gerais",
                bgcolor=COLOR_ACCENT if filtro == "apostilas" else COLOR_CARD,
                color="#000" if filtro == "apostilas" else COLOR_TEXT,
                on_click=lambda e: set_filtro("apostilas")
            )
        ]

        cards_aulas = []
        for aula in aulas:
            titulo = aula["titulo"]
            resumo = aula["resumo_conteudo"] or "Clique para ver os tópicos da apostila."
            codigo = aula["codigo_aula"]
            audio_path = aula["audio_path"]
            texto_biblico = aula["texto_biblico"]

            botoes_card = [
                ft.ElevatedButton(
                    "📖 Ver Resumo & Tópicos",
                    bgcolor="#2A2A38",
                    color=COLOR_TEXT,
                    on_click=lambda e, a=aula: abrir_detalhe_aula(a)
                )
            ]

            if audio_path:
                botoes_card.append(
                    ft.ElevatedButton(
                        "▶️ Ouvir Aula (MP3)",
                        bgcolor=COLOR_FLAME,
                        color=COLOR_TEXT,
                        on_click=lambda e, p=audio_path, t=titulo: tocar_aula_audio(p, t)
                    )
                )

            botoes_card.append(
                ft.OutlinedButton(
                    "🎬 Teleprompter / Gravação",
                    style=ft.ButtonStyle(color=COLOR_ACCENT),
                    on_click=lambda e, r=resumo, t=titulo: page.launch_url(f"/teleprompter?texto={urllib.parse.quote(r or t)}")
                )
            )

            tags_row = []
            if codigo:
                tags_row.append(
                    ft.Container(
                        bgcolor="rgba(245, 158, 11, 0.15)",
                        padding=ft.padding.symmetric(horizontal=8, vertical=3),
                        border_radius=6,
                        content=ft.Text(f"#{codigo}", size=11, color=COLOR_ACCENT, weight=ft.FontWeight.BOLD)
                    )
                )
            if texto_biblico:
                tags_row.append(
                    ft.Container(
                        bgcolor="#1E293B",
                        padding=ft.padding.symmetric(horizontal=8, vertical=3),
                        border_radius=6,
                        content=ft.Text(f"📖 {texto_biblico}", size=11, color="#38BDF8")
                    )
                )
            if audio_path:
                tags_row.append(
                    ft.Container(
                        bgcolor="rgba(16, 185, 129, 0.15)",
                        padding=ft.padding.symmetric(horizontal=8, vertical=3),
                        border_radius=6,
                        content=ft.Text("🎧 Áudio Disponível (Desktop)", size=11, color="#10B981", weight=ft.FontWeight.BOLD)
                    )
                )

            cards_aulas.append(
                ft.Container(
                    bgcolor=COLOR_CARD,
                    border=ft.border.all(1, COLOR_BORDER),
                    border_radius=14,
                    padding=18,
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.AUTO_STORIES_ROUNDED if not audio_path else ft.Icons.HEADPHONES_ROUNDED, color=COLOR_ACCENT, size=26),
                            ft.Text(titulo, size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT, expand=True)
                        ]),
                        ft.Row(tags_row, wrap=True, spacing=8),
                        ft.Text(resumo[:200] + ("..." if len(resumo) > 200 else ""), size=13, color=COLOR_MUTED),
                        ft.Row(botoes_card, alignment=ft.MainAxisAlignment.END, spacing=10, wrap=True)
                    ], spacing=10)
                )
            )

        return ft.Column([
            ft.Row([
                ft.Column([
                    ft.Text("📚 Escola Bíblica & Apostilas Teológicas", size=22, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                    ft.Text("15 Aulas de Introdução à Teologia, Bibliologia e acervo de apostilas completas.", size=14, color=COLOR_MUTED)
                ], spacing=4),
                botoes_modo
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, wrap=True),
            ft.Row(botoes_filtro, scroll=ft.ScrollMode.AUTO),
            ft.Divider(color=COLOR_BORDER),
            ft.ListView(controls=cards_aulas, spacing=16, expand=True)
        ], expand=True, spacing=14)

    def abrir_detalhe_aula(aula):
        def fechar(e=None):
            if hasattr(page, "pop_dialog"):
                page.pop_dialog()
            else:
                dialog.open = False
                page.update()

        audio_path = aula["audio_path"]
        titulo = aula["titulo"]

        dialog_actions = [
            ft.TextButton("Fechar", on_click=fechar)
        ]
        if audio_path:
            dialog_actions.insert(0, ft.ElevatedButton(
                "▶️ Tocar Áudio da Aula",
                bgcolor=COLOR_FLAME,
                color=COLOR_TEXT,
                on_click=lambda e: tocar_aula_audio(audio_path, titulo)
            ))

        dialog_actions.insert(1, ft.OutlinedButton(
            "🎬 Roteiro Teleprompter",
            style=ft.ButtonStyle(color=COLOR_ACCENT),
            on_click=lambda e: page.launch_url(f"/teleprompter?texto={urllib.parse.quote(aula['resumo_conteudo'] or titulo)}")
        ))

        corpo_dialog = [
            ft.Text(aula["titulo"], size=18, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
            ft.Text(f"📖 Texto Bíblico: {aula['texto_biblico'] or 'Conforme apostila'}", size=13, color=COLOR_ACCENT, weight=ft.FontWeight.BOLD),
            ft.Divider(color=COLOR_BORDER),
            ft.Markdown(aula["resumo_conteudo"] or "Sem resumo disponível.")
        ]
        if audio_path:
            corpo_dialog.append(ft.Container(
                bgcolor="#1E293B",
                padding=10,
                border_radius=8,
                content=ft.Row([
                    ft.Icon(ft.Icons.FOLDER_ROUNDED, color=COLOR_ACCENT, size=18),
                    ft.Text(f"Local do Arquivo: {audio_path}", size=11, color=COLOR_MUTED, expand=True)
                ])
            ))

        dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.BOOK_ROUNDED, color=COLOR_ACCENT),
                ft.Text("Guia Didático da Aula", color=COLOR_TEXT, weight=ft.FontWeight.BOLD)
            ], spacing=8),
            content=ft.Container(
                width=650,
                height=480,
                content=ft.ListView(corpo_dialog, spacing=10)
            ),
            actions=dialog_actions
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
                        ft.OutlinedButton("🕊️ Mural de Oração", style=ft.ButtonStyle(color=COLOR_ACCENT), on_click=lambda e: navegar_para("oracao"))
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
        elif estado["aba_atual"] == "estudos":
            conteudo_view.content = render_admin_estudos()
        elif estado["aba_atual"] == "oracao":
            conteudo_view.content = render_admin_oracoes()
        elif estado["aba_atual"] == "celula":
            conteudo_view.content = render_aluno_home()
        elif estado["usuario_role"] == "admin":
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
                ft.IconButton(ft.Icons.BOLT_ROUNDED, tooltip="⚡ Trilha Gamificada Duolingo (Módulo 01)", icon_color=COLOR_ACCENT, on_click=lambda e: (estado.update({"aba_atual": "estudos", "modo_estudos": "gamificado"}), atualizar_tela())),
                ft.IconButton(ft.Icons.FORUM_ROUNDED, tooltip="🌐 Rede Social // Comunidade Skool", on_click=lambda e: navegar_para("comunidade")),
                ft.IconButton(ft.Icons.BOOK_ROUNDED, tooltip="Estudos & Apostilas", on_click=lambda e: (estado.update({"aba_atual": "estudos", "modo_estudos": "grade"}), atualizar_tela())),
                ft.IconButton(ft.Icons.VOLUNTEER_ACTIVISM_ROUNDED, tooltip="Mural de Oração", on_click=lambda e: navegar_para("oracao")),
                ft.IconButton(ft.Icons.PEOPLE_ROUNDED, tooltip="Célula Digital", on_click=lambda e: navegar_para("celula")),
            ], spacing=10)
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

