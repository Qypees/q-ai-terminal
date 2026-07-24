import flet as ft
import random
import threading
import time

def top5_sayfasi_olustur(page: ft.Page, geri_don_fonksiyonu):
    sayfa_aktif = [True] 
    
    def cerceve(k, r): return ft.Border(ft.BorderSide(k, r), ft.BorderSide(k, r), ft.BorderSide(k, r), ft.BorderSide(k, r))
    coin_havuzu = ["BTC", "ETH", "SOL", "PEPE", "WIF", "AVAX", "LINK", "DOGE", "RNDR", "FET", "SHIB", "ARB", "OP", "SUI", "APT"]
    
    def ai_veri_uret(zaman_dilimi):
        secilenler = random.sample(coin_havuzu, 10)
        yukselenler, dusenler = [], []
        carpan = 1
        if "15" in zaman_dilimi: carpan = 1.5
        elif "30" in zaman_dilimi: carpan = 2
        elif "Saat" in zaman_dilimi: carpan = 4
        elif "Gün" in zaman_dilimi: carpan = 10
        elif "Hafta" in zaman_dilimi: carpan = 25

        for i in range(5):
            y_coin, d_coin = secilenler[i], secilenler[i+5]
            yukselenler.append({
                "coin": y_coin, "fiyat": random.uniform(0.5, 200), "yuzde": round(random.uniform(1.5 * carpan, 5.0 * carpan), 2),
                "hacim": f"${round(random.uniform(10 * carpan, 500 * carpan), 1)}M", "ai_yon": "LONG 🟢", "ai_kaldirac": random.choice([5, 10, 20]), "ai_guven": random.randint(75, 98)
            })
            dusenler.append({
                "coin": d_coin, "fiyat": random.uniform(0.5, 200), "yuzde": round(random.uniform(-5.0 * carpan, -1.5 * carpan), 2),
                "hacim": f"${round(random.uniform(5 * carpan, 300 * carpan), 1)}M", "ai_yon": "SHORT 🔴", "ai_kaldirac": random.choice([5, 10]), "ai_guven": random.randint(70, 95)
            })
        yukselenler.sort(key=lambda x: x["yuzde"], reverse=True)
        dusenler.sort(key=lambda x: x["yuzde"]) 
        return yukselenler, dusenler

    yukselenler_sutunu = ft.Column(spacing=10, expand=True)
    dusenler_sutunu = ft.Column(spacing=10, expand=True)

    def liste_karti_uret(veri, is_gainer):
        ana_renk, isaret = ("#10B981", "+") if is_gainer else ("#EF4444", "")
        return ft.Container(
            content=ft.Row([
                ft.Column([ft.Text(veri["coin"], weight="900", size=16, color="white"), ft.Text(f"${veri['fiyat']:,.4f}", color="#A0A0A5", size=12)], expand=1),
                ft.Column([ft.Text("Hacim", color="#737373", size=10), ft.Text(veri["hacim"], color="white", size=12, weight="bold")], alignment=ft.MainAxisAlignment.CENTER, expand=1),
                ft.Container(content=ft.Text(f"{isaret}%{veri['yuzde']}", color=ana_renk, weight="bold", size=14), alignment=ft.Alignment(1, 0), expand=1)
            ]),
            bgcolor="#050507", border=ft.Border(left=ft.BorderSide(4, ana_renk)), border_radius=6, padding=15
        )

    def sayfalari_guncelle(zaman_dilimi):
        y, d = ai_veri_uret(zaman_dilimi)
        yukselenler_sutunu.controls.clear()
        dusenler_sutunu.controls.clear()
        for v in y: yukselenler_sutunu.controls.append(liste_karti_uret(v, True))
        for v in d: dusenler_sutunu.controls.append(liste_karti_uret(v, False))
        page.update()

    zaman_dropdown = ft.Dropdown(
        options=[
            ft.dropdown.Option("5 Dakikalık"), ft.dropdown.Option("15 Dakikalık"), ft.dropdown.Option("1 Saatlik"), ft.dropdown.Option("1 Günlük")
        ],
        value="1 Saatlik", width=180, bgcolor="#0A0A0E", border_color="#1A1A24", color="white"
    )
    
    def dropdown_degisti(e):
        sayfalari_guncelle(e.control.value)
    zaman_dropdown.on_change = dropdown_degisti

    ust_panel = ft.Row([
        ft.Row([ft.Text("🏆", size=24), ft.Text("AI DESTEKLİ TOP 5", size=20, weight="900", color="white")]),
        ft.Row([
            # HATA KÖKTEN ÇÖZÜLDÜ: Flet ikonu yerine Emoji eklendi
            ft.Text("🔄", size=16),
            ft.Text("Canlı", color="#00ffcc", size=12, weight="bold"),
            zaman_dropdown
        ])
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    ana_icerik = ft.Container(
        content=ft.Column([
            ust_panel, ft.Divider(color="#1A1A24"), ft.Container(height=10),
            ft.Row([
                ft.Column([ft.Container(content=ft.Text("🚀 EN ÇOK YÜKSELENLER", color="#10B981", weight="bold"), bgcolor="#0A0A0E", padding=10, border_radius=6, width=float('inf')), yukselenler_sutunu], expand=1),
                ft.Container(width=10),
                ft.Column([ft.Container(content=ft.Text("💥 EN ÇOK DÜŞENLER", color="#EF4444", weight="bold"), bgcolor="#0A0A0E", padding=10, border_radius=6, width=float('inf')), dusenler_sutunu], expand=1)
            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START, expand=True)
        ], expand=True), bgcolor="#030304", padding=20, expand=True
    )

    def otomatik_yenile():
        while sayfa_aktif[0]:
            time.sleep(5)
            if sayfa_aktif[0]:
                sayfalari_guncelle(zaman_dropdown.value)

    threading.Thread(target=otomatik_yenile, daemon=True).start()

    def guvenli_cikis():
        sayfa_aktif[0] = False
        geri_don_fonksiyonu()

    sayfalari_guncelle(zaman_dropdown.value)

    return ft.Container(
        content=ft.Column([
            ft.Row([ft.TextButton(content=ft.Text("⬅️ Qypees Ana Ekrana Dön", color="#00ffcc"), on_click=lambda e: guvenli_cikis())]),
            ana_icerik
        ], expand=True), bgcolor="#030304", padding=10, expand=True
    )