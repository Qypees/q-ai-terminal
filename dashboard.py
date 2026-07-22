import flet as ft
from ai_signal_page import ai_signal_sayfasi_olustur
from chart_page import grafik_sayfasi_olustur
from generic_page import genel_sayfa_olustur
from market_page import piyasa_sayfasi_olustur
from news_page import haber_sayfasi_olustur

def ana_ekran_olustur(page: ft.Page):
    
    # --- YENİ NESİL GÜVENLİ ÇERÇEVE MOTORU (FLET 0.80.0 UYUMLU) ---
    def cerceve_olustur(kalinlik, renk):
        kenar = ft.BorderSide(kalinlik, renk)
        return ft.Border(top=kenar, right=kenar, bottom=kenar, left=kenar)

    # --- PREMIUM KART MOTORU ---
    def kutu_olustur(baslik, alt_metin, fonk=None, esneklik=1, bg="#0A0A0E"):
        icerik = ft.Column(
            controls=[
                ft.Text(baslik, size=16, weight="900", color="white"), 
                ft.Container(height=2),
                ft.Text(alt_metin, size=12, color="#737373", text_align="center") 
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        kutu = ft.Container(
            content=icerik,
            bgcolor=bg,
            border=cerceve_olustur(1, "#1A1A24"), 
            border_radius=16, 
            padding=20,
            expand=esneklik,
            shadow=[
                ft.BoxShadow(blur_radius=20, color="#000000", offset=ft.Offset(0, 10)), 
            ],
            animate_scale=ft.Animation(200, ft.AnimationCurve.DECELERATE),
            animate=ft.Animation(200, ft.AnimationCurve.DECELERATE),
            on_click=fonk
        )

        def hover_olayi(e):
            e.control.scale = 1.02 if e.data == "true" else 1.0
            e.control.border = cerceve_olustur(1, "#00ffcc") if e.data == "true" else cerceve_olustur(1, "#1A1A24")
            e.control.update()
            
        kutu.on_hover = hover_olayi
        return kutu

    # ==========================================
    # SAYFA GEÇİŞ SİSTEMLERİ
    # ==========================================
    def sayfaya_gec(olusturucu_fonksiyon, modul_adi="Modül"):
        def gecis(e):
            page.snack_bar.content.value = f"⚡ {modul_adi} Başlatılıyor..."
            page.snack_bar.bgcolor = "#fb923c"
            page.snack_bar.open = True
            page.update()

            def geri_don():
                page.controls.clear()
                page.add(ana_ekran_olustur(page))
                page.update()

            page.controls.clear()
            page.add(olusturucu_fonksiyon(page, geri_don))
            page.update()
        return gecis

    def jenerik_sayfaya_gec(baslik, emoji, aciklama):
        def gecis(e):
            def geri_don():
                page.controls.clear()
                page.add(ana_ekran_olustur(page))
                page.update()

            page.controls.clear()
            page.add(genel_sayfa_olustur(baslik, emoji, aciklama, geri_don))
            page.update()
        return gecis


    # ==========================================
    # DİNAMİK 16'LI KUTU DİZİLİMİ
    # ==========================================

    # 1. KUTU: Tarih ve Saat 
    kutu_1 = ft.Container(
        content=ft.Row(
            [ft.Text("📍 İstanbul | 22 Temmuz 2026, 23:25", size=14, weight="bold", color="#A0A0A5")], 
            alignment=ft.MainAxisAlignment.CENTER
        ),
        bgcolor="#050507", border_radius=16, padding=15, height=55,
        border=cerceve_olustur(1, "#1A1A24"),
        on_click=jenerik_sayfaya_gec("Tarih ve Saat", "📍", "Yerel zaman dilimi ve alarm ayarları çok yakında burada olacak.")
    )

    # 🔴 LİVE ETİKETİ EKLENDİ
    kutu_2 = kutu_olustur("📈 CANLI PİYASA  🔴 LİVE", "Fiyatlar ve tahta ekranı\n(İçeri Gir)", fonk=sayfaya_gec(piyasa_sayfasi_olustur, "Canlı Piyasa"), esneklik=3)
    kutu_3 = kutu_olustur("📰 SON DAKİKA", "Piyasa Haberleri\n(İçeri Gir)", fonk=sayfaya_gec(haber_sayfasi_olustur, "Haber Merkezi"), esneklik=1)
    kutu_4 = kutu_olustur("🧠 AI FIRSATLARI", "Sinyaller ve Yorumlar\n(İçeri Gir)", fonk=sayfaya_gec(ai_signal_sayfasi_olustur, "AI Sinyal Merkezi"), esneklik=2)
    
    satir_234 = ft.Row([kutu_2, ft.Column([kutu_3, kutu_4], expand=2, spacing=15)], height=220)

    kutu_5 = kutu_olustur("📊 GRAFİK EKRANI", "AI Destekli Analizler ve TradingView Entegrasyonu (İçeri Gir)", fonk=sayfaya_gec(grafik_sayfasi_olustur, "Grafik Terminali"))
    kutu_5.height = 85 

    kutu_6 = kutu_olustur("🏆 TOP 5 COİN", "En çok düşen/yükselen", fonk=jenerik_sayfaya_gec("Top 5 Coin", "🏆", "Günün en çok kazandıran ve kaybettiren varlıkları."))
    kutu_7 = kutu_olustur("🔥 ISI HARİTASI", "Genel piyasa sıcaklığı", fonk=jenerik_sayfaya_gec("Isı Haritası", "🔥", "Sektörel bazda piyasa sıcaklık haritası."))
    satir_67 = ft.Row([kutu_6, kutu_7], height=120)

    kutu_15 = kutu_olustur("📝 NOT DEFTERİ", "Kişisel trade notları", fonk=jenerik_sayfaya_gec("Not Defteri", "📝", "Kişisel trade fikirleriniz ve işlem geçmişiniz."), esneklik=1)
    
    # ==========================================
    # KUTU 14: QYPEES TERMİNALİ ÖZEL LOGO ALANI
    # ==========================================
    hareketli_logo = ft.Column([
        ft.ProgressRing(width=65, height=65, stroke_width=4, color="#00ffcc"),
        ft.Container(height=5),
        ft.Text("Q", size=48, weight="900", color="white"),
        # HATA DÜZELTİLDİ: letter_spacing argümanı tamamen kaldırıldı
        ft.Text("Qypees Terminali", size=13, weight="bold", color="#00ffcc")
    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0)
    
    kutu_14 = ft.Container(
        content=hareketli_logo, bgcolor="#050507", border_radius=16, expand=2,
        border=cerceve_olustur(1, "#00ffcc"), 
        shadow=[ft.BoxShadow(spread_radius=2, blur_radius=25, color="#00ffcc", offset=ft.Offset(0, 0))] 
    ) 
    
    kutu_16 = kutu_olustur("🎵 MÜZİK", "Spotify Kontrolü", fonk=jenerik_sayfaya_gec("Müzik Kontrol", "🎵", "Spotify entegrasyonu ile işlem yaparken odaklanın."), esneklik=1)
    
    satir_15_14_16 = ft.Row([kutu_15, kutu_14, kutu_16], height=240)

    # 8 ve 9. KUTULAR 
    icerik_8 = ft.Row([
        ft.Text("🤖 AI BOT DURUMU", weight="900", color="white", size=14),
        ft.Switch(value=True, active_color="#00ffcc", active_track_color="#006652")
    ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
    kutu_8 = ft.Container(
        content=icerik_8, bgcolor="#0A0A0E", border_radius=16, expand=1,
        border=cerceve_olustur(1, "#1A1A24"), padding=20
    ) 
    
    kutu_9 = kutu_olustur("💬 AI SOHBET", "Asistanla konuş", fonk=jenerik_sayfaya_gec("AI Sohbet", "💬", "Q-AI ile doğrudan iletişim kurabileceğiniz sohbet arayüzü."))
    satir_89 = ft.Row([kutu_8, kutu_9], height=95)

    kutu_10 = kutu_olustur("💼 CÜZDAN ÖZETİ", "Tüm borsa hesaplarınızdaki toplam varlıklar (İçeri Gir)", fonk=jenerik_sayfaya_gec("Cüzdan Özeti", "💼", "Borsa hesaplarınızdaki toplam varlık değeriniz."))
    kutu_10.height = 85

    kutu_11 = kutu_olustur("💰 VARLIK BÖLGESİ", "Portföy Dağılımı", fonk=jenerik_sayfaya_gec("Varlık Bölgesi", "💰", "Elinizdeki varlıkların oransal dağılım grafiği."))
    kutu_12 = kutu_olustur("⚙️ AYARLAR", "API ve Konfigürasyon", fonk=jenerik_sayfaya_gec("Ayarlar", "⚙️", "API anahtarları ve terminal konfigürasyonu."))
    kutu_13 = kutu_olustur("👤 PROFİL", "Güvenlik ve Hesap", fonk=jenerik_sayfaya_gec("Profil", "👤", "Kişisel hesap bilgileriniz ve güvenlik ayarları."), esneklik=2)
    
    satir_1112_13 = ft.Row([ft.Column([kutu_11, kutu_12], expand=2, spacing=15), kutu_13], height=210)

    # ==========================================
    # MERKEZİ HİZALAMA VE MAKSİMUM GENİŞLİK KİLİDİ
    # ==========================================
    merkez_kapsayici = ft.Container(
        content=ft.Column(
            controls=[
                kutu_1, satir_234, kutu_5, satir_67, satir_15_14_16, satir_89, kutu_10, satir_1112_13
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=15 
        ),
        width=1100, 
        alignment=ft.Alignment(0, -1)
    )

    ana_icerik = ft.Container(
        content=merkez_kapsayici,
        padding=20,
        expand=True,
        bgcolor="#030304",
        alignment=ft.Alignment(0, -1) 
    )
    
    return ana_icerik