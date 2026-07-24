import flet as ft
import random

def top5_sayfasi_olustur(page: ft.Page, geri_don_fonksiyonu):
    
    # ==========================================
    # ZIRHLI ÇERÇEVE MOTORU (Hata Engelliyici)
    # ==========================================
    def cerceve_olustur(kalinlik, renk):
        kenar = ft.BorderSide(kalinlik, renk)
        return ft.Border(top=kenar, right=kenar, bottom=kenar, left=kenar)

    # ==========================================
    # SAHTE AI VERİ MOTORU (Dinamik)
    # ==========================================
    coin_havuzu = ["BTC", "ETH", "SOL", "PEPE", "WIF", "AVAX", "LINK", "DOGE", "RNDR", "FET", "SHIB", "ARB", "OP", "SUI", "APT"]
    
    def ai_veri_uret(zaman_dilimi):
        secilenler = random.sample(coin_havuzu, 10)
        yukselenler = []
        dusenler = []
        
        # Zaman dilimine göre sahte hacim ve yüzde çarpanı
        carpan = 1
        if "15" in zaman_dilimi: carpan = 1.5
        elif "30" in zaman_dilimi: carpan = 2
        elif "Saat" in zaman_dilimi: carpan = 4
        elif "Gün" in zaman_dilimi: carpan = 10
        elif "Hafta" in zaman_dilimi: carpan = 25

        for i in range(5):
            # Yükselen Coin Üret
            y_coin = secilenler[i]
            y_fiyat = random.uniform(0.5, 200) if y_coin not in ["BTC", "ETH"] else random.uniform(2000, 65000)
            yukselenler.append({
                "coin": y_coin,
                "fiyat": y_fiyat,
                "yuzde": round(random.uniform(1.5 * carpan, 5.0 * carpan), 2),
                "hacim": f"${round(random.uniform(10 * carpan, 500 * carpan), 1)}M",
                "ai_yon": "LONG 🟢",
                "ai_kaldirac": random.choice([5, 10, 15, 20]),
                "ai_guven": random.randint(75, 98),
                "ai_neden": "Aşırı alım hacmi ve balina cüzdanlarında birikim tespit edildi."
            })
            
            # Düşen Coin Üret
            d_coin = secilenler[i+5]
            d_fiyat = random.uniform(0.5, 200) if d_coin not in ["BTC", "ETH"] else random.uniform(2000, 65000)
            dusenler.append({
                "coin": d_coin,
                "fiyat": d_fiyat,
                "yuzde": round(random.uniform(-5.0 * carpan, -1.5 * carpan), 2),
                "hacim": f"${round(random.uniform(5 * carpan, 300 * carpan), 1)}M",
                "ai_yon": "SHORT 🔴",
                "ai_kaldirac": random.choice([5, 10, 20]),
                "ai_guven": random.randint(70, 95),
                "ai_neden": "Kritik destek seviyesi kırıldı, algoritmik satış baskısı devam ediyor."
            })
            
        yukselenler.sort(key=lambda x: x["yuzde"], reverse=True)
        dusenler.sort(key=lambda x: x["yuzde"]) 
        return yukselenler, dusenler

    # ==========================================
    # POP-UP (AÇILIR PENCERE) - AI SİNYAL DETAYI
    # ==========================================
    dialog = ft.AlertDialog(modal=True, bgcolor="#0A0A0E")
    
    def kapat_dialog(e):
        dialog.open = False
        page.update()

    def ai_sinyal_goster(e, veri):
        ana_renk = "#10B981" if "LONG" in veri["ai_yon"] else "#EF4444"
        
        icerik = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("🤖 Q-AI İŞLEM ONAYI", color="#00ffcc", weight="900", size=18),
                    ft.IconButton(icon=ft.icons.CLOSE, icon_color="white", on_click=kapat_dialog)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(color="#1A1A24"),
                
                ft.Row([
                    ft.Text(f"{veri['coin']}/USDT", size=24, weight="900", color="white"),
                    ft.Container(
                        content=ft.Text(veri["ai_yon"], weight="bold", color="white"),
                        bgcolor=ana_renk, padding=6, border_radius=6
                    )
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Container(height=10),
                
                ft.Row([
                    ft.Column([ft.Text("Tavsiye Edilen Kaldıraç", color="#737373", size=12), ft.Text(f"{veri['ai_kaldirac']}X İZOLE", color="white", weight="bold", size=16)]),
                    ft.Column([ft.Text("AI Güven Skoru", color="#737373", size=12), ft.Text(f"%{veri['ai_guven']}", color=ana_renk, weight="bold", size=16)]),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                
                ft.Container(height=10),
                ft.Text("🧠 Algoritma Yorumu:", color="#00ffcc", size=12, weight="bold"),
                ft.Text(veri["ai_neden"], color="#A0A0A5", size=12, italic=True)
            ], width=350, height=220),
            padding=10
        )
        
        dialog.content = icerik
        page.dialog = dialog
        dialog.open = True
        page.update()

    # ==========================================
    # LİSTE OLUŞTURMA MOTORU
    # ==========================================
    yukselenler_sutunu = ft.Column(spacing=10, expand=True)
    dusenler_sutunu = ft.Column(spacing=10, expand=True)

    def liste_karti_uret(veri, is_gainer):
        ana_renk = "#10B981" if is_gainer else "#EF4444"
        isaret = "+" if is_gainer else ""
        
        kart = ft.Container(
            content=ft.Row([
                # Sol: Coin ve Fiyat
                ft.Column([
                    ft.Text(veri["coin"], weight="900", size=16, color="white"),
                    ft.Text(f"${veri['fiyat']:,.4f}".rstrip('0').rstrip('.'), color="#A0A0A5", size=12)
                ], spacing=2, expand=1),
                
                # Orta: Hacim
                ft.Column([
                    ft.Text("Hacim", color="#737373", size=10),
                    ft.Text(veri["hacim"], color="white", size=12, weight="bold")
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=0, expand=1),
                
                # Sağ: Yüzde
                ft.Container(
                    content=ft.Text(f"{isaret}%{veri['yuzde']}", color=ana_renk, weight="bold", size=14),
                    alignment=ft.Alignment(1, 0), # HATA DÜZELTİLDİ: Matematiksel koordinat (Sağ Merkez) kullanıldı
                    expand=1
                )
            ]),
            bgcolor="#050507",
            border=ft.Border(left=ft.BorderSide(4, ana_renk)), 
            border_radius=6,
            padding=15,
            ink=True, 
            on_click=lambda e: ai_sinyal_goster(e, veri)
        )
        return kart

    def sayfalari_guncelle(zaman_dilimi):
        yukselen_veriler, dusen_veriler = ai_veri_uret(zaman_dilimi)
        
        yukselenler_sutunu.controls.clear()
        dusenler_sutunu.controls.clear()
        
        for v in yukselen_veriler: yukselenler_sutunu.controls.append(liste_karti_uret(v, True))
        for v in dusen_veriler: dusenler_sutunu.controls.append(liste_karti_uret(v, False))
        
        page.update()

    # ==========================================
    # ÜST KONTROL PANELİ
    # ==========================================
    zaman_dropdown = ft.Dropdown(
        options=[
            ft.dropdown.Option("5 Dakikalık"),
            ft.dropdown.Option("15 Dakikalık"),
            ft.dropdown.Option("30 Dakikalık"),
            ft.dropdown.Option("1 Saatlik"),
            ft.dropdown.Option("4 Saatlik"),
            ft.dropdown.Option("1 Günlük"),
            ft.dropdown.Option("2 Haftalık"),
        ],
        value="1 Saatlik",
        width=200,
        bgcolor="#0A0A0E",
        border_color="#1A1A24",
        color="white"
    )
    zaman_dropdown.on_change = lambda e: sayfalari_guncelle(e.control.value)

    ust_panel = ft.Row([
        ft.Row([
            ft.Text("🏆", size=24),
            ft.Text("AI DESTEKLİ TOP 5", size=20, weight="900", color="white")
        ]),
        zaman_dropdown
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    # ==========================================
    # ANA İSKELET (Yükselenler ve Düşenler Yan Yana)
    # ==========================================
    ana_icerik = ft.Container(
        content=ft.Column([
            ust_panel,
            ft.Divider(color="#1A1A24"),
            ft.Container(height=10),
            
            ft.Row([
                # Yükselenler Kolonu
                ft.Column([
                    ft.Container(
                        content=ft.Text("🚀 EN ÇOK YÜKSELENLER", color="#10B981", weight="bold"),
                        bgcolor="#0A0A0E", padding=10, border_radius=6, border=cerceve_olustur(1, "#1A1A24"), width=float('inf')
                    ),
                    yukselenler_sutunu
                ], expand=1),
                
                ft.Container(width=10), 
                
                # Düşenler Kolonu
                ft.Column([
                    ft.Container(
                        content=ft.Text("💥 EN ÇOK DÜŞENLER", color="#EF4444", weight="bold"),
                        bgcolor="#0A0A0E", padding=10, border_radius=6, border=cerceve_olustur(1, "#1A1A24"), width=float('inf')
                    ),
                    dusenler_sutunu
                ], expand=1)
                
            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START, expand=True)
            
        ], expand=True),
        bgcolor="#030304", padding=20, expand=True
    )

    # İlk verileri yükle
    sayfalari_guncelle("1 Saatlik")

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.TextButton(
                    content=ft.Text("⬅️ Qypees Ana Ekrana Dön", color="#00ffcc"), 
                    on_click=lambda e: geri_don_fonksiyonu()
                )
            ]),
            ana_icerik
        ], expand=True),
        bgcolor="#030304", padding=10, expand=True
    )