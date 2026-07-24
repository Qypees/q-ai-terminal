import flet as ft
import time
import random

def ai_sohbet_sayfasi_olustur(page: ft.Page, geri_don_fonksiyonu):
    
    # --- GÜVENLİ ÇERÇEVE ---
    def cerceve_olustur(kalinlik, renk):
        kenar = ft.BorderSide(kalinlik, renk)
        return ft.Border(top=kenar, right=kenar, bottom=kenar, left=kenar)

    # --- SOHBET GEÇMİŞİ VE ARAYÜZÜ ---
    sohbet_gecmisi = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=15)
    
    sesli_yanit_aktif = False

    def ses_modunu_degistir(e):
        nonlocal sesli_yanit_aktif
        sesli_yanit_aktif = e.control.value
        page.snack_bar.content.value = "🔊 Sesli Yanıt Motoru Aktif Edildi!" if sesli_yanit_aktif else "🔇 Sesli Yanıt Motoru Kapatıldı."
        page.snack_bar.bgcolor = "#00ffcc" if sesli_yanit_aktif else "#EF4444"
        page.snack_bar.open = True
        page.update()

    def mesaj_balonu_olustur(mesaj, gonderen="ben"):
        if gonderen == "ai":
            # AI Balonu (Sola Dayalı, Neon Turkuaz, Siberpunk Çizgiler)
            balon = ft.Container(
                content=ft.Row([
                    ft.Icon(ft.icons.SMART_TOY, color="#00ffcc", size=20),
                    ft.Container(
                        content=ft.Text(mesaj, color="#E2E8F0", size=14),
                        bgcolor="#0A0A0E", padding=15, border_radius=ft.border_radius.only(top_left=0, top_right=15, bottom_left=15, bottom_right=15),
                        border=ft.Border(left=ft.BorderSide(3, "#00ffcc"), bottom=ft.BorderSide(1, "#1A1A24")),
                        shadow=[ft.BoxShadow(blur_radius=15, color="#00ffcc", spread_radius=-10)],
                        width=500
                    )
                ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START),
                margin=ft.margin.only(bottom=10)
            )
        else:
            # Kullanıcı Balonu (Sağa Dayalı, Koyu Gri)
            balon = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Text(mesaj, color="white", size=14),
                        bgcolor="#1A1A24", padding=15, border_radius=ft.border_radius.only(top_left=15, top_right=0, bottom_left=15, bottom_right=15),
                        border=cerceve_olustur(1, "#27272A"),
                        width=400
                    ),
                    ft.Icon(ft.icons.PERSON, color="#737373", size=20)
                ], alignment=ft.MainAxisAlignment.END, vertical_alignment=ft.CrossAxisAlignment.START),
                margin=ft.margin.only(bottom=10)
            )
        return balon

    def ai_yanit_uret(kullanici_mesaji):
        mesaj = kullanici_mesaji.lower()
        if "btc" in mesaj or "bitcoin" in mesaj:
            return "Q-AI Analizi: Bitcoin (BTC) güçlü bir akümülasyon (toplama) evresinde. Zincir üstü (On-chain) verilerde borsalardan soğuk cüzdanlara yüklü çıkışlar tespit ettim. Yakında yukarı yönlü sert bir kırılım gelebilir! 🚀"
        elif "eth" in mesaj or "ethereum" in mesaj:
            return "Q-AI Analizi: Ethereum (ETH) ağındaki gas ücretleri stabil. Balina cüzdanları son 24 saatte 50.000 ETH alımı yaptı. Trend desteğinde tutunuyor."
        elif "ses" in mesaj or "merhaba" in mesaj:
            return "Merhaba Patron! Ben senin kişisel kripto yapay zekân Q-AI. Piyasaları senin için 7/24 tarıyorum. İstediğin bir coin var mı?"
        else:
            cevaplar = [
                "Bunu global piyasa likidite haritasıyla eşleştiriyorum... İşlem hacmi şu an yatay seyrediyor. Beklemede kalmak en iyi seçenek olabilir.",
                "Algoritmam bu veriyi inceledi. Risk/Ödül oranı şu an tam sınırda. Stop-loss seviyeni giriş fiyatına yakın tutmanı öneririm.",
                "Bu varlıkta aşırı alım (Overbought) tespit ettim. Balinalar satışa hazırlanıyor olabilir, lütfen dikkatli ol! 🔴"
            ]
            return random.choice(cevaplar)

    def mesaj_gonder(e):
        if not mesaj_girdisi.value: return
        
        yeni_mesaj = mesaj_girdisi.value
        mesaj_girdisi.value = ""
        sohbet_gecmisi.controls.append(mesaj_balonu_olustur(yeni_mesaj, "ben"))
        page.update()

        # AI Düşünme Efekti
        yaziyor_gostergesi = ft.Container(
            content=ft.Row([ft.ProgressRing(width=16, height=16, color="#00ffcc", stroke_width=2), ft.Text("Q-AI piyasayı tarıyor...", color="#00ffcc", size=12, italic=True)]),
            margin=ft.margin.only(left=30, bottom=10)
        )
        sohbet_gecmisi.controls.append(yaziyor_gostergesi)
        page.update()

        # Yapay Zeka Gecikmesi (Gerçekçi His)
        time.sleep(1.5)
        
        # Yanıtı ekle ve yazıyor ibaresini sil
        sohbet_gecmisi.controls.remove(yaziyor_gostergesi)
        ai_cevap = ai_yanit_uret(yeni_mesaj)
        sohbet_gecmisi.controls.append(mesaj_balonu_olustur(ai_cevap, "ai"))
        
        # Eğer Ses Aktifse Sesli Sinyal Ver (UI Efekti)
        if sesli_yanit_aktif:
            page.snack_bar.content.value = "🔊 Q-AI Sesli Yanıt Oynatılıyor..."
            page.snack_bar.bgcolor = "#3B82F6"
            page.snack_bar.open = True

        # Scrollu en alta indir
        page.update()

    def sesle_yazdir_click(e):
        page.snack_bar.content.value = "🎤 Mikrofon Dinleniyor... (Sesli Asistan API v1.3'te entegre edilecek)"
        page.snack_bar.bgcolor = "#F59E0B"
        page.snack_bar.open = True
        page.update()

    # --- ALT KONTROL (Mesaj Yazma Alanı) ---
    mesaj_girdisi = ft.TextField(
        hint_text="Q-AI'ye bir coin sor veya piyasa analizi iste...",
        bgcolor="transparent", border_color="transparent", color="white",
        expand=True, on_submit=mesaj_gonder
    )

    girdi_alani = ft.Container(
        content=ft.Row([
            ft.IconButton(icon=ft.icons.MIC, icon_color="#00ffcc", tooltip="Sesli Komut", on_click=sesle_yazdir_click),
            mesaj_girdisi,
            ft.IconButton(icon=ft.icons.SEND, icon_color="white", bgcolor="#00ffcc", tooltip="Gönder", on_click=mesaj_gonder)
        ]),
        bgcolor="#0A0A0E", border_radius=25, padding=ft.padding.symmetric(horizontal=10, vertical=5),
        border=cerceve_olustur(1, "#1A1A24")
    )

    # --- ÜST BAR VE İSKELET ---
    ust_bar = ft.Row([
        ft.Row([
            ft.Icon(ft.icons.SMART_TOY, color="#00ffcc", size=28),
            ft.Text("Q-AI KRİPTO ASİSTAN", size=22, weight="900", color="white")
        ]),
        ft.Row([
            ft.Text("Sesli Yanıt Motoru:", color="#737373", size=12),
            ft.Switch(value=False, active_color="#00ffcc", on_change=ses_modunu_degistir)
        ])
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    # İlk Karşılama Mesajı
    sohbet_gecmisi.controls.append(mesaj_balonu_olustur("Sistem Çevrimiçi. Ben Q-AI, piyasa analisti ve işlem asistanınım. Portföyünü uçurmak için hazır bekliyorum!", "ai"))

    ana_icerik = ft.Container(
        content=ft.Column([
            ust_bar, ft.Divider(color="#1A1A24"),
            ft.Container(content=sohbet_gecmisi, expand=True, padding=ft.padding.only(right=15)), # Chat Alanı
            girdi_alani
        ], expand=True),
        bgcolor="#030304", padding=20, expand=True
    )

    return ft.Container(
        content=ft.Column([
            ft.TextButton(content=ft.Text("⬅️ Panoya Dön", color="#3B82F6"), on_click=lambda e: geri_don_fonksiyonu()), 
            ana_icerik
        ], expand=True),
        bgcolor="#030304", padding=10, expand=True
    )