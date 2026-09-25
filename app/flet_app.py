"""Plataforma Integrada Ministério Metanoia & Escola de Pregadores.
Construída em Python + Flet com perfis de Administrador (Pastor) e Aluno (Discípulo).
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import flet as ft
from app.db.database import get_connection

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
    page.title = "Ministério Metanoia // Plataforma Pastoral & Escola Bíblica"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = COLOR_BG
    page.padding = 0

    # Estado da Aplicação
    estado = {
        "usuario_role": "admin", # "admin" (Pastor) ou "aluno" (Discípulo)
        "aba_atual": "estudos",
        "resumo_selecionado": None
    }

    # Container dinâmico central
    conteudo_view = ft.Container(expand=True, padding=24)

    def alternar_papel(e):
        estado["usuario_role"] = "aluno" if estado["usuario_role"] == "admin" else "admin"
        btn_role.text = f"Modo: {'👑 Pastor (ADM)' if estado['usuario_role'] == 'admin' else '🐑 Discípulo (Aluno)'}"
        btn_role.update()
        atualizar_tela()

    btn_role = ft.ElevatedButton(
        text="Modo: 👑 Pastor (ADM)",
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
        def fechar(e):
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
                    colors=["#1E1E28", "#121217"]
                ),
                border=ft.border.all(1, COLOR_BORDER),
                border_radius=16,
                padding=24,
                content=ft.Column([
                    ft.Row([
                        ft.Icon(ft.Icons.WB_SUNNY_ROUNDED, color=COLOR_ACCENT, size=32),
                        ft.Text("A ORDEM MATINAL DAS 06H // DIA 01", size=20, weight=ft.FontWeight.BOLD, color=COLOR_TEXT)
                    ]),
                    ft.Text('"Não vos conformeis com este século, mas transformai-vos pela renovação da vossa mente." — Romanos 12:2', size=14, italic=True, color=COLOR_ACCENT),
                    ft.Text("Quem governa o seu dia hoje? O algoritmo ou o Senhor da sua alma? Antes de tocar em qualquer rede social, consagre o seu primeiro suspiro aos pés da cruz.", size=14, color=COLOR_MUTED),
                    ft.Row([
                        ft.ElevatedButton("🎧 Ouvir Áudio Devocional (2 min)", bgcolor=COLOR_FLAME, color=COLOR_TEXT),
                        ft.OutlinedButton("✅ Cumprir Ordem de Missão", style=ft.ButtonStyle(color=COLOR_ACCENT))
                    ])
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
                        ft.Text("Célula Digital Metanoia", size=16, weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                        ft.Text("Encontro Semanal ao Vivo às Terças 20h30. Ninguém luta sozinho!", size=13, color=COLOR_MUTED),
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
                        ft.Icon(ft.Icons.SHIELD_ROUNDED, color="#EF4444", size=28),
                        ft.Text("Protocolo SOS 180s", size=16, weight=ft.FontWeight.BOLD, color="#EF4444"),
                        ft.Text("Fissura por dopamina ou crise de ansiedade? Quebre a onda agora.", size=13, color=COLOR_MUTED),
                        ft.ElevatedButton(
                            "Disparar SOS Imediato",
                            bgcolor="#7F1D1D",
                            color=COLOR_TEXT,
                            on_click=lambda e: abrir_modal_sos()
                        )
                    ], spacing=10)
                )
            ], spacing=16)
        ], spacing=20, expand=True)

    def abrir_modal_sos():
        def fechar(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("🚨 PROTOCOLO SENTINELA SOS // 180s", color="#EF4444", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=450,
                height=250,
                content=ft.Column([
                    ft.Text("1. LEVANTE DA CAMA OU CADEIRA AGORA.", weight=ft.FontWeight.BOLD, color=COLOR_TEXT),
                    ft.Text("2. Vá até o banheiro e lave o rosto com água gelada (choque vagal).", color=COLOR_MUTED),
                    ft.Text("3. Faça 20 flexões no chão ou 30 polichinelos para redirecionar o sangue.", color=COLOR_MUTED),
                    ft.Text('"Aquele que cuida estar em pé, olhe que não caia." — 1 Co 10:12', color=COLOR_ACCENT, italic=True),
                    ft.Text("A onda química quebra em 3 minutos. Você é livre em Cristo!", color=COLOR_TEXT)
                ], spacing=12)
            ),
            actions=[ft.ElevatedButton("Concluir Protocolo & De Pé", bgcolor=COLOR_FLAME, color=COLOR_TEXT, on_click=fechar)]
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

    # --- BARRA DE NAVEGAÇÃO LATERAL / HEADER ---
    def atualizar_tela():
        conteudo_view.content = None
        if estado["usuario_role"] == "admin":
            if estado["aba_atual"] == "estudos":
                conteudo_view.content = render_admin_estudos()
            elif estado["aba_atual"] == "oracao":
                conteudo_view.content = render_admin_oracoes()
            else:
                conteudo_view.content = render_admin_estudos()
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
                ft.IconButton(ft.Icons.BOOK_ROUNDED, tooltip="Estudos & Apostilas", on_click=lambda e: navegar_para("estudos")),
                ft.IconButton(ft.Icons.VOLUNTEER_ACTIVISM_ROUNDED, tooltip="Mural de Oração", on_click=lambda e: navegar_para("oracao")),
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
