import flet as ft
from data_generator import generate_retail_samples, generate_sme_samples
from pipelines import RetailPipeline, SMEPipeline
from visualizations import *
from voice import stt_from_file
import threading, random, time

retail_samples = generate_retail_samples()
sme_samples = generate_sme_samples()

def main(page: ft.Page):

    page.title = "Enterprise Loan Intelligence "
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 1400
    page.window_height = 900

    results = ft.Column(scroll="auto", expand=True)
    realtime_text = ft.Text(size=16)

    def realtime():
        while True:
            realtime_text.value = f"Live Risk Index: {random.randint(500,800)}"
            page.update()
            time.sleep(3)

    threading.Thread(target=realtime, daemon=True).start()

    def process_retail(e):
        app = retail_samples[0]
        result = RetailPipeline().run(app)
        show_dashboard(result)

    def process_sme(e):
        app = sme_samples[0]
        result = SMEPipeline().run(app)
        show_dashboard(result)

    def show_dashboard(result):
        results.controls.clear()
        results.controls.extend([
            realtime_text,
            sankey_pipeline_diagram(),
            foir_dscr_gauge(result.get("foir_post_loan",40)),
            ltv_gauge(result.get("ltv_ratio",70)),
            radar_scorecard(result),
            dpd_trend_chart(),
            portfolio_treemap(),
            cambridge_network(result)
        ])
        page.update()

    page.add(
        ft.Column([
            ft.Text("Loan Processing Dashboard", size=26, weight="bold"),
            ft.Row([
                ft.ElevatedButton("Process Retail", on_click=process_retail),
                ft.ElevatedButton("Process SME", on_click=process_sme)
            ]),
            results
        ])
    )

if __name__ == "__main__":
    ft.app(target=main, port=8000, view=ft.WEB_BROWSER)
