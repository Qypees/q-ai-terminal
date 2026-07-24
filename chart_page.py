import flet as ft

def grafik_sayfasi_olustur(page: ft.Page, geri_don_fonksiyonu):
    
    # --- YENİ NESİL ÇERÇEVE MOTORU (FLET 0.80.0 UYUMLU) ---
    def cerceve_olustur(kalinlik, renk):
        kenar = ft.BorderSide(kalinlik, renk)
        return ft.Border(top=kenar, right=kenar, bottom=kenar, left=kenar)

    durum = {"coin": "", "zaman": ""}
    
    ana_icerik = ft.AnimatedSwitcher(
        content=ft.Container(),
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=400,
        reverse_duration=400,
        switch_in_curve=ft.AnimationCurve.DECELERATE,
        switch_out_curve=ft.AnimationCurve.DECELERATE,
    )

    # ==========================================
    # ADIM 1: SADECE ARAMA ÇUBUĞU 
    # ==========================================
    def goster_adim_1(e=None):
        arama_input = ft.TextField(
            label="Örn: BTC, ETH, SOL",
            width=400,
            border_color="#00ffcc",
            color="white",
            text_align=ft.TextAlign.CENTER,
            text_size=24,
            autofocus=True,
            border_radius=16
        )
        
        def ileri_git(e):
            if arama_input.value:
                durum["coin"] = arama_input.value.upper()
                goster_adim_2()
            else:
                page.snack_bar.content.value = "Lütfen bir coin girin!"
                page.snack_bar.bgcolor = "red"
                page.snack_bar.open = True
                page.update()

        kutu = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("🔍", size=70),
                    ft.Text("Q-AI GRAFİK MOTORU", size=26, weight="900", color="white"),
                    ft.Text("Analiz etmek istediğiniz varlığı girerek başlayın.", color="#737373", size=14),
                    ft.Container(height=25),
                    arama_input,
                    ft.Container(height=15),
                    # HATA DÜZELTİLDİ: text="İleri" yerine content=ft.Text() kullanıldı
                    ft.ElevatedButton(
                        content=ft.Text("İleri ➔", color="black", weight="900", size=16),
                        style=ft.ButtonStyle(bgcolor="#00ffcc"),
                        width=400, 
                        height=55, 
                        on_click=ileri_git
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            alignment=ft.Alignment(0, 0),
            expand=True
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
            # HATA DÜZELTİLDİ: text=z yerine content=ft.Text(z) kullanıldı
            butonlar.append(
                ft.ElevatedButton(
                    content=ft.Text(z, color="white", weight="bold", size=16),
                    data=z,
                    width=120,
                    height=60,
                    style=ft.ButtonStyle(
                        bgcolor="#0A0A0E",
                        shape=ft.RoundedRectangleBorder(radius=12),
                        side=ft.BorderSide(1, "#1A1A24")
                    ),
                    on_click=zaman_sec
                )
            )
            
        kutu = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(f"Hedef: {durum['coin']}", size=32, weight="900", color="#00ffcc"),
                    ft.Text("Q-AI'nin hangi zaman dilimini analiz etmesini istersiniz?", color="#737373", size=15),
                    ft.Container(height=35),
                    ft.Row(controls=butonlar, alignment=ft.MainAxisAlignment.CENTER, wrap=True, spacing=20),
                    ft.Container(height=50),
                    ft.TextButton(
                        content=ft.Text("🡄 Coin Değiştir", color="white70"), 
                        on_click=goster_adim_1
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            alignment=ft.Alignment(0, 0),
            expand=True
        )
        ana_icerik.content = kutu
        page.update()

    # ==========================================
    # ADIM 3: FİNAL (GRAFİK, YAPAY ZEKA VE HABERLER)
    # ==========================================
    def goster_adim_3(e=None):
        coin = durum["coin"]
        zaman = durum["zaman"]

        grafik_alani = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("📊", size=20),
                    ft.Text(f"{coin}/USDT - {zaman} Canlı Grafik", weight="900", color="white")
                ]),
                ft.Container(height=10),
                ft.Container(
                    content=ft.Text("TradingView API Bağlantısı Bekleniyor...\n(V1.1'de Gerçek Veri Akacak)", color="#333333", size=18, weight="bold", text_align="center"),
                    bgcolor="#050507",
                    border=cerceve_olustur(1, "#1A1A24"),
                    border_radius=12,
                    expand=True,
                    alignment=ft.Alignment(0, 0)
                )
            ], expand=True),
            height=300,
            padding=20,
            bgcolor="#0A0A0E",
            border=cerceve_olustur(1, "#1A1A24"),
            border_radius=16,
            shadow=[ft.BoxShadow(blur_radius=15, color="#000000", offset=ft.Offset(0, 5))]
        )

        ai_analiz_alani = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("🤖", size=20),
                    ft.Text("Q-AI KARAR MOTORU", weight="900", color="#00ffcc")
                ]),
                ft.Divider(color="#1A1A24"),
                ft.Row([ft.Text("YÖN:", color="#737373", size=13), ft.Text("LONG 🟢", weight="900", color="#10B981", size=16)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([ft.Text("KALDIRAÇ:", color="#737373", size=13), ft.Text("10x İzole", weight="bold", color="white")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([ft.Text("KAR AL (TEPE):", color="#737373", size=13), ft.Text("Üst Direnç Kırılımı", weight="bold", color="#F59E0B")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Row([ft.Text("STOP-LOSS:", color="#737373", size=13), ft.Text("%3 Alt Destek", weight="bold", color="#EF4444")], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(color="#1A1A24"),
                ft.Text("Gelişmiş AI Yorumu:", weight="bold", color="white", size=13),
                ft.Text(f"{coin} için {zaman} periyodunda MacD kesişimi ve güçlü hacim girişi tespit edildi. RSI 55 seviyesinde ve yukarı yönlü momentum destekleniyor. İşleme girmek için re-test (geri çekilme) beklenebilir.", color="#A0A0A5", size=12)
            ]),
            padding=20,
            bgcolor="#050507",
            border=cerceve_olustur(1, "#00ffcc"), 
            border_radius=16,
            shadow=[ft.BoxShadow(blur_radius=20, color="#00ffcc", offset=ft.Offset(0, 0))]
        )

        haber_alani = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("📰", size=20),
                    ft.Text(f"{coin} SON DAKİKA GELİŞMELERİ", weight="900", color="white")
                ]),
                ft.Divider(color="#1A1A24"),
                ft.ListTile(
                    leading=ft.Text("🟢", size=16),
                    title=ft.Text(f"Balinalar son 24 saatte yüklü miktarda {coin} biriktirdi.", color="white", size=13),
                    subtitle=ft.Text("3 dakika önce", color="#737373", size=11),
                    content_padding=0
                ),
                ft.ListTile(
                    leading=ft.Text("🟠", size=16),
                    title=ft.Text(f"{coin} geliştirici ekibinden kritik ağ güncellemesi duyurusu geldi.", color="white", size=13),
                    subtitle=ft.Text("1 saat önce", color="#737373", size=11),
                    content_padding=0
                )
            ]),
            padding=20,
            bgcolor="#0A0A0E",
            border=cerceve_olustur(1, "#1A1A24"),
            border_radius=16
        )

        kutu = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.TextButton(content=ft.Text("⬅️ Geri Dön", color="white"), on_click=goster_adim_2),
                    ft.Text("GRAFİK VE ANALİZ TERMİNALİ", size=18, weight="900", color="white")
                ], alignment=ft.MainAxisAlignment.START),
                ft.Container(height=10),
                
                grafik_alani,
                ft.Container(height=10),
                ai_analiz_alani,
                ft.Container(height=10),
                haber_alani
            ], scroll=ft.ScrollMode.AUTO), 
            expand=True,
            alignment=ft.Alignment(0, -1)
        )
        
        ana_icerik.content = kutu
        page.update()

    goster_adim_1()

    return ft.Container(
        content=ft.Column([
            ft.Row([
                ft.TextButton(content=ft.Text("🏠 Ana Panoya Dön", color="#00ffcc"), on_click=lambda e: geri_don_fonksiyonu())
            ]),
            ana_icerik
        ], expand=True),
        padding=20,
        expand=True,
        bgcolor="#030304"
    )