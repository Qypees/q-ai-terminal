import flet as ft
import random

# EĞER VERİTABANI DOSYASI VARSA İÇERİ AKTAR
try:
    import veritabani
except ImportError:
    veritabani = None

def grafik_sayfasi_olustur(page: ft.Page, geri_don_fonksiyonu):
    
    def cerceve_olustur(kalinlik, renk):
        kenar = ft.BorderSide(kalinlik, renk)
        return ft.Border(top=kenar, right=kenar, bottom=kenar, left=kenar)

    durum = {"coin": "", "zaman": ""}
    
    # SAYFALAR ARASI YUMUŞAK GEÇİŞ MOTORU
    ana_icerik = ft.AnimatedSwitcher(
        content=ft.Container(),
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=500,
        reverse_duration=500,
        switch_in_curve=ft.AnimationCurve.DECELERATE,
        switch_out_curve=ft.AnimationCurve.DECELERATE,
    )

    # BUTONLAR İÇİN HOVER (ÜZERİNE GELİNCE BÜYÜME) ANİMASYONU
    def animasyonlu_buton_hover(e):
        e.control.scale = 1.05 if e.data == "true" else 1.0
        e.control.update()

    # ==========================================
    # ADIM 1: AKILLI ARAMA ÇUBUĞU (ENTER DESTEKLİ)
    # ==========================================
    def goster_adim_1(e=None):
        def ileri_git(e):
            if arama_input.value.strip():
                durum["coin"] = arama_input.value.strip().upper()
                goster_adim_2()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("⚠️ Sistem Uyarısı: Lütfen geçerli bir coin girin!", weight="bold"), bgcolor="#EF4444")
                page.snack_bar.open = True
                page.update()

        arama_input = ft.TextField(
            label="Örn: BTC, ETH, SOL",
            width=400, border_color="#00ffcc", color="white",
            text_align=ft.TextAlign.CENTER, text_size=24,
            autofocus=True, border_radius=16,
            on_submit=ileri_git # ENTER TUŞU İLE GEÇİŞ EKLENDİ
        )

        ileri_butonu = ft.ElevatedButton(
            content=ft.Text("Hedefi Kilitle ➔", color="black", weight="900", size=16),
            style=ft.ButtonStyle(bgcolor="#00ffcc", shape=ft.RoundedRectangleBorder(radius=12)),
            width=400, height=55, on_click=ileri_git,
            animate_scale=ft.Animation(200, ft.AnimationCurve.DECELERATE)
        )
        ileri_butonu.on_hover = animasyonlu_buton_hover

        kutu = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("🎯", size=70),
                    ft.Text("Q-AI GRAFİK MOTORU", size=26, weight="900", color="white"),
                    ft.Text("Analiz edilecek kripto varlığı belirleyin. (Enter'a basarak ilerleyebilirsiniz)", color="#737373", size=13),
                    ft.Container(height=25),
                    arama_input,
                    ft.Container(height=15),
                    ileri_butonu
                ],
                alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            alignment=ft.Alignment(0, 0), expand=True
        )
        ana_icerik.content = kutu
        page.update()

    # ==========================================
    # ADIM 2: ZAMAN DİLİMİ (TIMEFRAME) SEÇİMİ
    # ==========================================
    def goster_adim_2(e=None):
        def zaman_sec(e):
            durum["zaman"] = e.control.data
            goster_adim_3()

        zamanlar = ["15m", "1h", "4h", "1d"]
        butonlar = []
        for z in zamanlar:
            btn = ft.ElevatedButton(
                content=ft.Text(z, color="white", weight="bold", size=16),
                data=z, width=120, height=60,
                style=ft.ButtonStyle(bgcolor="#0A0A0E", shape=ft.RoundedRectangleBorder(radius=12), side=ft.BorderSide(1, "#00ffcc")),
                on_click=zaman_sec, animate_scale=ft.Animation(200, ft.AnimationCurve.DECELERATE)
            )
            btn.on_hover = animasyonlu_buton_hover
            butonlar.append(btn)
            
        kutu = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(f"Hedef Kilitlendi: {durum['coin']}", size=32, weight="900", color="#00ffcc"),
                    ft.Text("Derin analiz için zaman dilimini (Timeframe) seçin.", color="#737373", size=15),
                    ft.Container(height=35),
                    ft.Row(controls=butonlar, alignment=ft.MainAxisAlignment.CENTER, wrap=True, spacing=20),
                    ft.Container(height=50),
                    ft.TextButton(content=ft.Text("🡄 Hedefi Değiştir", color="#A0A0A5"), on_click=goster_adim_1)
                ],
                alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            alignment=ft.Alignment(0, 0), expand=True
        )
        ana_icerik.content = kutu
        page.update()

    # ==========================================
    # ADIM 3: FİNAL (NATIVE SİMÜLASYON + TV KÖPRÜSÜ)
    # ==========================================
    def goster_adim_3(e=None):
        coin = durum["coin"]
        zaman = durum["zaman"]

        # 1. GERÇEKÇİ FİYAT VE HEDEF SİMÜLASYONU
        fiyat_veritabani = {"BTC": 64500.0, "ETH": 3450.0, "SOL": 145.0, "BNB": 580.0, "AVAX": 32.5, "XRP": 0.55}
        guncel_fiyat = fiyat_veritabani.get(coin, round(random.uniform(10.0, 500.0), 2))
        
        # Trend yönü (Yapay Zeka Yorumu için)
        trend_yonu = random.choice(["LONG 🟢", "LONG 🟢", "SHORT 🔴"]) 
        if "LONG" in trend_yonu:
            kar_al_fiyati = guncel_fiyat * 1.045
            stop_loss_fiyati = guncel_fiyat * 0.972
            ai_metin = f"{coin} için {zaman} periyodunda MacD kesişimi ve hacim artışı saptandı. Fiyat ${stop_loss_fiyati:,.2f} altına düşmezse hedef doğrudan ${kar_al_fiyati:,.2f} seviyesidir."
        else:
            kar_al_fiyati = guncel_fiyat * 0.955
            stop_loss_fiyati = guncel_fiyat * 1.028
            ai_metin = f"{coin} zayıflık gösteriyor. ${stop_loss_fiyati:,.2f} direnci aşılamazsa geri çekilme beklenebilir. İlk destek seviyesi ${kar_al_fiyati:,.2f} olacaktır."

        # 2. GERÇEKÇİ PİYASA (MUM) ANİMASYONU
        mumlar = []
        gecici_yukseklik = random.randint(50, 100)
        for _ in range(35):  
            # Mumların birbirine bağlı rastgele hareketi (Random Walk Algorithm)
            gecici_yukseklik += random.randint(-25, 25)
            gecici_yukseklik = max(20, min(180, gecici_yukseklik)) # Sınırlar içinde tut
            
            renk = "#00ffcc" if random.choice([True, False]) or "LONG" in trend_yonu else "#EF4444"
            
            mum = ft.Container(
                width=8, height=gecici_yukseklik, bgcolor=renk, border_radius=4,
                shadow=[ft.BoxShadow(blur_radius=10, color=renk, spread_radius=-3)],
                animate=ft.Animation(700, ft.AnimationCurve.EASE_OUT)
            )
            mumlar.append(mum)
            
        neon_grafik = ft.Row(controls=mumlar, alignment=ft.MainAxisAlignment.SPACE_EVENLY, vertical_alignment=ft.CrossAxisAlignment.END, expand=True)

        # 3. ASENKRON TRADINGVIEW BUTONU
        tv_zaman_haritasi = {"15m": "15", "1h": "60", "4h": "240", "1d": "D"}
        tv_param = tv_zaman_haritasi.get(zaman, "D")
        
        async def tv_linkini_ac(e):
            page.snack_bar = ft.SnackBar(ft.Text("⚡ Tarayıcı üzerinden TradingView başlatılıyor..."), bgcolor="#00ffcc")
            page.snack_bar.open = True
            page.update()
            await page.launch_url(f"https://www.tradingview.com/chart/?symbol=BINANCE:{coin}USDT&interval={tv_param}")
        
        tv_baglanti_butonu = ft.ElevatedButton(
            content=ft.Row([
                ft.Text("🚀", size=22),
                ft.Text("TRADINGVIEW'DE AÇ", weight="900", size=18, color="#050507")
            ], alignment=ft.MainAxisAlignment.CENTER),
            style=ft.ButtonStyle(
                bgcolor="#00ffcc", 
                shape=ft.RoundedRectangleBorder(radius=10),
                shadow_color="#00ffcc", elevation=10
            ),
            width=350, height=60,
            on_click=tv_linkini_ac,
            animate_scale=ft.Animation(200, ft.AnimationCurve.BOUNCE_OUT)
        )
        tv_baglanti_butonu.on_hover = animasyonlu_buton_hover

        grafik_alani = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("📈", size=24),
                    ft.Text(f"SİBERPUNK GRAFİK: {coin}/USDT | {zaman}", weight="900", color="white", size=18)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=10),
                
                ft.Stack([
                    ft.Container(
                        content=neon_grafik,
                        bgcolor="#0A0A0E", border=ft.Border(bottom=ft.BorderSide(2, "#1A1A24")),
                        expand=True, padding=20, alignment=ft.Alignment(0, 1),
                        opacity=0.4 
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Profesyonel çizim araçlarınız, indikatörleriniz ve kaydedilmiş", color="#A0A0A5", size=14),
                            ft.Text("şablonlarınıza erişmek için tam sürüme geçiş yapın.", color="#A0A0A5", size=14),
                            ft.Container(height=15),
                            tv_baglanti_butonu
                        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                        alignment=ft.Alignment(0, 0)
                    )
                ], expand=True)

            ], expand=True),
            expand=7, padding=20, bgcolor="#050507",
            border=cerceve_olustur(1, "#1A1A24"), border_radius=16,
            shadow=[ft.BoxShadow(blur_radius=20, color="#000000", offset=ft.Offset(0, 10))]
        )

        # 4. SAĞ PANEL: Q-AI ANALİZ VE DİNAMİK VERİLER
        ai_analiz_alani = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("🤖", size=18),
                    ft.Text("Q-AI İŞLEM SİNYALİ", weight="900", color="#00ffcc", size=14)
                ]),
                ft.Divider(color="#1A1A24"),
                ft.Row([ft.Text("GÜNCEL FİYAT:", color="#737373", size=12), ft.Text(f"${guncel_fiyat:,.2f}", weight="900", color="white", size=15)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([ft.Text("YÖN:", color="#737373", size=12), ft.Text(trend_yonu, weight="900", color="#10B981" if "LONG" in trend_yonu else "#EF4444", size=15)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([ft.Text("KALDIRAÇ:", color="#737373", size=12), ft.Text("10x İzole", weight="bold", color="white", size=12)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([ft.Text("KAR AL (TP):", color="#737373", size=12), ft.Text(f"${kar_al_fiyati:,.2f}", weight="900", color="#00ffcc", size=13)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([ft.Text("STOP (SL):", color="#737373", size=12), ft.Text(f"${stop_loss_fiyati:,.2f}", weight="900", color="#EF4444", size=13)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(color="#1A1A24"),
                ft.Text("Q-AI Yorumu:", weight="bold", color="white", size=12),
                ft.Text(ai_metin, color="#94A3B8", size=11, text_align=ft.TextAlign.JUSTIFY)
            ]),
            padding=20, bgcolor="#0A0A0E",
            border=cerceve_olustur(1, "#00ffcc" if "LONG" in trend_yonu else "#EF4444"), border_radius=16,
            shadow=[ft.BoxShadow(blur_radius=20, color="#00ffcc" if "LONG" in trend_yonu else "#EF4444", spread_radius=-5)]
        )

        haber_alani = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("📰", size=18),
                    ft.Text(f"{coin} CANLI AKIŞ", weight="900", color="white", size=14)
                ]),
                ft.Divider(color="#1A1A24"),
                ft.ListTile(leading=ft.Text("🟢", size=14), title=ft.Text(f"Büyük cüzdanlardan {coin} transferi saptandı.", color="#E2E8F0", size=12), subtitle=ft.Text("3 dk önce", color="#64748B", size=10), content_padding=0),
                ft.ListTile(leading=ft.Text("🟠", size=14), title=ft.Text(f"{coin} ağında hacim dalgalanması yaşanıyor.", color="#E2E8F0", size=12), subtitle=ft.Text("1 sa önce", color="#64748B", size=10), content_padding=0)
            ]),
            padding=20, bgcolor="#0A0A0E",
            border=cerceve_olustur(1, "#1A1A24"), border_radius=16, expand=True
        )
        
        sag_panel = ft.Column([ai_analiz_alani, ft.Container(height=10), haber_alani], expand=3)

        kutu = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.TextButton(
                        content=ft.Row([ft.Text("⬅️", size=16), ft.Text("Parametreleri Değiştir", color="white", weight="bold")]),
                        on_click=goster_adim_2, style=ft.ButtonStyle(overlay_color="#1A1A24")
                    ),
                    ft.Text("TERMİNAL KONTROL MERKEZİ", size=16, weight="900", color="#737373")
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=15),
                
                ft.Row([grafik_alani, sag_panel], expand=True, vertical_alignment=ft.CrossAxisAlignment.START, spacing=20)
                
            ]), 
            expand=True, alignment=ft.Alignment(0, -1)
        )
        
        ana_icerik.content = kutu
        page.update()

    # Uygulama açıldığında Adım 1'i başlat
    goster_adim_1()

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.TextButton(
                    content=ft.Row([ft.Text("🏠", size=16), ft.Text("Ana Panoya Dön", color="#00ffcc", weight="900")]), 
                    on_click=lambda e: geri_don_fonksiyonu()
                )
            ]),
            ana_icerik
        ], expand=True),
        padding=15, expand=True, bgcolor="#030304"
    )