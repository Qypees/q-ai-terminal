import flet as ft

def sinyal_sayfasi_olustur(page, ana_ekrana_don_fonksiyonu):
    zemin_siyah = "#0c0c0c"
    kutu_zemin = "#151515"
    luks_turuncu = "#fb923c"
    mat_altin = "#8a6c44"

    ust_panel = ft.Row(
        controls=[
            ft.Container(content=ft.Text("◄ GERİ DÖN", color=luks_turuncu, weight="900", size=13), on_click=lambda e: ana_ekrana_don_fonksiyonu(), padding=10),
            ft.Container(content=ft.Text("⚡ Bot Sinyal Merkezi", size=18, color="white", weight="bold"), padding=10)
        ], alignment="spaceBetween"
    )

    def neumo_kutu(icerik, padding_degeri=15):
        return ft.Container(
            bgcolor=kutu_zemin, border_radius=15, padding=padding_degeri,
            shadow=[
                ft.BoxShadow(spread_radius=1, blur_radius=6, color="#222222", offset=ft.Offset(-3, -3)),
                ft.BoxShadow(spread_radius=1, blur_radius=6, color="#000000", offset=ft.Offset(3, 3)),
            ], content=icerik
        )

    def sinyal_karti(coin, yon, fiyat, zaman, guven):
        yon_renk = "#107C10" if yon == "AL (BUY)" else "#E81123"
        bg_renk = "#0a260a" if yon == "AL (BUY)" else "#260a0a"
        return neumo_kutu(
            ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Row(controls=[
                                ft.Text(coin, color=mat_altin, weight="900", size=16),
                                ft.Container(content=ft.Text(yon, color=yon_renk, weight="bold", size=11), bgcolor=bg_renk, border_radius=6, padding=6)
                            ], spacing=10),
                            ft.Text(zaman, color="#666666", size=12)
                        ], alignment="spaceBetween"
                    ),
                    ft.Container(height=4),
                    ft.Row(
                        controls=[
                            ft.Text(f"Tetik Fiyat: ${fiyat}", color="white", size=13),
                            ft.Text(f"Güven: %{guven}", color=luks_turuncu, weight="bold", size=13)
                        ], alignment="spaceBetween"
                    )
                ], spacing=5
            ), padding_degeri=12
        )

    liste_alani = ft.Column(
        expand=True, scroll="auto", spacing=12,
        controls=[
            sinyal_karti("BTC/USDT", "AL (BUY)", "64,150.00", "Az önce", "94"),
            sinyal_karti("ETH/USDT", "SAT (SELL)", "3,420.50", "3 dk önce", "88"),
            sinyal_karti("SOL/USDT", "AL (BUY)", "144.80", "12 dk önce", "91"),
            sinyal_karti("AVAX/USDT", "AL (BUY)", "28.40", "25 dk önce", "85"),
        ]
    )

    return ft.Container(
        expand=True, bgcolor=zemin_siyah, padding=15,
        content=ft.Column(expand=True, spacing=15, controls=[ust_panel, ft.Text("Aktif Algoritma Sinyalleri", size=14, color="#AAAAAA"), liste_alani])
    )