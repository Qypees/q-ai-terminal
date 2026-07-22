import flet as ft
# Alt sayfalarımızı içeri aktarıyoruz
from ai_signal_page import ai_signal_sayfasi_olustur
from chart_page import grafik_sayfasi_olustur
from generic_page import genel_sayfa_olustur
from market_page import piyasa_sayfasi_olustur
from news_page import haber_sayfasi_olustur

def ana_ekran_olustur(page: ft.Page):
    
    # --- GÜVENLİ KUTU MOTORU ---
    def kutu_olustur(baslik, alt_metin, fonk=None, esneklik=1, bg="#111111"):
        icerik = ft.Column(
            controls=[
                ft.Text(baslik, size=16, weight="bold", color="#00ffcc", text_align="center"),
                ft.Container(height=5),
                ft.Text(alt_metin, size=12, color="white70", text_align="center")
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
        
        return ft.Container(
            content=icerik,
            bgcolor=bg,
            border_radius=10,
            padding=10,
            expand=esneklik,
            on_click=fonk
        )

    # ==========================================
    # SAYFA GEÇİŞ SİSTEMLERİ
    # ==========================================
    def sayfaya_gec(olusturucu_fonksiyon):
        # Kutuya tıklandığında ekranı temizleyip ilgili sayfayı açar
        def gecis(e):
            def geri_don():
                page.controls.clear()
                page.add(ana_ekran_olustur(page))
                page.update()

            page.controls.clear()
            page.add(olusturucu_fonksiyon(page, geri_don))
            page.update()
        return gecis

    def jenerik_sayfaya_gec(baslik, emoji, aciklama):
        # Henüz özel sayfası olmayan kutular için joker sayfayı çağırır
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
    # KUTULARIN DİZİLİMİ VE BAĞLANTILARI
    # ==========================================

    # 1. KUTU: Tarih ve Saat
    kutu_1 = ft.Container(
        content=ft.Row(
            [ft.Text("📍 İstanbul | 22 Temmuz 2026, 23:10", size=15, weight="bold", color="white")], 
            alignment=ft.MainAxisAlignment.CENTER
        ),
        bgcolor="#111111", border_radius=10, padding=15, height=50,
        on_click=jenerik_sayfaya_gec("Tarih ve Saat", "📍", "Yerel zaman dilimi ve alarm ayarları çok yakında burada olacak.")
    )

    # 2, 3 ve 4. KUTULAR
    # Kutu 2 Özel Sayfaya Gider (market_page.py)
    kutu_2 = kutu_olustur("📈 CANLI PİYASA", "Fiyatlar ve tahta ekranı\n(İçeri Gir)", fonk=sayfaya_gec(piyasa_sayfasi_olustur), esneklik=3)
    
    # Kutu 3 Özel Sayfaya Gider (news_page.py)
    kutu_3 = kutu_olustur("📰 SON DAKİKA", "Piyasa Haberleri\n(İçeri Gir)", fonk=sayfaya_gec(haber_sayfasi_olustur), esneklik=1)
    
    # Kutu 4 Özel Sayfaya Gider (ai_signal_page.py)
    kutu_4 = kutu_olustur("🧠 AI FIRSATLARI", "Short/Long yorumları ve Sinyaller\n(İçeri Gir)", fonk=sayfaya_gec(ai_signal_sayfasi_olustur), esneklik=2)
    
    satir_234 = ft.Row([kutu_2, ft.Column([kutu_3, kutu_4], expand=2)], height=220)

    # 5. KUTU: Grafik - Özel Sayfaya Gider (chart_page.py)
    kutu_5 = ft.Container(
        content=ft.Row(
            [ft.Text("📊 GRAFİK EKRANI: AI Destekli Analizler ve Yorumlar (İçeri Gir)", color="#00ffcc", weight="bold")],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        bgcolor="#111111", border_radius=10, height=60,
        on_click=sayfaya_gec(grafik_sayfasi_olustur)
    )

    # 6 ve 7. KUTULAR 
    kutu_6 = kutu_olustur("🏆 TOP 5 COİN", "En çok düşen/yükselen\n(İçeri Gir)", fonk=jenerik_sayfaya_gec("Top 5 Coin", "🏆", "Günün en çok kazandıran ve kaybettiren varlıkları."))
    kutu_7 = kutu_olustur("🔥 ISI HARİTASI", "Genel piyasa sıcaklığı\n(İçeri Gir)", fonk=jenerik_sayfaya_gec("Isı Haritası", "🔥", "Sektörel bazda piyasa sıcaklık haritası."))
    satir_67 = ft.Row([kutu_6, kutu_7], height=100)

    # 15, 14 ve 16. KUTULAR 
    kutu_15 = kutu_olustur("📝 NOT DEFTERİ", "(İçeri Gir)", fonk=jenerik_sayfaya_gec("Not Defteri", "📝", "Kişisel trade fikirleriniz ve işlem geçmişiniz."), esneklik=1)
    
    # KUTU 14: SABİT LOGO (İçine Girilmez)
    hareketli_logo = ft.Column([
        ft.ProgressRing(width=60, height=60, stroke_width=5, color="#00ffcc"),
        ft.Container(height=15),
        ft.Text("Q-AI", size=35, weight="bold", color="white")
    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    kutu_14 = ft.Container(content=hareketli_logo, bgcolor="#050505", border_radius=10, expand=2) 
    
    kutu_16 = kutu_olustur("🎵 MÜZİK", "Spotify Kontrol\n(İçeri Gir)", fonk=jenerik_sayfaya_gec("Müzik Kontrol", "🎵", "Spotify entegrasyonu ile işlem yaparken odaklanın."), esneklik=1)
    
    satir_15_14_16 = ft.Row([kutu_15, kutu_14, kutu_16], height=250)

    # 8 ve 9. KUTULAR 
    # KUTU 8: BOT SWITCH (İçine Girilmez)
    icerik_8 = ft.Row([
        ft.Text("🤖 AI BOT DURUMU", weight="bold", color="white"),
        ft.Switch(value=True, active_color="green")
    ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
    kutu_8 = ft.Container(content=icerik_8, bgcolor="#111111", border_radius=10, expand=1) 
    
    kutu_9 = kutu_olustur("💬 AI SOHBET", "Sesli ve Yazılı Bot\n(İçeri Gir)", fonk=jenerik_sayfaya_gec("AI Sohbet", "💬", "Q-AI ile doğrudan iletişim kurabileceğiniz sohbet arayüzü."))
    satir_89 = ft.Row([kutu_8, kutu_9], height=80)

    # 10. KUTU: Cüzdan Genel 
    kutu_10 = ft.Container(
        content=ft.Row(
            [ft.Text("💼 CÜZDAN ÖZETİ (İçeri Gir)", color="#00ffcc", weight="bold")],
            alignment=ft.MainAxisAlignment.CENTER
        ),
        bgcolor="#111111", border_radius=10, height=60,
        on_click=jenerik_sayfaya_gec("Cüzdan Özeti", "💼", "Borsa hesaplarınızdaki toplam varlık değeriniz.")
    )

    # 11, 12 ve 13. KUTULAR
    kutu_11 = kutu_olustur("💰 VARLIK BÖLGESİ", "(İçeri Gir)", fonk=jenerik_sayfaya_gec("Varlık Bölgesi", "💰", "Elinizdeki varlıkların oransal dağılım grafiği."))
    kutu_12 = kutu_olustur("⚙️ AYARLAR", "(İçeri Gir)", fonk=jenerik_sayfaya_gec("Ayarlar", "⚙️", "API anahtarları ve terminal konfigürasyonu."))
    kutu_13 = kutu_olustur("👤 PROFİL", "Kullanıcı ekranı\n(İçeri Gir)", fonk=jenerik_sayfaya_gec("Profil", "👤", "Kişisel hesap bilgileriniz ve güvenlik ayarları."), esneklik=2)
    
    satir_1112_13 = ft.Row([ft.Column([kutu_11, kutu_12], expand=2), kutu_13], height=200)

    # ==========================================
    # TÜM ŞABLONU ANA EKRANA YERLEŞTİR
    # ==========================================
    ana_icerik = ft.Container(
        content=ft.Column(
            controls=[
                kutu_1, satir_234, kutu_5, satir_67, satir_15_14_16, satir_89, kutu_10, satir_1112_13
            ],
            scroll=ft.ScrollMode.AUTO,
            spacing=10
        ),
        padding=10,
        expand=True,
        bgcolor="#030303"
    )
    
    return ana_icerik