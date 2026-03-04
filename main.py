import flet as ft
import threading, random, time
from data_generator import generate_retail_samples, generate_sme_samples
from pipelines import RetailPipeline, SMEPipeline
from visualizations import (sankey_pipeline_diagram, foir_dscr_gauge, ltv_gauge,
                             radar_scorecard, dpd_trend_chart, portfolio_treemap,
                             cambridge_network)
from voice import stt_from_file

retail_all = generate_retail_samples()
sme_all    = generate_sme_samples()


def translate_to_hindi(text: str) -> str:
    try:
        from deep_translator import GoogleTranslator
        return GoogleTranslator(source="en", target="hi").translate(text)
    except Exception as ex:
        return f"[Translation error: {ex}]"


def main(page: ft.Page):
    page.title = "Enterprise Loan Intelligence"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width  = 1400
    page.window_height = 900
    page.scroll = ft.ScrollMode.AUTO

    # ── shared state ─────────────────────────────────────────────────────────
    selected_applicant = {"data": None}

    # ── live risk ticker ──────────────────────────────────────────────────────
    live_text = ft.Text("Live Risk Index: —", size=13, color=ft.colors.BLUE_700,
                        weight=ft.FontWeight.BOLD)
    def _live():
        while True:
            live_text.value = f"🔴 Live Risk Index: {random.randint(500,800)}"
            try: page.update()
            except: pass
            time.sleep(3)
    threading.Thread(target=_live, daemon=True).start()

    # ════════════════════════════════════════════════════════════════════════
    # DETAIL PANEL (right side)
    # ════════════════════════════════════════════════════════════════════════
    detail_col    = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=6)
    dashboard_col = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)

    translate_output = ft.Text("", size=13, italic=True, color=ft.colors.DEEP_PURPLE)
    voice_status     = ft.Text("", size=12, color=ft.colors.GREY_700)

    def show_detail(app):
        selected_applicant["data"] = app
        rows = []
        skip = {"id"}
        for k, v in app.items():
            if k in skip: continue
            rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(k.replace("_"," ").title(), weight=ft.FontWeight.W_500, size=13)),
                ft.DataCell(ft.Text(str(v), size=13)),
            ]))
        detail_col.controls.clear()
        detail_col.controls.append(
            ft.Text(f"📋 {app['name']}  [{app['id']}]",
                    size=16, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_900)
        )
        detail_col.controls.append(
            ft.DataTable(
                columns=[ft.DataColumn(ft.Text("Field")),
                         ft.DataColumn(ft.Text("Value"))],
                rows=rows,
                border=ft.border.all(1, ft.colors.BLUE_100),
                border_radius=8,
            )
        )
        detail_col.controls.append(translate_output)
        detail_col.controls.append(voice_status)
        page.update()

    def process_and_show(e):
        app = selected_applicant.get("data")
        if not app:
            page.snack_bar = ft.SnackBar(ft.Text("Select an applicant first!"))
            page.snack_bar.open = True
            page.update()
            return
        is_sme = app["id"].startswith("S")
        result = (SMEPipeline() if is_sme else RetailPipeline()).run(app)
        dashboard_col.controls.clear()
        dashboard_col.controls.extend([
            live_text,
            ft.Text("Pipeline Flow", size=14, weight=ft.FontWeight.BOLD),
            sankey_pipeline_diagram(),
            ft.Row([
                ft.Column([ft.Text("FOIR Gauge", size=13, weight=ft.FontWeight.BOLD),
                           foir_dscr_gauge(result.get("foir_post_loan", 40))], expand=1),
                ft.Column([ft.Text("LTV Gauge",  size=13, weight=ft.FontWeight.BOLD),
                           ltv_gauge(result.get("ltv_ratio", 70))], expand=1),
            ]),
            ft.Text("Risk Scorecard", size=14, weight=ft.FontWeight.BOLD),
            radar_scorecard(result),
            ft.Text("DPD Trend", size=14, weight=ft.FontWeight.BOLD),
            dpd_trend_chart(),
            ft.Text("Portfolio by City", size=14, weight=ft.FontWeight.BOLD),
            portfolio_treemap(),
            ft.Text("Entity Network", size=14, weight=ft.FontWeight.BOLD),
            cambridge_network(result),
            ft.Container(
                ft.Text(f"Risk: {result.get('risk','—')}",
                        size=18, weight=ft.FontWeight.BOLD,
                        color={"LOW":"#27ae60","MEDIUM":"#f39c12","HIGH":"#e74c3c"}.get(
                            result.get("risk","MEDIUM"),"#333")),
                padding=12, bgcolor=ft.colors.GREY_100, border_radius=8,
            )
        ])
        page.update()

    def do_translate(e):
        app = selected_applicant.get("data")
        if not app: return
        summary = (f"Name: {app['name']}, City: {app.get('city','')}, "
                   f"Loan: {app.get('loan_amt','')}, CIBIL: {app.get('cibil_score','')}")
        translate_output.value = "⏳ Translating..."
        page.update()
        hindi = translate_to_hindi(summary)
        translate_output.value = f"🇮🇳 Hindi: {hindi}"
        page.update()

    def do_voice(e):
        voice_status.value = "🎤 Voice: upload a .wav file to use STT"
        page.update()

    # ════════════════════════════════════════════════════════════════════════
    # SEARCHABLE LIST BUILDER
    # ════════════════════════════════════════════════════════════════════════
    def build_applicant_tab(all_data, key_field="city"):
        search_box  = ft.TextField(hint_text=f"Search by name / {key_field}…",
                                   prefix_icon=ft.icons.SEARCH,
                                   expand=True, height=45)
        list_view   = ft.ListView(expand=True, spacing=4, padding=4)

        def render_list(data):
            list_view.controls.clear()
            for app in data[:100]:  # cap at 100 for performance
                label = f"{app['id']}  •  {app['name']}  •  {app.get(key_field,'')}"
                def _make_click(a=app):
                    def _click(e):
                        show_detail(a)
                    return _click
                list_view.controls.append(
                    ft.ListTile(
                        title=ft.Text(label, size=13),
                        subtitle=ft.Text(f"₹{app['loan_amt']:,}  |  CIBIL {app['cibil_score']}", size=11),
                        on_click=_make_click(),
                        bgcolor=ft.colors.SURFACE_VARIANT,
                        shape=ft.RoundedRectangleBorder(radius=6),
                    )
                )
            page.update()

        def on_search(e):
            q = search_box.value.strip().lower()
            filtered = [a for a in all_data if
                        q in a["name"].lower() or q in a.get(key_field,"").lower()] if q else all_data
            render_list(filtered)

        search_box.on_change = on_search
        render_list(all_data)

        return ft.Row([
            # Left: list
            ft.Container(
                ft.Column([
                    ft.Row([search_box]),
                    ft.Container(list_view, expand=True),
                ], expand=True),
                width=420, expand=False,
                border=ft.border.all(1, ft.colors.BLUE_100),
                border_radius=10, padding=8,
            ),
            # Right: detail + dashboard
            ft.Container(
                ft.Column([
                    ft.Row([
                        ft.ElevatedButton("⚙ Process & Dashboard", on_click=process_and_show,
                                          bgcolor=ft.colors.BLUE_700, color=ft.colors.WHITE),
                        ft.ElevatedButton("🇮🇳 Translate", on_click=do_translate,
                                          bgcolor=ft.colors.DEEP_PURPLE, color=ft.colors.WHITE),
                        ft.ElevatedButton("🎤 Voice", on_click=do_voice,
                                          bgcolor=ft.colors.TEAL, color=ft.colors.WHITE),
                    ], spacing=8),
                    ft.Divider(),
                    ft.Row([
                        ft.Container(detail_col, expand=1,
                                     border=ft.border.all(1, ft.colors.GREY_200),
                                     border_radius=8, padding=10),
                        ft.Container(dashboard_col, expand=2,
                                     border=ft.border.all(1, ft.colors.GREY_200),
                                     border_radius=8, padding=10),
                    ], expand=True, vertical_alignment=ft.CrossAxisAlignment.START),
                ], expand=True),
                expand=True, padding=8,
            ),
        ], expand=True, vertical_alignment=ft.CrossAxisAlignment.START)

    # ════════════════════════════════════════════════════════════════════════
    # TABS
    # ════════════════════════════════════════════════════════════════════════
    retail_tab_content = build_applicant_tab(retail_all, key_field="city")
    sme_tab_content    = build_applicant_tab(sme_all,    key_field="industry")

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=200,
        expand=True,
        tabs=[
            ft.Tab(text="🏦 Retail Loans",  content=ft.Container(retail_tab_content, padding=10, expand=True)),
            ft.Tab(text="🏢 SME Loans",     content=ft.Container(sme_tab_content,    padding=10, expand=True)),
            ft.Tab(text="📊 Dashboard",     content=ft.Container(dashboard_col,       padding=10, expand=True)),
        ],
    )

    page.add(
        ft.Column([
            ft.Container(
                ft.Row([
                    ft.Text("Enterprise Loan Intelligence", size=22,
                            weight=ft.FontWeight.BOLD, color=ft.colors.BLUE_900),
                    ft.Container(expand=True),
                    live_text,
                ]),
                bgcolor=ft.colors.BLUE_50, padding=ft.padding.symmetric(horizontal=16, vertical=8),
                border_radius=0,
            ),
            ft.Container(tabs, expand=True),
        ], expand=True, spacing=0)
    )


if __name__ == "__main__":
    ft.app(target=main, port=8000, view=ft.WEB_BROWSER)
