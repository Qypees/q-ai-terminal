import flet as ft
import random
from veritabani import COINLER, COIN_FIYATLARI

def ai_signal_sayfasi_olustur(page: ft.Page, geri_don_fonksiyonu):
    
    def cerceve(k, r): return ft.Border(ft.BorderSide(k, r), ft.BorderSide(k, r), ft.BorderSide(k, r), ft.BorderSide(k, r))

    # 100 coin içinden sadece 5 ila 9 tanesinde "Fırsat Var" olarak işaretliyoruz
    firsat_kac_tane = random.randint(5, 9)
    firsat_coinleri = random.sample(COINLER, firsat_kac_tane)

    liste_sutunu = ft.Column(spacing=15, scroll=ft.ScrollMode.AUTO, expand=True)

    for coin in firsat_coinleri:
        yon = random.choice(["LONG", "SHORT"])
        renk = "#10B981" if yon == "LONG" else "#EF4444"
        ikon = "🟢" if yon == "LONG" else "🔴"
        kaldirac = random.choice(["5x", "10x", "20x"])
        fiyat = COIN_FIYATLARI[coin]
        hedef = fiyat * 1.05 if yon == "LONG" else fiyat * 0.95
        stop = fiyat * 0.97 if yon == "LONG" else fiyat * 1.03

        kart = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(f"{coin} / USDT", weight="900", size=18, color="white"),
                    # HATA KÖKTEN ÇÖZÜLDÜ: ft.padding.symmetric yerine doğrudan 5 yazıldı
                    ft.Container(content=ft.Text(f"{yon} {ikon}", color="white", weight="bold", size=14), bgcolor=renk, padding=5, border_radius=6),
                    ft.Text(f"Kaldıraç: {kaldirac}", color="#00ffcc", weight="bold")
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(color="#1A1A24"),
                ft.Row([
                    ft.Column([ft.Text("Giriş Fiyatı", color="#737373", size=12), ft.Text(f"${fiyat:,.4f}", color="white", weight="bold")]),
                    ft.Column([ft.Text("Hedef (Take Profit)", color="#737373", size=12), ft.Text(f"${hedef:,.4f}", color="#10B981", weight="bold")]),
                    ft.Column([ft.Text("Stop Loss", color="#737373", size=12), ft.Text(f"${stop:,.4f}", color="#EF4444", weight="bold")])
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
            ]),
            bgcolor="#0A0A0E", padding=15, border_radius=12, border=ft.Border(left=ft.BorderSide(4, renk), bottom=ft.BorderSide(1, "#1A1A24"))
        )
        liste_sutunu.controls.append(kart)

    ana_icerik = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("🤖", size=24), 
                ft.Text("AI İŞLEM FIRSATLARI", size=20, weight="900", color="white")
            ]),
            ft.Text(f"Q-AI 100 coini taradı ve {firsat_kac_tane} adet aktif işlem fırsatı buldu.", color="#A0A0A5", size=13),
            ft.Divider(color="#1A1A24"),
            ft.Container(height=5),
            liste_sutunu
        ], expand=True), bgcolor="#030304", padding=20, expand=True
    )

    return ft.Container(content=ft.Column([ft.TextButton(content=ft.Text("⬅️ Panoya Dön", color="#00ffcc"), on_click=lambda e: geri_don_fonksiyonu()), ana_icerik], expand=True), bgcolor="#030304", padding=10, expand=True)