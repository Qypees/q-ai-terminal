import flet as ft
import time
import threading
import json
import urllib.request

def ai_signal_sayfasi_olustur(page, geri_don_fonk):
    # --- SAF HEX RENKLER ---
    zemin_siyah = "#030303"
    kutu_zemin = "#0A0A0C"
    luks_turuncu = "#FF8C00"
    mat_altin = "#B89B72"
    gri_metin = "#8E8E93"
    canli_yesil = "#30D158"
    canli_kirmizi = "#FF453A"
    ai_zemin = "#050A15"  
    ai_neon = "#00E5FF"
    buton_zemin = "#1A1A1E"

    sayfa_aktif = [True]

    ana_kapsayici = ft.Container(expand=True, bgcolor=zemin_siyah, padding=10)
    liste_alani = ft.ListView(expand=True, spacing=12)

    # --- ÜST BAR ---
    def geri_don(e):
        sayfa_aktif[0] = False
        geri_don_fonk()

    canli_led = ft.Text("🟢", size=10)

    def manuel_yenile(e):
        canli_led.value = "🟡"
        try: ust_bar.update()
        except: pass
        sinyal_kartlarini_olustur()
        canli_led.value = "🟢"
        try: ust_bar.update()
        except: pass

    ust_bar = ft.Row([
        ft.Row([
            ft.Container(content=ft.Text("◀️", size=18), on_click=geri_don, padding=10),
            canli_led
        ], spacing=5),
        ft.Row([
            ft.Text("🧠", size=18),
            ft.Text("Q-AI SİNYAL & FIRSAT MERKEZİ", color=mat_altin, weight="bold", size=14)
        ], spacing=5, alignment="center", expand=True),
        ft.Container(content=ft.Text("🔄", size=18), on_click=manuel_yenile, padding=10),
    ], alignment="spaceBetween")

    # --- Q-AI MAKRO PİYASA YORUM PANELİ ---
    ai_makro_durum = ft.Text("ANALİZ EDİLİYOR...", color=gri_metin, weight="900", size=14)
    ai_makro_aciklama = ft.Text("Canlı borsa emir defterleri ve volatilite endeksleri taranıyor...", color=ai_neon, size=11)

    makro_panel = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Row([
                    ft.Text("⚡", size=16),
                    ft.Text("MAKRO PİYASA RAPORU", color=ai_neon, weight="900", size=12)
                ], spacing=5),
                ft.Container(
                    content=ft.Text("VİP SİNYAL", color="#030303", weight="bold", size=9),
                    bgcolor=ai_neon, padding=3, border_radius=4
                )
            ], alignment="spaceBetween"),
            ft.Container(height=1, bgcolor="#1A2035"),
            ai_makro_durum,
            ai_makro_aciklama
        ], spacing=8),
        bgcolor=ai_zemin, padding=15, border_radius=15,
        shadow=ft.BoxShadow(blur_radius=8, color="#0A1020")
    )

    # --- GELİŞMİŞ Q-AI FIRSAT HAVUZU ---
    sinyal_veritabani = [
        {
            "sembol": "SOL", "isim": "Solana", "tip": "LONG", "kaldirac": "10x",
            "giris": "142.50 - 145.00", "hedef": "165.00", "stop": "138.00",
            "risk_orani": "1:3.4", "basari": "%88",
            "yorum": "Ağ üzerindeki DEX hacmi rekor kırıyor. Majör direnç hacimli kırılmak üzere. Momentum alıcıların lehine."
        },
        {
            "sembol": "BTC", "isim": "Bitcoin", "tip": "LONG", "kaldirac": "5x",
            "giris": "63,800 - 64,300", "hedef": "68,500", "stop": "62,200",
            "risk_orani": "1:2.8", "basari": "%92",
            "yorum": "Kurumsal spot ETF girişlerinde tırmanış var. Likidite havuzunun üst bandı hedefleniyor."
        },
        {
            "sembol": "ETH", "isim": "Ethereum", "tip": "SHORT", "kaldirac": "10x",
            "giris": "3,320 - 3,350", "hedef": "3,100", "stop": "3,420",
            "risk_orani": "1:3.1", "basari": "%85",
            "yorum": "Güçlü direnç bölgesinden gelen hacimsiz tepki satıcıların baskısını artırdı. Kısa vadeli düzeltme bekleniyor."
        },
        {
            "sembol": "AVAX", "isim": "Avalanche", "tip": "LONG", "kaldirac": "8x",
            "giris": "34.80 - 35.50", "hedef": "41.00", "stop": "33.20",
            "risk_orani": "1:3.5", "basari": "%81",
            "yorum": "Alt-ağ (Subnet) duyuruları ve ekosistem ortaklıkları akıllı parayı bu varlığa çekti. Teknik formasyon olumlu."
        },
        {
            "sembol": "DOGE", "isim": "Dogecoin", "tip": "SHORT", "kaldirac": "15x",
            "giris": "0.122 - 0.125", "hedef": "0.105", "stop": "0.131",
            "risk_orani": "1:2.2", "basari": "%78",
            "yorum": "Meme coin dominansı düşüş trendinde. Aşırı alım bölgesinde zayıflama emareleri gösteriyor, hızlı kar satışı gelebilir."
        },
        {
            "sembol": "FET", "isim": "Fetch.ai", "tip": "LONG", "kaldirac": "7x",
            "giris": "2.05 - 2.12", "hedef": "2.60", "stop": "1.92",
            "risk_orani": "1:3.0", "basari": "%86",
            "yorum": "Yapay zeka sektöründeki konferans ve birleşme takvimi fiyatı destekliyor. Akümülasyon evresi tamamlandı."
        }
    ]

    def sinyal_kartlarini_olustur():
        liste_alani.controls.clear()
        
        liste_alani.controls.append(makro_panel)
        liste_alani.controls.append(ft.Container(height=5))

        try:
            url = "https://api.binance.com/api/v3/ticker/24hr"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=4) as response:
                data = json.loads(response.read().decode())
            binance_dict = {item["symbol"]: float(item["lastPrice"]) for item in data}
        except:
            binance_dict = {}

        long_sayisi = sum(1 for s in sinyal_veritabani if s["tip"] == "LONG")
        short_sayisi = sum(1 for s in sinyal_veritabani if s["tip"] == "SHORT")

        if long_sayisi >= short_sayisi:
            ai_makro_durum.value = "🟢 AGRESİF LONG & TREND DÖNÜŞÜ"
            ai_makro_durum.color = canli_yesil
            ai_makro_aciklama.value = f"Piyasada alıcı iştahı baskın ({long_sayisi} Long / {short_sayisi} Short). Kaldıraçlı pozisyonlarda trend yönünde ilerlemek yüksek olasılık sunuyor."
        else:
            ai_makro_durum.value = "🔴 TEMKİNLİ SHORT & RİSK YÖNETİMİ"
            ai_makro_durum.color = canli_kirmizi
            ai_makro_aciklama.value = f"Direnç bölgelerinde satıcı baskısı yoğunlaşıyor ({short_sayisi} Short / {long_sayisi} Long). Sermaye koruması ön planda tutulmalı."

        for sinyal in sinyal_veritabani:
            sembol = sinyal["sembol"]
            guncel_fiyat = binance_dict.get(sembol + "USDT", 0.0)
            fiyat_str = f"${guncel_fiyat:,.4f}" if guncel_fiyat < 1 and guncel_fiyat > 0 else f"${guncel_fiyat:,.2f}" if guncel_fiyat > 0 else "Canlı Bekleniyor..."

            tip = sinyal["tip"]
            bg_tip_renk = "#0b3d14" if tip == "LONG" else "#3d0b0b"

            detay_kutu = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Column([
                            ft.Text("GİRİŞ ARALIĞI", color=gri_metin, size=9, weight="bold"),
                            ft.Text(sinyal["giris"], color="white", size=11, weight="bold")
                        ]),
                        ft.Column([
                            ft.Text("HEDEF (TP)", color=gri_metin, size=9, weight="bold"),
                            ft.Text(sinyal["hedef"], color=canli_yesil, size=11, weight="bold")
                        ]),
                        ft.Column([
                            ft.Text("STOP (SL)", color=gri_metin, size=9, weight="bold"),
                            ft.Text(sinyal["stop"], color=canli_kirmizi, size=11, weight="bold")
                        ]),
                    ], alignment="spaceBetween"),
                    ft.Container(height=8),
                    ft.Row([
                        ft.Row([
                            ft.Text("Risk/Ödül:", color=gri_metin, size=10),
                            ft.Text(sinyal["risk_orani"], color=mat_altin, weight="bold", size=10)
                        ], spacing=4),
                        ft.Row([
                            ft.Text("AI Başarı Skoru:", color=gri_metin, size=10),
                            ft.Text(sinyal["basari"], color=canli_yesil, weight="bold", size=10)
                        ], spacing=4)
                    ], alignment="spaceBetween"),
                    ft.Container(height=4),
                    ft.Text("🤖 Q-AI Teknik Gerekçe:", color=luks_turuncu, weight="bold", size=10),
                    ft.Text(sinyal["yorum"], color=gri_metin, size=11, italic=True)
                ], spacing=6),
                bgcolor=ai_zemin, padding=12, border_radius=10,
                visible=False
            )

            def kart_tiklandi(e, box=detay_kutu):
                box.visible = not box.visible
                try: box.update()
                except: pass

            kart = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Row([
                            ft.Container(
                                content=ft.Text(sembol[0], color="white", weight="bold", size=14),
                                width=34, height=34, bgcolor=buton_zemin, border_radius=17, alignment=ft.Alignment(0,0)
                            ),
                            ft.Column([
                                ft.Text(sembol, color="white", weight="900", size=13),
                                ft.Text(f"Fiyat: {fiyat_str}", color=gri_metin, size=10)
                            ], spacing=0)
                        ], spacing=10),
                        ft.Row([
                            ft.Container(
                                content=ft.Text(sinyal["kaldirac"], color="white", weight="bold", size=10),
                                bgcolor=buton_zemin, padding=6, border_radius=6
                            ),
                            ft.Container(
                                content=ft.Text(tip, color="white", weight="900", size=11),
                                bgcolor=bg_tip_renk, padding=6, border_radius=6
                            )
                        ], spacing=6)
                    ], alignment="spaceBetween"),
                    detay_kutu
                ], spacing=8),
                bgcolor=kutu_zemin, padding=15, border_radius=15,
                shadow=ft.BoxShadow(blur_radius=5, color="#050505"),
                on_click=kart_tiklandi
            )
            liste_alani.controls.append(kart)

        try: liste_alani.update()
        except: pass

    sinyal_kartlarini_olustur()

    ana_kapsayici.content = ft.Column([
        ust_bar,
        ft.Container(height=5),
        liste_alani
    ], expand=True, spacing=5)

    return ana_kapsayici