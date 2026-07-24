import flet as ft
import random
import threading
import time

def piyasa_sayfasi_olustur(page: ft.Page, geri_don_fonksiyonu):
    sayfa_aktif = [True] 

    def cerceve(k, r): return ft.Border(ft.BorderSide(k, r), ft.BorderSide(k, r), ft.BorderSide(k, r), ft.BorderSide(k, r))
    
    coinler = ["BTC", "ETH", "SOL", "BNB", "XRP", "DOGE", "ADA", "AVAX", "LINK", "DOT", "MATIC", "SHIB", "LTC", "TRX", "NEAR", "APT", "SUI", "ARB", "OP", "FET", "RNDR", "PEPE", "WIF"]
    
    # 1. ADIM: KALICI VERİ TABANI OLUŞTUR
    # Sıralamanın sapıtmaması için veriler sürekli baştan yaratılmayacak, ufak dalgalanacak
    piyasa_verileri = []
    baslangic_fiyatlari = {
        "BTC": 64500.0, "ETH": 3100.0, "SOL": 145.0, "BNB": 580.0, "XRP": 0.60, 
        "DOGE": 0.15, "ADA": 0.45, "AVAX": 35.0, "LINK": 14.0, "DOT": 7.0, 
        "MATIC": 0.70, "SHIB": 0.000025, "LTC": 85.0, "TRX": 0.11, "NEAR": 6.5,
        "APT": 9.0, "SUI": 1.2, "ARB": 1.1, "OP": 2.5, "FET": 2.1, "RNDR": 8.5, "PEPE": 0.000008, "WIF": 2.8
    }
    
    for coin in coinler:
        piyasa_verileri.append({
            "coin": coin,
            "fiyat": baslangic_fiyatlari[coin],
            "degisim": random.uniform(-8.0, 8.0),
            "hacim": random.randint(50, 2000)
        })

    # SIRALAMA HAFIZASI (Varsayılan: Hacme göre büyükten küçüğe)
    siralama = {"aktif": "hacim", "ters": True} 

    def siralama_ayarla(olcut):
        # Aynı başlığa bir daha tıklarsa yönü değiştir, farklıysa yeni ölçütü seç
        if siralama["aktif"] == olcut:
            siralama["ters"] = not siralama["ters"]
        else:
            siralama["aktif"] = olcut
            siralama["ters"] = True
        verileri_guncelle()

    liste_sutunu = ft.Column(spacing=12, expand=True, scroll=ft.ScrollMode.AUTO)

    def verileri_guncelle():
        # Verileri Gerçekçi Dalgalandır (Arka Plan Motoru için)
        for veri in piyasa_verileri:
            veri["fiyat"] *= (1 + random.uniform(-0.5, 0.5) / 100)
            veri["degisim"] += random.uniform(-0.1, 0.1)
            veri["hacim"] += random.randint(-5, 5)
            if veri["hacim"] < 1: veri["hacim"] = 1 # Hacim eksiye düşmesin

        # VERİLERİ SIRALA (Python sort fonksiyonu)
        if siralama["aktif"] == "fiyat":
            piyasa_verileri.sort(key=lambda x: x["fiyat"], reverse=siralama["ters"])
        elif siralama["aktif"] == "degisim":
            piyasa_verileri.sort(key=lambda x: x["degisim"], reverse=siralama["ters"])
        elif siralama["aktif"] == "hacim":
            piyasa_verileri.sort(key=lambda x: x["hacim"], reverse=siralama["ters"])

        liste_sutunu.controls.clear()
        
        # SIRALAMA OKLARI (UI)
        ok_fiyat = "⬇️" if siralama["aktif"]=="fiyat" and siralama["ters"] else "⬆️" if siralama["aktif"]=="fiyat" else "↕️"
        ok_degisim = "⬇️" if siralama["aktif"]=="degisim" and siralama["ters"] else "⬆️" if siralama["aktif"]=="degisim" else "↕️"
        ok_hacim = "⬇️" if siralama["aktif"]=="hacim" and siralama["ters"] else "⬆️" if siralama["aktif"]=="hacim" else "↕️"

        baslik = ft.Container(
            content=ft.Row([
                ft.Text("COIN / USDT", color="#737373", size=12, weight="bold", width=120),
                
                # TIKLANABİLİR BAŞLIKLAR
                ft.Container(content=ft.Text(f"FİYAT {ok_fiyat}", color="#00ffcc" if siralama["aktif"]=="fiyat" else "#737373", size=12, weight="bold"), width=120, on_click=lambda e: siralama_ayarla("fiyat"), ink=True),
                ft.Container(content=ft.Text(f"24S DEĞİŞİM {ok_degisim}", color="#00ffcc" if siralama["aktif"]=="degisim" else "#737373", size=12, weight="bold"), width=110, on_click=lambda e: siralama_ayarla("degisim"), ink=True),
                ft.Container(content=ft.Text(f"24S HACİM {ok_hacim}", color="#00ffcc" if siralama["aktif"]=="hacim" else "#737373", size=12, weight="bold"), on_click=lambda e: siralama_ayarla("hacim"), ink=True)
                
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=10
        )
        liste_sutunu.controls.append(baslik)

        # LİSTEYİ EKRANA ÇİZ
        for veri in piyasa_verileri:
            renk = "#10B981" if veri["degisim"] >= 0 else "#EF4444"
            isaret = "+" if veri["degisim"] >= 0 else ""
            fiyat_metni = f"${veri['fiyat']:,.2f}" if veri['fiyat'] > 1 else f"${veri['fiyat']:,.5f}"
            
            kart = ft.Container(
                content=ft.Row([
                    ft.Text(f"{veri['coin']}", weight="900", size=18, color="white", width=120),
                    ft.Text(fiyat_metni, weight="bold", size=16, color=renk, width=120),
                    ft.Container(
                        content=ft.Text(f"{isaret}{veri['degisim']:.2f}%", weight="bold", size=14, color="white"),
                        bgcolor=renk, 
                        padding=5, 
                        border_radius=6, width=80, 
                        alignment=ft.Alignment(0, 0)
                    ),
                    ft.Text(f"${int(veri['hacim'])}M", color="#A0A0A5", size=14, weight="bold")
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                bgcolor="#0A0A0E",
                padding=15,
                border_radius=8,
                border=ft.Border(left=ft.BorderSide(3, renk), bottom=ft.BorderSide(1, "#1A1A24")),
                shadow=[ft.BoxShadow(blur_radius=10, color=renk, spread_radius=-8)]
            )
            liste_sutunu.controls.append(kart)
        
        try:
            page.update()
        except:
            pass

    def otomatik_yenile():
        while sayfa_aktif[0]:
            time.sleep(2.5) 
            if sayfa_aktif[0]:
                verileri_guncelle()

    threading.Thread(target=otomatik_yenile, daemon=True).start()

    def guvenli_cikis():
        sayfa_aktif[0] = False
        geri_don_fonksiyonu()

    verileri_guncelle() 

    ana_icerik = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Row([ft.Text("🔴", size=20), ft.Text("CANLI PİYASA", size=28, weight="900", color="white")]),
                ft.Row([ft.Text("🔄 Canlı Akış Aktif", color="#00ffcc", size=12, weight="bold")])
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(color="#1A1A24"),
            ft.Container(height=10),
            liste_sutunu
        ], expand=True),
        padding=20, expand=True, bgcolor="#030304"
    )

    return ft.Container(
        content=ft.Column([
            ft.TextButton(content=ft.Text("⬅️ Panoya Dön", color="white"), on_click=lambda e: guvenli_cikis()),
            ana_icerik
        ], expand=True),
        bgcolor="#030304", expand=True
    )