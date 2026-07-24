import flet as ft
import random

def piyasa_sayfasi_olustur(page: ft.Page, geri_don_fonksiyonu):
    def cerceve(k, r): return ft.Border(ft.BorderSide(k, r), ft.BorderSide(k, r), ft.BorderSide(k, r), ft.BorderSide(k, r))

    # Sahte Emir Tahtası Verileri
    alislar = [ft.Row([ft.Text(f"{random.uniform(64000, 65000):.2f}", color="#10B981", weight="bold"), ft.Text(f"{random.uniform(0.1, 2.5):.3f}", color="white")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN) for _ in range(10)]
    satislar = [ft.Row([ft.Text(f"{random.uniform(65000, 66000):.2f}", color="#EF4444", weight="bold"), ft.Text(f"{random.uniform(0.1, 2.5):.3f}", color="white")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN) for _ in range(10)]
    satislar.reverse()

    tahta = ft.Row([
        ft.Container(content=ft.Column([ft.Text("🟢 ALIŞ (BIDS)", color="#10B981", weight="900")] + alislar), expand=1, padding=15, bgcolor="#0A0A0E", border=cerceve(1, "#064E3B"), border_radius=10, shadow=[ft.BoxShadow(blur_radius=15, color="#10B981", spread_radius=-5)]),
        ft.Container(content=ft.Column([ft.Text("🔴 SATIŞ (ASKS)", color="#EF4444", weight="900")] + satislar), expand=1, padding=15, bgcolor="#0A0A0E", border=cerceve(1, "#7F1D1D"), border_radius=10, shadow=[ft.BoxShadow(blur_radius=15, color="#EF4444", spread_radius=-5)])
    ], spacing=20)

    ana_icerik = ft.Container(
        content=ft.Column([
            ft.Row([ft.Text("🔴 CANLI PİYASA", size=28, weight="900", color="white"), ft.Text("BTC/USDT", size=20, color="#00ffcc")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(color="#1A1A24"),
            ft.Container(content=ft.Text("$65,024.50", size=45, weight="900", color="#00ffcc"), alignment=ft.Alignment(0, 0), padding=20, border_radius=15, gradient=ft.LinearGradient(begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1), colors=["#0A0A0E", "#032015"])),
            tahta
        ]), padding=20, expand=True, bgcolor="#030304"
    )

    return ft.Container(content=ft.Column([ft.TextButton(content=ft.Text("⬅️ Panoya Dön", color="white"), on_click=lambda e: geri_don_fonksiyonu()), ana_icerik], expand=True), bgcolor="#030304", expand=True)