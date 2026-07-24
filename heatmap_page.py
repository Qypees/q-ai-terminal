import flet as ft
import random

def isi_haritasi_sayfasi_olustur(page: ft.Page, geri_don_fonksiyonu):
    def cerceve(k, r): return ft.Border(ft.BorderSide(k, r), ft.BorderSide(k, r), ft.BorderSide(k, r), ft.BorderSide(k, r))
    MERKEZ, G_GENISLIK, G_YUKSEKLIK = ft.Alignment(0, 0), 950, 450
    coin_havuzu = ["BTC", "ETH", "SOL", "XRP", "ADA", "AVAX", "LINK", "DOT", "MATIC", "DOGE", "SHIB", "PEPE", "WIF", "RNDR", "FET", "AGIX", "OP", "ARB", "SUI", "APT"]

    def ai_rsi_uret(zaman):
        vol = 5 if "Dakika" in zaman else 15
        return [{"coin": c, "rsi": max(20, min(80, 50 + random.uniform(-vol*2, vol*2))), "x": max(10, min(G_GENISLIK-30, i*(G_GENISLIK/len(coin_havuzu)) + random.uniform(-10, 10)))} for i, c in enumerate(coin_havuzu)]

    grafik_katmani = ft.Stack(width=G_GENISLIK, height=G_YUKSEKLIK)

    def grafigi_ciz(veriler):
        grafik_katmani.controls.clear()
        bolgeler = [{"isim": "OVERBOUGHT", "c1": "#2e080e", "c2": "transparent", "y": 0, "h": 75, "tc": "#ef4444"}, {"isim": "OVERSOLD", "c1": "transparent", "c2": "#022c22", "y": 375, "h": 75, "tc": "#10b981"}]
        
        for b in bolgeler:
            grafik_katmani.controls.append(ft.Container(top=b["y"], left=0, width=G_GENISLIK, height=b["h"], gradient=ft.LinearGradient(begin=ft.Alignment(0,-1), end=ft.Alignment(0,1), colors=[b["c1"], b["c2"]])))
            grafik_katmani.controls.append(ft.Container(top=b["y"]+30, left=G_GENISLIK-120, content=ft.Text(b["isim"], color=b["tc"], weight="bold", opacity=0.6)))

        orta_y = G_YUKSEKLIK / 2 
        grafik_katmani.controls.append(ft.Container(top=orta_y, left=0, width=G_GENISLIK, height=1, bgcolor="#737373", opacity=0.3))

        for v in veriler:
            y_pos = G_YUKSEKLIK - ((v["rsi"] - 20) / 60) * G_YUKSEKLIK
            renk = "#ef4444" if v["rsi"]>=70 else "#f472b6" if v["rsi"]>=60 else "#9ca3af" if v["rsi"]>=40 else "#34d399" if v["rsi"]>=30 else "#10b981"
            
            grafik_katmani.controls.append(ft.Container(top=min(y_pos, orta_y), left=v["x"]+4, width=1, height=abs(y_pos - orta_y), bgcolor=renk, opacity=0.2))
            grafik_katmani.controls.append(ft.Container(top=y_pos-10, left=v["x"]-10, content=ft.Column([ft.Text(v["coin"], size=9, color="white", weight="bold"), ft.Container(width=10, height=10, border_radius=10, bgcolor=renk, shadow=ft.BoxShadow(blur_radius=10, color=renk, spread_radius=2))], spacing=2, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)))
        page.update()

    zaman_dropdown = ft.Dropdown(options=[ft.dropdown.Option("15 Dakikalık"), ft.dropdown.Option("1 Saatlik"), ft.dropdown.Option("1 Günlük")], value="1 Saatlik", width=150, bgcolor="#0A0A0E", border_color="#1A1A24", color="white")
    zaman_dropdown.on_change = lambda e: grafigi_ciz(ai_rsi_uret(e.control.value))

    ana_icerik = ft.Container(content=ft.Column([
        ft.Row([ft.Text("🔥 GLOW ISI HARİTASI", size=24, weight="900", color="white"), zaman_dropdown], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        ft.Divider(color="#1A1A24"),
        ft.Container(content=grafik_katmani, bgcolor="#050507", border=cerceve(1, "#1A1A24"), border_radius=12, padding=10, width=G_GENISLIK+20, height=G_YUKSEKLIK+20, alignment=MERKEZ)
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER), bgcolor="#030304", padding=20, expand=True, alignment=ft.Alignment(0, -1))

    grafigi_ciz(ai_rsi_uret("1 Saatlik"))
    return ft.Container(content=ft.Column([ft.TextButton(content=ft.Text("⬅️ Panoya Dön", color="#00ffcc"), on_click=lambda e: geri_don_fonksiyonu()), ana_icerik], expand=True, scroll=ft.ScrollMode.AUTO), bgcolor="#030304", padding=10, expand=True)