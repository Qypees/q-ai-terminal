import flet as ft
from datetime import datetime
import time
import threading

# Sayfalar
from generic_page import genel_sayfa_olustur
from market_page import piyasa_sayfasi_olustur 
from news_page import haber_sayfasi_olustur 
from ai_signal_page import ai_signal_sayfasi_olustur 
from chart_page import grafik_sayfasi_olustur # <-- Grafik ve Analiz sayfası eklendi

global_page_instance = None

def ana_ekran_olustur(page):
    global global_page_instance
    global_page_instance = page

    # --- PREMIUM RENK PALETİ ---
    zemin_siyah = "#030303"      
    kutu_zemin = "#0A0A0C"       
    luks_turuncu = "#FF8C00"     
    mat_altin = "#B89B72"        
    gri_metin = "#8E8E93"        
    canli_yesil = "#30D158"      
    canli_kirmizi = "#FF453A"    
    mavi_urg = "#0A84FF"         

    bosluk = 12 

    ana_ekran_kapsayici = ft.Container(
        expand=True,
        bgcolor=zemin_siyah,
        padding=bosluk,
    )

    def ana_ekrana_don():
        ana_ekran_kapsayici.content = dashboard_arayuzunu_kur()
        ana_ekran_kapsayici.update()

    def kutuya_tiklandi(kutu_ismi):
        if kutu_ismi == "Canlı Piyasa":
            ana_ekran_kapsayici.content = piyasa_sayfasi_olustur(page, ana_ekrana_don)
        elif kutu_ismi == "Haber Akışı":
            ana_ekran_kapsayici.content = haber_sayfasi_olustur(page, ana_ekrana_don)
        elif kutu_ismi == "AI Fırsat Analizi":
            ana_ekran_kapsayici.content = ai_signal_sayfasi_olustur(page, ana_ekrana_don)
        elif kutu_ismi == "Grafik ve Analiz":
            ana_ekran_kapsayici.content = grafik_sayfasi_olustur(page, ana_ekrana_don)
        else:
            ana_ekran_kapsayici.content = genel_sayfa_olustur(
                kutu_ismi, 
                "⚙️", 
                f"{kutu_ismi} modülü ekranına başarıyla geçiş yapıldı.", 
                ana_ekrana_don
            )
        ana_ekran_kapsayici.update()

    # --- 8 Numaralı Kutu İçin Özel Neon Aç/Kapat Mantığı ---
    def ai_bot_tetikle(e, container, metin, ikon):
        if container.data == "kapali":
            container.data = "acik"
            container.shadow = ft.BoxShadow(spread_radius=2, blur_radius=15, color="#663800")
            container.gradient = ft.LinearGradient(
                begin=ft.Alignment(-1.0, -1.0), end=ft.Alignment(1.0, 1.0),
                colors=["#3d2200", kutu_zemin]
            )
            metin.value = "AI BOT AKTİF"
            metin.color = luks_turuncu
            ikon.value = "🟢"
        else:
            container.data = "kapali"
            container.shadow = None
            container.gradient = ft.LinearGradient(
                begin=ft.Alignment(-1.0, -1.0), end=ft.Alignment(1.0, 1.0),
                colors=["#121214", kutu_zemin]
            )
            metin.value = "AI BOT KAPALI"
            metin.color = gri_metin
            ikon.value = "🔴"
        container.update()

    # --- VIP Kutu Üretici ---
    def kutu_yap(icerik, tiklama_fonk=None, yukseklik=None, bg_renk=None, padding_deg=12):
        return ft.Container(
            content=icerik,
            on_click=tiklama_fonk,
            height=yukseklik,
            expand=True if yukseklik is None else False,
            bgcolor=bg_renk,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1.0, -1.0),
                end=ft.Alignment(1.0, 1.0),
                colors=["#141416", kutu_zemin]
            ) if bg_renk is None else None,
            border_radius=18,
            padding=padding_deg,
            animate=ft.Animation(300, ft.AnimationCurve.DECELERATE),
            alignment=ft.Alignment(0, 0)
        )

    def badge_yap(metin, renk, yazi_renk="white"):
        return ft.Container(
            content=ft.Text(metin, size=9, weight="bold", color=yazi_renk),
            bgcolor=renk, border_radius=4, padding=3
        )

    def dashboard_arayuzunu_kur():
        su_an = datetime.now()
        tarih_metni = su_an.strftime("%d %B %Y | %H:%M")
        kutu_1 = kutu_yap(
            ft.Row([
                ft.Row([
                    ft.Container(width=6, height=6, bgcolor=canli_kirmizi, border_radius=3, shadow=ft.BoxShadow(blur_radius=5, color=canli_kirmizi)),
                    ft.Text("LIVE", color=canli_kirmizi, weight="900", size=10)
                ], spacing=4),
                ft.Text(tarih_metni, color=mat_altin, weight="bold", size=12)
            ], alignment="spaceBetween"),
            yukseklik=45, padding_deg=10
        )

        kutu_2_icerik = ft.Column([
            ft.Row([ft.Text("📊 PİYASA", color=luks_turuncu, weight="900", size=11), ft.Text("📈", size=14)], alignment="spaceBetween"),
            ft.Container(height=2), 
            ft.Row([ft.Text("BTC", color="white", weight="bold", size=13), ft.Row([ft.Text("$64,230", color="white", size=13), badge_yap("+2.1%", "#0b3d14", canli_yesil)])], alignment="spaceBetween"),
            ft.Row([ft.Text("ETH", color="white", weight="bold", size=13), ft.Row([ft.Text("$3,310", color="white", size=13), badge_yap("-0.8%", "#3d0b0b", canli_kirmizi)])], alignment="spaceBetween"),
            ft.Row([ft.Text("SOL", color="white", weight="bold", size=13), ft.Row([ft.Text("$145.2", color="white", size=13), badge_yap("+5.4%", "#0b3d14", canli_yesil)])], alignment="spaceBetween"),
        ], spacing=8)
        kutu_2 = kutu_yap(kutu_2_icerik, tiklama_fonk=lambda e: kutuya_tiklandi("Canlı Piyasa"))

        kutu_3 = kutu_yap(
            ft.Column([
                ft.Row([ft.Text("📰 HABER", color=mavi_urg, weight="900", size=10), badge_yap("YENİ", mavi_urg)], alignment="spaceBetween"),
                ft.Text("Fed faiz kararı açıklandı, piyasada sert hareket bekleniyor.", color="#D1D1D6", size=10, max_lines=3)
            ], alignment="start", spacing=5),
            tiklama_fonk=lambda e: kutuya_tiklandi("Haber Akışı")
        )

        kutu_4 = kutu_yap(
            ft.Column([
                ft.Text("🧠 AI SİNYAL", color=mat_altin, weight="900", size=10),
                ft.Container(
                    content=ft.Row([
                        ft.Text("SOL", color="white", weight="900", size=14),
                        ft.Text("⬆️", color=canli_yesil, size=14),
                        ft.Text("LONG", color=canli_yesil, weight="900", size=12)
                    ], alignment="center", spacing=4),
                    bgcolor="#0A2211", border_radius=8, padding=5, expand=True
                )
            ], alignment="center", horizontal_alignment="center", spacing=5),
            tiklama_fonk=lambda e: kutuya_tiklandi("AI Fırsat Analizi")
        )

        kutu_5 = kutu_yap(
            ft.Row([
                ft.Row([
                    ft.Container(content=ft.Text("📈", size=20), padding=8, bgcolor="#1A1A1E", border_radius=10),
                    ft.Column([
                        ft.Text("AI GRAFİK TERMİNALİ", color="white", weight="900", size=12),
                        ft.Text("Profesyonel analiz ve formasyonlar", color=gri_metin, size=10)
                    ], spacing=0, alignment="center")
                ], spacing=10),
                ft.Container(content=ft.Text("GİRİŞ", color=zemin_siyah, weight="900", size=10), bgcolor=luks_turuncu, padding=8, border_radius=15)
            ], alignment="spaceBetween"),
            yukseklik=70,
            tiklama_fonk=lambda e: kutuya_tiklandi("Grafik ve Analiz")
        )

        kutu_6 = kutu_yap(
            ft.Column([
                ft.Text("🏆 TOP HAREKET", color=mat_altin, weight="900", size=10),
                ft.Row([
                    badge_yap("↑ PEPE", "#0b3d14", canli_yesil),
                    badge_yap("↓ DOGE", "#3d0b0b", canli_kirmizi)
                ], alignment="center", spacing=5)
            ], alignment="center", horizontal_alignment="center", spacing=8),
            tiklama_fonk=lambda e: kutuya_tiklandi("Top 5 Coinler")
        )

        kutu_7 = kutu_yap(
            ft.Column([
                ft.Text("🗺️ ISI HARİTASI", color=mat_altin, weight="900", size=10),
                ft.Row([
                    ft.Container(width=12, height=12, bgcolor=canli_yesil, border_radius=2),
                    ft.Container(width=12, height=12, bgcolor=canli_kirmizi, border_radius=2),
                    ft.Container(width=12, height=12, bgcolor="#202020", border_radius=2),
                    ft.Container(width=12, height=12, bgcolor=canli_yesil, border_radius=2),
                    ft.Container(width=12, height=12, bgcolor=canli_yesil, border_radius=2),
                ], alignment="center", spacing=3)
            ], alignment="center", horizontal_alignment="center", spacing=8),
            tiklama_fonk=lambda e: kutuya_tiklandi("Isı Haritası")
        )

        logo_animasyon = ft.Container(
            content=ft.Column([
                ft.Text("Q", size=55, color="white", weight="900"),
                ft.Text("TERMINAL", size=10, color=luks_turuncu, weight="900") 
            ], alignment="center", horizontal_alignment="center", spacing=2),
            alignment=ft.Alignment(0, 0),
            animate_scale=ft.Animation(2500, ft.AnimationCurve.EASE_IN_OUT),
            scale=1.0
        )
        def logo_nefes_al():
            while True:
                try:
                    logo_animasyon.scale = 1.03
                    logo_animasyon.update()
                    time.sleep(2.5)
                    logo_animasyon.scale = 0.97
                    logo_animasyon.update()
                    time.sleep(2.5)
                except:
                    break
        threading.Thread(target=logo_nefes_al, daemon=True).start()
        kutu_14 = kutu_yap(logo_animasyon, bg_renk="transparent")

        kutu_15 = kutu_yap(
            ft.Column([
                ft.Container(content=ft.Text("📝", size=22), padding=12, bgcolor="#1A1A1E", border_radius=30),
                ft.Text("NOTLAR", color=gri_metin, size=10, weight="bold")
            ], alignment="center", horizontal_alignment="center", spacing=10),
            tiklama_fonk=lambda e: kutuya_tiklandi("Not Defteri")
        )

        kutu_16 = kutu_yap(
            ft.Column([
                ft.Container(content=ft.Text("🎵", size=22), padding=12, bgcolor="#1A1A1E", border_radius=30),
                ft.Text("MÜZİK", color=gri_metin, size=10, weight="bold")
            ], alignment="center", horizontal_alignment="center", spacing=10),
            tiklama_fonk=lambda e: kutuya_tiklandi("Spotify / Müzik")
        )

        bot_ikon = ft.Text("🔴", size=12)
        bot_metin = ft.Text("AI BOT KAPALI", color=gri_metin, size=11, weight="900")
        kutu_8 = ft.Container(
            content=ft.Row([bot_ikon, bot_metin], alignment="center", spacing=8),
            data="kapali",
            border_radius=18, padding=10,
            gradient=ft.LinearGradient(begin=ft.Alignment(-1.0, -1.0), end=ft.Alignment(1.0, 1.0), colors=["#141416", kutu_zemin]),
            animate=ft.Animation(300, ft.AnimationCurve.DECELERATE),
        )
        kutu_8.on_click = lambda e: ai_bot_tetikle(e, kutu_8, bot_metin, bot_ikon)

        kutu_9 = kutu_yap(
            ft.Row([
                ft.Text("🎙️", size=18), 
                ft.Text("SOHBET", color="white", size=11, weight="900"),
                ft.Row([
                    ft.Container(width=3, height=8, bgcolor=luks_turuncu, border_radius=2),
                    ft.Container(width=3, height=14, bgcolor=luks_turuncu, border_radius=2),
                    ft.Container(width=3, height=10, bgcolor=luks_turuncu, border_radius=2),
                ], spacing=2)
            ], alignment="center", spacing=8),
            tiklama_fonk=lambda e: kutuya_tiklandi("AI Sohbet")
        )

        kutu_10 = kutu_yap(
            ft.Row([
                ft.Column([
                    ft.Text("💰 TOPLAM BAKİYE", color=gri_metin, weight="bold", size=10),
                    ft.Text("$12,450.00", color="white", weight="900", size=22)
                ], spacing=0, alignment="center"),
                ft.Container(content=ft.Text("💼", size=24), padding=12, bgcolor="#1A1A1E", border_radius=15)
            ], alignment="spaceBetween"),
            yukseklik=80, padding_deg=15,
            tiklama_fonk=lambda e: kutuya_tiklandi("Ana Cüzdan")
        )

        kutu_11 = kutu_yap(
            ft.Column([
                ft.Text("📊", size=26), 
                ft.Text("PORTFÖY\nÖZETİ", color="white", size=10, weight="bold", text_align="center")
            ], alignment="center", horizontal_alignment="center", spacing=8),
            tiklama_fonk=lambda e: kutuya_tiklandi("Cüzdan Detay")
        )

        kutu_12 = kutu_yap(
            ft.Column([
                ft.Text("⚙️", size=26), 
                ft.Text("AYARLAR", color="white", size=10, weight="bold", text_align="center")
            ], alignment="center", horizontal_alignment="center", spacing=8),
            tiklama_fonk=lambda e: kutuya_tiklandi("Sistem Ayarları")
        )

        kutu_13 = kutu_yap(
            ft.Column([
                ft.Container(
                    content=ft.Text("Q", size=20, color="white", weight="bold"),
                    width=50, height=50, bgcolor=luks_turuncu, border_radius=25, alignment=ft.Alignment(0,0)
                ),
                ft.Text("QYPEE", color="white", weight="900", size=14),
                badge_yap("PRO ÜYE", "#1A1A1E", mat_altin)
            ], alignment="center", horizontal_alignment="center", spacing=8),
            tiklama_fonk=lambda e: kutuya_tiklandi("Profil Ekranı")
        )

        satir_2 = ft.Row([
            ft.Container(content=kutu_2, expand=1, height=150), 
            ft.Column([
                ft.Container(content=kutu_3, expand=1), 
                ft.Container(content=kutu_4, expand=1)  
            ], expand=1, height=150, spacing=bosluk)
        ], spacing=bosluk)

        satir_4 = ft.Row([
            ft.Container(content=kutu_6, expand=1, height=75), 
            ft.Container(content=kutu_7, expand=1, height=75)  
        ], spacing=bosluk)

        satir_5 = ft.Row([
            ft.Container(content=kutu_15, expand=2, height=160), 
            ft.Container(content=kutu_14, expand=3, height=160), 
            ft.Container(content=kutu_16, expand=2, height=160)  
        ], spacing=bosluk)

        satir_6 = ft.Row([
            ft.Container(content=kutu_8, expand=1, height=65), 
            ft.Container(content=kutu_9, expand=1, height=65)  
        ], spacing=bosluk)

        satir_8 = ft.Row([
            ft.Column([
                ft.Container(content=kutu_11, expand=1), 
                ft.Container(content=kutu_12, expand=1)  
            ], expand=1, height=170, spacing=bosluk),
            ft.Container(content=kutu_13, expand=1, height=170) 
        ], spacing=bosluk)

        return ft.Column([
            kutu_1,         
            satir_2,        
            kutu_5,         
            satir_4,        
            satir_5,        
            satir_6,        
            kutu_10,        
            satir_8         
        ], expand=True, scroll="auto", spacing=bosluk)

    ana_ekran_kapsayici.content = dashboard_arayuzunu_kur()
    return ana_ekran_kapsayici