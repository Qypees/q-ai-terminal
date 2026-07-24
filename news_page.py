import flet as ft

def haber_sayfasi_olustur(page: ft.Page, geri_don_fonksiyonu):
    def cerceve(k, r): return ft.Border(ft.BorderSide(k, r), ft.BorderSide(k, r), ft.BorderSide(k, r), ft.BorderSide(k, r))

    haberler = [
        {"saat": "10:45", "baslik": "SEC, Yeni Kripto ETF Başvurularını Onayladı!", "etki": "BULLISH 🚀", "renk": "#10B981", "skor": 0.9},
        {"saat": "09:30", "baslik": "Global Borsalarda Sert Satış Baskısı Devam Ediyor.", "etki": "BEARISH 🩸", "renk": "#EF4444", "skor": 0.2},
        {"saat": "08:15", "baslik": "Asya Merkez Bankası Faiz Kararını Sabit Tuttu.", "etki": "NÖTR ⚖️", "renk": "#9CA3AF", "skor": 0.5}
    ]

    haber_sutunu = ft.Column(spacing=15, expand=True, scroll=ft.ScrollMode.AUTO)
    for h in haberler:
        kart = ft.Container(
            content=ft.Column([
                ft.Row([ft.Text(h["saat"], color="#737373"), ft.Container(content=ft.Text(h["etki"], color=h["renk"], weight="bold", size=12), bgcolor="#1A1A24", padding=5, border_radius=5)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Text(h["baslik"], color="white", size=16, weight="bold"),
                ft.Text("AI Etki Analizi:", color="#A0A0A5", size=10),
                ft.ProgressBar(value=h["skor"], color=h["renk"], bgcolor="#1A1A24")
            ]),
            bgcolor="#0A0A0E", padding=20, border_radius=12, border=cerceve(1, h["renk"]), shadow=[ft.BoxShadow(blur_radius=10, color=h["renk"], spread_radius=-8)]
        )
        haber_sutunu.controls.append(kart)

    ana_icerik = ft.Container(
        content=ft.Column([
            ft.Text("📰 AI SON DAKİKA RADARI", size=28, weight="900", color="white"),
            ft.Divider(color="#1A1A24"), haber_sutunu
        ]), padding=20, expand=True, bgcolor="#030304"
    )

    return ft.Container(content=ft.Column([ft.TextButton(content=ft.Text("⬅️ Panoya Dön", color="white"), on_click=lambda e: geri_don_fonksiyonu()), ana_icerik], expand=True), bgcolor="#030304", expand=True)