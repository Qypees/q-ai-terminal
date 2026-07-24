import flet as ft

def ai_signal_sayfasi_olustur(page: ft.Page, geri_don_fonksiyonu):
    def cerceve(k, r): return ft.Border(ft.BorderSide(k, r), ft.BorderSide(k, r), ft.BorderSide(k, r), ft.BorderSide(k, r))

    sinyaller = [
        {"coin": "ETH", "yon": "LONG", "renk": "#00ffcc", "giris": "3100.50", "hedef": "3400.00", "stop": "2950.00", "guven": 0.92},
        {"coin": "SOL", "yon": "SHORT", "renk": "#F43F5E", "giris": "145.20", "hedef": "120.00", "stop": "155.00", "guven": 0.85}
    ]

    sinyal_sutunu = ft.Row(wrap=True, spacing=20, alignment=ft.MainAxisAlignment.CENTER)
    for s in sinyaller:
        kart = ft.Container(
            content=ft.Column([
                ft.Row([ft.Text(f"{s['coin']}/USDT", size=22, weight="900", color="white"), ft.Text(s["yon"], size=18, weight="900", color=s["renk"])], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(color="#1A1A24"),
                ft.Row([ft.Column([ft.Text("GİRİŞ", size=10, color="#737373"), ft.Text(s["giris"], size=16, color="white", weight="bold")]), ft.Column([ft.Text("HEDEF", size=10, color="#737373"), ft.Text(s["hedef"], size=16, color=s["renk"], weight="bold")]), ft.Column([ft.Text("STOP", size=10, color="#737373"), ft.Text(s["stop"], size=16, color="#EF4444", weight="bold")])], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=10),
                ft.Text("Q-AI Güven Skoru", size=10, color="#A0A0A5"),
                ft.ProgressBar(value=s["guven"], color=s["renk"], bgcolor="#1A1A24", height=8)
            ]),
            bgcolor="#050507", width=350, padding=20, border_radius=16, border=cerceve(1, s["renk"]), shadow=[ft.BoxShadow(blur_radius=25, color=s["renk"], spread_radius=-10)]
        )
        sinyal_sutunu.controls.append(kart)

    ana_icerik = ft.Container(
        content=ft.Column([
            ft.Text("🧠 Q-AI ALGORİTMİK SİNYALLER", size=28, weight="900", color="#00ffcc"),
            ft.Text("Sistem piyasayı tarıyor. Tespit edilen en güvenilir fırsatlar aşağıdadır.", color="#737373"),
            ft.Divider(color="#1A1A24"), ft.Container(height=20), sinyal_sutunu
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER), padding=20, expand=True, bgcolor="#030304"
    )

    return ft.Container(content=ft.Column([ft.TextButton(content=ft.Text("⬅️ Panoya Dön", color="white"), on_click=lambda e: geri_don_fonksiyonu()), ana_icerik], expand=True), bgcolor="#030304", expand=True)