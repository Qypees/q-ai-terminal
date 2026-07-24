import flet as ft
import random
import datetime

# SİSTEM HAFIZASI (Sayfalar arası geçişlerde verilerin silinmesini engeller)
aktif_pozisyonlar = []
spot_varliklar = [] # Yeni eklenen borsa varlıklarını tutar

def cuzdan_sayfasi_olustur(page: ft.Page, geri_don_fonksiyonu):
    
    def cerceve_olustur(kalinlik, renk):
        kenar = ft.BorderSide(kalinlik, renk)
        return ft.Border(top=kenar, right=kenar, bottom=kenar, left=kenar)

    # SAYFALAR ARASI YUMUŞAK GEÇİŞ MOTORU
    ana_icerik = ft.AnimatedSwitcher(
        content=ft.Container(),
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=400, reverse_duration=400,
        switch_in_curve=ft.AnimationCurve.DECELERATE,
        switch_out_curve=ft.AnimationCurve.DECELERATE,
    )

    def alt_kutu_olustur(baslik, alt_metin, fonk=None, neon_renk="#00ffcc"):
        kutu = ft.Container(
            content=ft.Column([
                ft.Text(baslik, size=22, weight="900", color="white"), 
                ft.Container(height=10),
                ft.Text(alt_metin, size=14, color="#A0A0A5", text_align="center") 
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            gradient=ft.LinearGradient(begin=ft.Alignment(-1, -1), end=ft.Alignment(1, 1), colors=["#0A0A0E", "#050507", "#030304"]),
            border=cerceve_olustur(1, "#1A1A24"), border_radius=16, padding=30, expand=True,
            shadow=[ft.BoxShadow(blur_radius=15, color="#000000", offset=ft.Offset(0, 10))],
            animate_scale=ft.Animation(300, ft.AnimationCurve.DECELERATE), on_click=fonk
        )
        def hover_olayi(e):
            e.control.scale = 1.03 if e.data == "true" else 1.0
            e.control.border = cerceve_olustur(1, neon_renk) if e.data == "true" else cerceve_olustur(1, "#1A1A24")
            e.control.shadow = [ft.BoxShadow(blur_radius=30, color=neon_renk, spread_radius=-5)] if e.data == "true" else [ft.BoxShadow(blur_radius=15, color="#000000", offset=ft.Offset(0, 10))]
            e.control.update()
        kutu.on_hover = hover_olayi
        return kutu

    # ==========================================
    # ALT SAYFA 1: SPOT CÜZDAN (DİNAMİK EKLEME VE SİLME)
    # ==========================================
    def goster_spot_cuzdan(e=None):
        spot_liste = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=10, expand=True)

        def listeyi_guncelle():
            # Silme fonksiyonu (Her bir elemanın index'ine göre siler)
            def varlik_sil(silinecek_index):
                spot_varliklar.pop(silinecek_index)
                listeyi_guncelle()
                page.snack_bar = ft.SnackBar(ft.Text("🗑️ Varlık cüzdandan başarıyla silindi!"), bgcolor="#EF4444")
                page.snack_bar.open = True
                page.update()

            spot_liste.controls.clear()
            if not spot_varliklar:
                spot_liste.controls.append(
                    ft.Container(content=ft.Text("Bakiye bulunmuyor. Sağ üstteki YENİ EKLE butonundan varlık ekleyin.", color="#737373", italic=True), padding=20)
                )
            else:
                for idx, varlik in enumerate(spot_varliklar):
                    ikon_sec = {"Binance": "🟨", "OKX": "⬛", "Gate.io": "🟥", "MEXC": "🟩", "KuCoin": "🟦"}.get(varlik['borsa'], "🪙")
                    kutu = ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(ikon_sec, size=24),
                                ft.Text(varlik['borsa'], weight="900", color="white", size=18),
                                ft.Container(expand=True),
                                ft.Text(f"${varlik['bakiye']}", weight="bold", color="#EAB308", size=18),
                                # SİLME BUTONU BURAYA EKLENDİ
                                ft.TextButton(content=ft.Text("❌", size=14), tooltip="Bu varlığı sil", on_click=lambda e, i=idx: varlik_sil(i))
                            ]),
                            ft.Divider(color="#1A1A24"),
                            ft.Text(varlik['detay'], color="#A0A0A5", size=14)
                        ]),
                        bgcolor="#0A0A0E", padding=20, border_radius=12, border=cerceve_olustur(1, "#1A1A24")
                    )
                    spot_liste.controls.append(kutu)
            page.update()

        # EKLEME FORMU (GİZLİ PANEL)
        borsa_input = ft.Dropdown(label="Borsa Seç", width=150, options=[ft.dropdown.Option("Binance"), ft.dropdown.Option("OKX"), ft.dropdown.Option("Gate.io"), ft.dropdown.Option("MEXC"), ft.dropdown.Option("KuCoin"), ft.dropdown.Option("Soğuk Cüzdan")])
        bakiye_input = ft.TextField(label="Miktar ($)", width=150)
        detay_input = ft.TextField(label="İçerik (Örn: 100 USDT, 0.5 SOL)", expand=True)
        
        def varlik_kaydet(e):
            if borsa_input.value and bakiye_input.value:
                spot_varliklar.append({
                    "borsa": borsa_input.value,
                    "bakiye": bakiye_input.value,
                    "detay": detay_input.value if detay_input.value else "Detay girilmedi"
                })
                borsa_input.value = ""; bakiye_input.value = ""; detay_input.value = ""
                form_paneli.visible = False
                listeyi_guncelle()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Borsa ve Miktar zorunludur!"), bgcolor="red")
                page.snack_bar.open = True; page.update()

        form_paneli = ft.Container(
            content=ft.Column([
                ft.Text("YENİ VARLIK EKLE", weight="bold", color="#EAB308"),
                ft.Row([borsa_input, bakiye_input, detay_input]),
                ft.Row([
                    ft.ElevatedButton("Kaydet", bgcolor="#EAB308", color="black", on_click=varlik_kaydet),
                    ft.TextButton("İptal", on_click=lambda e: (setattr(form_paneli, 'visible', False), page.update()))
                ])
            ]),
            visible=False, bgcolor="#050507", padding=20, border_radius=12, border=cerceve_olustur(1, "#EAB308")
        )

        def form_ac(e):
            form_paneli.visible = True
            page.update()

        icerik = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.TextButton(content=ft.Row([ft.Text("⬅️"), ft.Text("Cüzdan Menüsüne Dön", color="white")]), on_click=goster_ana_menu),
                    ft.Text("💼 SPOT CÜZDAN", size=20, weight="900", color="#EAB308"),
                    ft.TextButton(content=ft.Text("➕ YENİ EKLE", color="#EAB308", weight="900", size=16), tooltip="Yeni Borsa/Varlık Ekle", on_click=form_ac)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=10),
                form_paneli,
                spot_liste
            ]),
            padding=20, expand=True
        )
        ana_icerik.content = icerik
        listeyi_guncelle()

    # ==========================================
    # ALT SAYFA 2.5: İŞLEM DETAY VE YÖNETİM SAYFASI
    # ==========================================
    def goster_vadeli_detay(poz):
        yon_renk = "#10B981" if poz['yon'] == "LONG" else "#EF4444"
        
        detay_icerik = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.TextButton(content=ft.Row([ft.Text("⬅️"), ft.Text("Vadeli İşlemlere Dön", color="white")]), on_click=goster_vadeli_cuzdan),
                    ft.Text(f"⚡ İŞLEM MERKEZİ: {poz['coin']}", size=20, weight="900", color=yon_renk)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=20),
                
                # İŞLEM BİLGİLERİ KARTI
                ft.Container(
                    content=ft.Row([
                        ft.Column([ft.Text("YÖN", size=12, color="#737373"), ft.Text(poz['yon'], size=24, weight="900", color=yon_renk)]),
                        ft.Column([ft.Text("KALDIRAÇ", size=12, color="#737373"), ft.Text(poz['kaldirac'], size=24, weight="900", color="white")]),
                        ft.Column([ft.Text("MARJİN ($)", size=12, color="#737373"), ft.Text(f"${poz['miktar']}", size=24, weight="900", color="white")]),
                        ft.Column([ft.Text("GİRİŞ ZAMANI", size=12, color="#737373"), ft.Text(poz['zaman'], size=16, weight="bold", color="#A0A0A5")]),
                    ], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                    bgcolor="#050507", padding=20, border_radius=16, border=cerceve_olustur(1, yon_renk)
                ),
                ft.Container(height=20),
                
                # Q-AI YORUM KARTI
                ft.Container(
                    content=ft.Column([
                        ft.Row([ft.Text("🤖", size=24), ft.Text("Q-AI STRATEJİ YORUMU", weight="900", color="#00ffcc", size=18)]),
                        ft.Divider(color="#1A1A24"),
                        ft.Text(poz['ai_yorum'], color="#E2E8F0", size=14, italic=True)
                    ]),
                    bgcolor="#0A0A0E", padding=20, border_radius=16, border=cerceve_olustur(1, "#00ffcc"),
                    shadow=[ft.BoxShadow(blur_radius=15, color="#00ffcc", spread_radius=-5)]
                ),
                
                ft.Container(expand=True), # Boşluğu aşağı it
                
                # İŞLEM DEVAMLILIĞI (KONTROL PANELİ)
                ft.Container(
                    content=ft.Row([
                        ft.Text("Durum: ", color="#737373"),
                        ft.Text("🟢 AKTİF TAKİPTE", weight="bold", color="#10B981"),
                        ft.Container(expand=True),
                        ft.ElevatedButton("Zarar Kes / Kar Al Güncelle (Çok Yakında)", bgcolor="#1A1A24", color="white", disabled=True),
                        ft.ElevatedButton("İşlemi Kapat (Geçmişe Taşı)", bgcolor="#EF4444", color="white")
                    ]),
                    padding=20, bgcolor="#0A0A0E", border_radius=12, border=cerceve_olustur(1, "#1A1A24")
                )
            ]),
            padding=20, expand=True
        )
        ana_icerik.content = detay_icerik
        page.update()

    # ==========================================
    # ALT SAYFA 2: VADELİ POZİSYONLAR (AI BOT)
    # ==========================================
    def goster_vadeli_cuzdan(e=None):
        pozisyonlar_listesi = ft.Column(scroll=ft.ScrollMode.AUTO, spacing=10, expand=True)

        def pozisyonlari_listele():
            pozisyonlar_listesi.controls.clear()
            if not aktif_pozisyonlar:
                pozisyonlar_listesi.controls.append(ft.Text("Henüz açık bir pozisyon bulunmuyor.", color="#737373", italic=True))
            else:
                for poz in reversed(aktif_pozisyonlar): 
                    yon_renk = "#10B981" if poz['yon'] == "LONG" else "#EF4444"
                    
                    kutu = ft.Container(
                        content=ft.Row([
                            ft.Column([
                                ft.Text(f"{poz['coin']} / USDT", weight="900", color="white", size=18),
                                ft.Text(f"{poz['kaldirac']} | {poz['yon']}", weight="bold", color=yon_renk, size=14)
                            ]),
                            ft.Container(expand=True),
                            ft.Column([
                                ft.Text("Marjin", color="#737373", size=12, text_align=ft.TextAlign.RIGHT),
                                ft.Text(f"${poz['miktar']}", weight="bold", color="white", size=18, text_align=ft.TextAlign.RIGHT)
                            ], alignment=ft.MainAxisAlignment.END),
                            # HATA DÜZELTİLDİ: Çöken Flet ok ikonu yerine metin oku kullanıldı
                            ft.Text("➔", color="#737373", size=20, weight="bold") 
                        ]),
                        bgcolor="#0A0A0E", padding=20, border_radius=12, border=cerceve_olustur(1, yon_renk),
                        on_click=lambda e, p=poz: goster_vadeli_detay(p) 
                    )
                    
                    def hover_yap(e):
                        e.control.bgcolor = "#111116" if e.data == "true" else "#0A0A0E"
                        e.control.update()
                    kutu.on_hover = hover_yap
                    
                    pozisyonlar_listesi.controls.append(kutu)
            page.update()

        # Girdi Alanları
        input_coin = ft.TextField(label="Coin (Örn: BTC)", width=150, border_color="#00ffcc", color="white")
        input_kaldirac = ft.Dropdown(label="Kaldıraç", width=120, border_color="#00ffcc", color="white", options=[ft.dropdown.Option("5x"), ft.dropdown.Option("10x"), ft.dropdown.Option("20x"), ft.dropdown.Option("50x")])
        input_yon = ft.Dropdown(label="Yön", width=120, border_color="#00ffcc", color="white", options=[ft.dropdown.Option("LONG"), ft.dropdown.Option("SHORT")])
        input_miktar = ft.TextField(label="Miktar ($)", width=150, border_color="#00ffcc", color="white")

        def ai_yorum_uret(coin, yon, kaldirac):
            if yon == "LONG":
                return f"Q-AI Analizi: {coin} için {kaldirac} kaldıraçlı LONG pozisyonu sisteme kaydedildi. Algoritmalar mevcut destek seviyesinde tutunma ihtimalini %74 olarak hesaplıyor. Likidite avına karşı dikkatli olun ve işleminizi Q-AI Terminal üzerinden izlemeye devam edin."
            else:
                return f"Q-AI Analizi: {coin} varlığında saptanan ayı kırılımı sonrası {kaldirac} kaldıraçlı SHORT işlem başlatıldı. Hacim düşüşü devam ederse alt destek noktaları test edilecektir. Ani sıçramalara karşı marjininizi takip ediyoruz."

        def pozisyon_ekle(e):
            if input_coin.value and input_kaldirac.value and input_yon.value and input_miktar.value:
                yeni_poz = {
                    "coin": input_coin.value.upper(),
                    "kaldirac": input_kaldirac.value,
                    "yon": input_yon.value,
                    "miktar": input_miktar.value,
                    "zaman": datetime.datetime.now().strftime("%H:%M"),
                    "ai_yorum": ai_yorum_uret(input_coin.value.upper(), input_yon.value, input_kaldirac.value)
                }
                aktif_pozisyonlar.append(yeni_poz)
                
                input_coin.value = ""; input_miktar.value = ""
                pozisyonlari_listele()
                page.snack_bar = ft.SnackBar(ft.Text("⚡ Pozisyon AI motoruna eklendi!"), bgcolor="#00ffcc")
                page.snack_bar.open = True; page.update()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("Lütfen tüm alanları doldurun!"), bgcolor="red")
                page.snack_bar.open = True; page.update()

        ekle_butonu = ft.ElevatedButton(content=ft.Text("Yapay Zekaya İşlet", weight="bold", color="black"), style=ft.ButtonStyle(bgcolor="#00ffcc"), height=55, on_click=pozisyon_ekle)

        icerik = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.TextButton(content=ft.Row([ft.Text("⬅️"), ft.Text("Cüzdan Menüsüne Dön", color="white")]), on_click=goster_ana_menu),
                    ft.Text("🤖 VADELİ İŞLEMLER MERKEZİ", size=20, weight="900", color="#00ffcc")
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=20),
                ft.Text("Manuel açtığınız pozisyonları AI motoruna kaydedin. İşlem detayları için eklenen kutuya tıklayın.", color="#A0A0A5", size=14),
                ft.Row([input_coin, input_kaldirac, input_yon, input_miktar, ekle_butonu], wrap=True, alignment=ft.MainAxisAlignment.START),
                ft.Container(height=10),
                ft.Divider(color="#1A1A24"),
                ft.Container(height=10),
                ft.Text("Aktif Pozisyonlarınız (Detaylar İçin Tıklayın):", weight="900", color="white", size=18),
                pozisyonlar_listesi
            ]),
            padding=20, expand=True
        )
        ana_icerik.content = icerik
        pozisyonlari_listele()

    # ==========================================
    # CÜZDAN ANA MENÜSÜ (KUTULAR)
    # ==========================================
    def goster_ana_menu(e=None):
        kutu_spot = alt_kutu_olustur("💼 SPOT CÜZDAN", "Borsa bakiyeleri, varlık dağılımı ve ekleme\n(İçeri Gir)", fonk=goster_spot_cuzdan, neon_renk="#EAB308")
        kutu_vadeli = alt_kutu_olustur("🤖 VADELİ POZİSYONLAR", "AI destekli açık işlem takibi ve yorumlamalar\n(İçeri Gir)", fonk=goster_vadeli_cuzdan, neon_renk="#00ffcc")
        
        icerik = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.TextButton(content=ft.Row([ft.Text("🏠", size=16), ft.Text("Ana Panoya Dön", color="#00ffcc", weight="900")]), on_click=lambda e: geri_don_fonksiyonu()),
                    ft.Text("CÜZDAN KONTROL MERKEZİ", size=22, weight="900", color="white")
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Container(height=30),
                ft.Row([kutu_spot, kutu_vadeli], expand=True, spacing=30)
            ]),
            padding=30, expand=True
        )
        ana_icerik.content = icerik
        page.update()

    goster_ana_menu()
    return ft.Container(content=ana_icerik, expand=True, bgcolor="#030304")