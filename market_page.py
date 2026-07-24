import flet as ft
import random
import threading
import time
from veritabani import COINLER, COIN_FIYATLARI

def piyasa_sayfasi_olustur(page: ft.Page, geri_don_fonksiyonu):
    sayfa_aktif = [True] 
    
    # 100 coini ve yapay zeka yorumlarını hafızaya al
    piyasa_verileri = []
    yorumlar = [
        "Güçlü alım bölgesinde, balina cüzdanları hareketli.",
        "Direnç noktasını kırmak üzere, hacim onay veriyor.",
        "Aşırı alım (Overbought) durumunda, düzeltme gelebilir.",
        "Akümülasyon evresinde, sabırlı olunmalı.",
        "MACD kesişimi aşağı yönlü, satış baskısı artabilir."
    ]

    for coin in COINLER:
        yon = random.choice(["LONG 🟢", "SHORT 🔴", "YATAY 🟡"])
        piyasa_verileri.append({
            "coin": coin, "fiyat": COIN_FIYATLARI[coin], 
            "degisim": random.uniform(-8.0, 8.0), "hacim": random.randint(10, 2500),
            "acik": False, 
            "ai_yon": yon,
            "ai_yorum": random.choice(yorumlar)
        })

    siralama = {"aktif": "hacim", "ters": True} 

    def siralama_ayarla(olcut):
        if siralama["aktif"] == olcut: siralama["ters"] = not siralama["ters"]
        else: siralama["aktif"] = olcut; siralama["ters"] = True
        verileri_guncelle()

    def kutu_tikla(e):
        tiklanan_coin = e.control.data
        for v in piyasa_verileri:
            if v["coin"] == tiklanan_coin:
                v["acik"] = not v["acik"]
        verileri_guncelle()

    liste_sutunu = ft.ListView(spacing=12, expand=True)

    def verileri_guncelle():
        for veri in piyasa_verileri:
            if veri["coin"] not in ["USDT", "USDC", "DAI"]:
                veri["fiyat"] *= (1 + random.uniform(-0.5, 0.5) / 100)
                veri["degisim"] += random.uniform(-0.1, 0.1)
            veri["hacim"] += random.randint(-5, 5)

        if siralama["aktif"] == "fiyat": piyasa_verileri.sort(key=lambda x: x["fiyat"], reverse=siralama["ters"])
        elif siralama["aktif"] == "degisim": piyasa_verileri.sort(key=lambda x: x["degisim"], reverse=siralama["ters"])
        elif siralama["aktif"] == "hacim": piyasa_verileri.sort(key=lambda x: x["hacim"], reverse=siralama["ters"])

        liste_sutunu.controls.clear()
        
        ok_f = "⬇️" if siralama["aktif"]=="fiyat" and siralama["ters"] else "⬆️" if siralama["aktif"]=="fiyat" else "↕️"
        ok_d = "⬇️" if siralama["aktif"]=="degisim" and siralama["ters"] else "⬆️" if siralama["aktif"]=="degisim" else "↕️"
        ok_h = "⬇️" if siralama["aktif"]=="hacim" and siralama["ters"] else "⬆️" if siralama["aktif"]=="hacim" else "↕️"

        baslik = ft.Container(
            content=ft.Row([
                ft.Text("COIN / USDT", color="#737373", size=12, weight="bold", width=120),
                ft.Container(content=ft.Text(f"FİYAT {ok_f}", color="#00ffcc" if siralama["aktif"]=="fiyat" else "#737373", size=12, weight="bold"), width=120, on_click=lambda e: siralama_ayarla("fiyat"), ink=True),
                ft.Container(content=ft.Text(f"24S DEĞİŞİM {ok_d}", color="#00ffcc" if siralama["aktif"]=="degisim" else "#737373", size=12, weight="bold"), width=110, on_click=lambda e: siralama_ayarla("degisim"), ink=True),
                ft.Container(content=ft.Text(f"24S HACİM {ok_h}", color="#00ffcc" if siralama["aktif"]=="hacim" else "#737373", size=12, weight="bold"), on_click=lambda e: siralama_ayarla("hacim"), ink=True)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), padding=10
        )
        liste_sutunu.controls.append(baslik)

        for veri in piyasa_verileri:
            renk = "#10B981" if veri["degisim"] >= 0 else "#EF4444"
            isaret = "+" if veri["degisim"] >= 0 else ""
            fiyat_metni = f"${veri['fiyat']:,.2f}" if veri['fiyat'] > 1 else f"${veri['fiyat']:,.5f}"
            
            ana_satir = ft.Container(
                data=veri["coin"], on_click=kutu_tikla, 
                content=ft.Row([
                    ft.Text(f"{veri['coin']}", weight="900", size=18, color="white", width=120),
                    ft.Text(fiyat_metni, weight="bold", size=16, color=renk, width=120),
                    ft.Container(content=ft.Text(f"{isaret}{veri['degisim']:.2f}%", weight="bold", size=14, color="white"), bgcolor=renk, padding=5, border_radius=6, width=80, alignment=ft.Alignment(0, 0)),
                    ft.Text(f"${int(veri['hacim'])}M", color="#A0A0A5", size=14, weight="bold")
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=10
            )

            # HATA KÖKTEN ÇÖZÜLDÜ: margin=ft.margin.only(...) yerine doğrudan margin=5 yazıldı
            ai_kutusu = ft.Container(
                content=ft.Row([
                    ft.Text("🤖 Q-AI:", color="#00ffcc", weight="bold"),
                    ft.Text(f"Yön: {veri['ai_yon']} | Analiz: {veri['ai_yorum']}", color="#A0A0A5", size=13)
                ]),
                visible=veri["acik"], 
                bgcolor="#050507", padding=10, border_radius=8, margin=5,
                border=ft.Border(left=ft.BorderSide(3, "#00ffcc"))
            )
            
            kart_tam = ft.Container(
                content=ft.Column([ana_satir, ai_kutusu], spacing=0),
                bgcolor="#0A0A0E", padding=5, border_radius=8, 
                border=ft.Border(left=ft.BorderSide(3, renk), bottom=ft.BorderSide(1, "#1A1A24")), 
                shadow=[ft.BoxShadow(blur_radius=10, color=renk, spread_radius=-8)]
            )
            liste_sutunu.controls.append(kart_tam)
        
        try: page.update()
        except: pass

    def otomatik_yenile():
        while sayfa_aktif[0]:
            time.sleep(2.5) 
            if sayfa_aktif[0]: verileri_guncelle()

    threading.Thread(target=otomatik_yenile, daemon=True).start()

    def guvenli_cikis():
        sayfa_aktif[0] = False
        geri_don_fonksiyonu()

    verileri_guncelle() 

    ana_icerik = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Row([ft.Text("🔴", size=20), ft.Text("CANLI PİYASA", size=28, weight="900", color="white")]),
                ft.Row([ft.Text("🔄", size=16), ft.Text("Akış Aktif", color="#00ffcc", size=12, weight="bold")])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Text("Detaylı yapay zeka analizi için varlıkların üzerine tıklayın.", color="#737373", size=12),
            ft.Divider(color="#1A1A24"), ft.Container(height=5), liste_sutunu
        ], expand=True), padding=20, expand=True, bgcolor="#030304"
    )

    return ft.Container(content=ft.Column([ft.TextButton(content=ft.Text("⬅️ Panoya Dön", color="white"), on_click=lambda e: guvenli_cikis()), ana_icerik], expand=True), bgcolor="#030304", expand=True)