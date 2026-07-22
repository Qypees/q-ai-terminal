import flet as ft

def genel_sayfa_olustur(baslik, emoji, aciklama, ana_ekrana_don_fonksiyonu):
    zemin_siyah = "#0c0c0c"
    kutu_zemin = "#151515"
    luks_turuncu = "#fb923c"
    mat_altin = "#8a6c44"

    ust_panel = ft.Row(
        controls=[
            ft.Container(content=ft.Text("◄ GERİ DÖN", color=luks_turuncu, weight="900", size=13), on_click=lambda e: ana_ekrana_don_fonksiyonu(), padding=10),
            ft.Container(content=ft.Text(f"{emoji} {baslik} Paneli", size=18, color="white", weight="bold"), padding=10)
        ], alignment="spaceBetween"
    )

    return ft.Container(
        expand=True, bgcolor=zemin_siyah, padding=15,
        content=ft.Column(
            expand=True, spacing=20,
            controls=[
                ust_panel,
                ft.Container(
                    expand=True, bgcolor=kutu_zemin, border_radius=20, padding=30,
                    shadow=[
                        ft.BoxShadow(spread_radius=1, blur_radius=8, color="#222222", offset=ft.Offset(-4, -4)),
                        ft.BoxShadow(spread_radius=1, blur_radius=8, color="#000000", offset=ft.Offset(4, 4)),
                    ],
                    content=ft.Column(
                        controls=[
                            ft.Text(emoji, size=50),
                            ft.Text(f"{baslik} Modülü Aktif", color=mat_altin, size=22, weight="bold"),
                            ft.Container(height=10),
                            ft.Text(aciklama, color="#AAAAAA", size=14),
                            ft.Container(height=20),
                            ft.Container(
                                content=ft.Text("Sistem Durumu: Stabil ve Çalışır", color="#107C10", weight="bold"),
                                bgcolor="#0a260a", padding=12, border_radius=8
                            )
                        ], alignment="center", horizontal_alignment="center"
                    )
                )
            ]
        )
    )