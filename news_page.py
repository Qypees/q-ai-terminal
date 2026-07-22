import flet as ft
import time
import threading
import json
import urllib.request
import urllib.parse
import ssl
import re
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime

def haber_sayfasi_olustur(page, geri_don_fonk):
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
    ilk_yukleme = [True] 
    kayitli_haber_idleri = set() 
    islem_suruyor = [False] 
    ai_gecmis_veriler = []

    ana_kapsayici = ft.Container(expand=True, bgcolor=zemin_siyah, padding=10)
    liste_alani = ft.ListView(expand=True, spacing=12)

    # --- BAŞLANGIÇ YÜKLENİYOR ANİMASYONU ---
    yukleniyor_kapsayici = ft.Container(
        content=ft.Column([
            ft.ProgressRing(color=luks_turuncu, stroke_width=3),
            ft.Container(height=10),
            ft.Text("Kripto Ağları Taranıyor...", color=gri_metin, size=12, weight="bold")
        ], horizontal_alignment="center", alignment="center"),
        alignment=ft.Alignment(0, 0),
        padding=100
    )
    liste_alani.controls.append(yukleniyor_kapsayici)

    # --- ÜST BAR ---
    def geri_don(e):
        sayfa_aktif[0] = False
        geri_don_fonk()

    canli_led = ft.Text("🟢", size=10)

    def manuel_yenile(e):
        if islem_suruyor[0]: return 
        
        canli_led.value = "🟡"
        try: ust_bar.update()
        except: pass
        
        liste_alani.controls.clear()
        liste_alani.controls.append(yukleniyor_kapsayici)
        kayitli_haber_idleri.clear()
        ai_gecmis_veriler.clear()
        ilk_yukleme[0] = True
        
        try: liste_alani.update()
        except: pass

        threading.Thread(target=haberleri_cek, daemon=True).start()

    ust_bar = ft.Row([
        ft.Row([
            ft.Container(content=ft.Text("◀️", size=18), on_click=geri_don, padding=10),
            canli_led
        ], spacing=5),
        ft.Row([
            ft.Text("📰", size=18),
            ft.Text("HABER AKIŞI", color=mat_altin, weight="bold", size=14)
        ], spacing=5, alignment="center", expand=True),
        ft.Container(content=ft.Text("🔄", size=18), on_click=manuel_yenile, padding=10),
    ], alignment="spaceBetween")

    # --- Q-AI MERKEZİ YÖNETİM PANELİ ---
    ai_durum_metni = ft.Text("TARANIYOR...", color=gri_metin, weight="900", size=14)
    ai_analiz_metni = ft.Text("Küresel ağlar dinleniyor, veriler toplanıyor...", color=ai_neon, size=11)
    ai_son_uyari = ft.Text("Bekleniyor...", color="white", weight="bold", size=10, max_lines=1)

    ai_yonetim_kapsayici = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Row([
                    ft.Text("🧠", size=16),
                    ft.Text("Q-AI KÜRESEL HABER BEYNİ", color=ai_neon, weight="900", size=12)
                ], spacing=5),
                ft.Container(
                    content=ft.Text("AKTİF", color="#030303", weight="bold", size=9),
                    bgcolor=ai_neon, padding=3, border_radius=4
                )
            ], alignment="spaceBetween"),
            ft.Container(height=1, bgcolor="#1A2035"), 
            ft.Row([
                ft.Column([
                    ft.Text("GENEL PİYASA YÖNÜ", color=gri_metin, size=9, weight="bold"),
                    ai_durum_metni
                ], spacing=0),
                ft.Column([
                    ft.Text("EN SON KRİTİK HABER", color=gri_metin, size=9, weight="bold"),
                    ft.Container(content=ai_son_uyari, width=150) 
                ], spacing=0, alignment="end")
            ], alignment="spaceBetween"),
            ai_analiz_metni
        ], spacing=8),
        bgcolor=ai_zemin, padding=15, border_radius=15,
        shadow=ft.BoxShadow(blur_radius=8, color="#0A1020")
    )

    # --- GOOGLE TRANSLATE ÇEVİRİ MOTORU ---
    def metni_ceviri_yap(text):
        if not text or len(text) < 3: return text
        try:
            kisa_metin = text[:800] 
            url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=tr&dt=t&q={urllib.parse.quote(kisa_metin)}"
            
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            with urllib.request.urlopen(req, timeout=5, context=ctx) as response:
                data = json.loads(response.read().decode('utf-8'))
                cevrilmis = "".join([sentence[0] for sentence in data[0] if sentence[0]])
                return cevrilmis
        except Exception:
            return text 

    # --- Q-AI DUYGU VE ETKİ ANALİZ MOTORU ---
    def ai_haber_analiz_et(orijinal_baslik, orijinal_detay):
        metin = (orijinal_baslik + " " + orijinal_detay).lower()
        
        bullish_kelimeler = ["etf", "approve", "buy", "bull", "surge", "launch", "partnership", "growth", "adopt", "upgrade", "invest", "breakout", "rally", "high", "soar"]
        bearish_kelimeler = ["sec", "ban", "hack", "drop", "bear", "lawsuit", "sell", "crash", "fed", "rate", "inflation", "scam", "delist", "sue", "warning", "fall", "plunge"]
        onemli_kelimeler = ["sec", "etf", "fed", "binance", "hack", "bank", "government", "war", "approved", "banned", "urgent", "vital"]

        bull_skor = sum(1 for kelime in bullish_kelimeler if kelime in metin)
        bear_skor = sum(1 for kelime in bearish_kelimeler if kelime in metin)
        
        onemli_mi = any(kelime in metin for kelime in onemli_kelimeler)
        
        if bear_skor > bull_skor:
            yon = "SHORT"
            renk = canli_kirmizi
            yorum = "Q-AI Tespiti: Haberde belirgin satış baskısı veya düzenleyici riski var. Likidite çıkışı yaşanabilir. Açığa satış (Short) mantıklıdır."
        elif bull_skor > bear_skor:
            yon = "LONG"
            renk = canli_yesil
            yorum = "Q-AI Tespiti: Haber kurumsal benimsenme veya teknolojik gelişim taşıyor. Anlık alım baskısı (Long) yaratacaktır."
        else:
            yon = "BEKLE"
            renk = gri_metin
            yorum = "Q-AI Tespiti: Bu haber piyasayı agresif yönlendirecek bir katalizör içermiyor. Nakitte kalıp izlemek en güvenlisidir."

        return onemli_mi, yon, renk, yorum

    # --- HTML TEMİZLEME VE ZAMAN HESAPLAMA ---
    def html_temizle(text):
        if not text: return "Detay bulunamadı."
        temiz = re.sub('<[^<]+>', '', text)
        temiz = temiz.replace('\n', ' ').replace('\t', ' ')
        return temiz.strip()

    def zaman_farki_hesapla(date_str):
        try:
            haber_zaman = parsedate_to_datetime(date_str).timestamp()
            fark = int(time.time() - haber_zaman)
            fark = max(0, fark)
            
            if fark < 60: return "ŞİMDİ"
            elif fark < 3600: return f"{fark//60} DK ÖNCE"
            elif fark < 86400: return f"{fark//3600} SAAT ÖNCE"
            else: return f"{fark//86400} GÜN ÖNCE"
        except:
            return "YENİ"

    # --- KART RENDER FONKSİYONU (PARALEL ÇEVİRİ MİMARİSİ) ---
    def haber_karti_olustur(haber):
        orijinal_baslik = haber.get("title", "")
        orijinal_detay = html_temizle(haber.get("description", ""))
        kaynak = "GÜNCEL" 
        zaman_etiketi = zaman_farki_hesapla(haber.get("pubDate", ""))
        
        # AI Analizi anında İngilizce metinden yapılır (Bekleme yok)
        onemli_mi, ai_yon, yon_renk, ai_yorum = ai_haber_analiz_et(orijinal_baslik, orijinal_detay)

        etki_bg = canli_kirmizi if onemli_mi else buton_zemin
        etki_txt = "🔥 ÖNEMLİ" if onemli_mi else kaynak.upper()
        etki_renk = "white" if onemli_mi else gri_metin

        # Flet Text nesneleri (İlk etapta İngilizce basılır, anında ekrana gelir)
        ui_baslik = ft.Text(orijinal_baslik, color="white", weight="bold", size=13)
        ui_detay = ft.Text(orijinal_detay[:150] + "...", color=gri_metin, size=11)
        ui_ceviri_durum = ft.Text("⏳ Çevriliyor...", color=luks_turuncu, size=9, weight="bold")

        detay_kapsayici = ft.Container(
            content=ft.Column([
                ft.Text("📰 Haber Özeti:", color=mat_altin, weight="bold", size=10),
                ui_detay, # Türkçe olunca değişecek
                ft.Container(height=5),
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text("🤖 Q-AI STRATEJİ & YORUM", color=luks_turuncu, weight="bold", size=10),
                            ft.Container(
                                content=ft.Text(ai_yon, color="white", weight="900", size=10),
                                bgcolor=yon_renk, padding=4, border_radius=4
                            )
                        ], alignment="spaceBetween"),
                        ft.Text(ai_yorum, color="#A0A0A5", size=11, italic=True)
                    ], spacing=6),
                    bgcolor=ai_zemin, padding=12, border_radius=8
                )
            ], spacing=4),
            visible=False 
        )

        def kart_tiklandi(e):
            detay_kapsayici.visible = not detay_kapsayici.visible
            try: detay_kapsayici.update()
            except: pass

        kart = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Row([
                        ft.Text(zaman_etiketi, color=gri_metin, size=9, weight="bold"),
                        ui_ceviri_durum # Çeviri durum ikonu
                    ], spacing=8),
                    ft.Container(
                        content=ft.Text(etki_txt, color=etki_renk, weight="900", size=8),
                        bgcolor=etki_bg, padding=4, border_radius=4
                    )
                ], alignment="spaceBetween"),
                
                ui_baslik, # Türkçe olunca değişecek
                detay_kapsayici 
            ], spacing=8),
            bgcolor=kutu_zemin, padding=15, border_radius=12,
            shadow=ft.BoxShadow(blur_radius=5, color="#050505"),
            on_click=kart_tiklandi
        )

        # ARKA PLANDA PARALEL ÇEVİRİ İŞLEMİ ATEŞLEYİCİSİ
        def arka_planda_cevir_ve_guncelle():
            tr_baslik = metni_ceviri_yap(orijinal_baslik)
            tr_detay = metni_ceviri_yap(orijinal_detay)
            
            if sayfa_aktif[0]:
                ui_baslik.value = tr_baslik
                ui_detay.value = tr_detay[:350] + "..." if len(tr_detay) > 350 else tr_detay
                ui_ceviri_durum.value = "🇹🇷 Türkçe"
                ui_ceviri_durum.color = canli_yesil
                
                try:
                    ui_baslik.update()
                    ui_detay.update()
                    ui_ceviri_durum.update()
                except: pass

        # Kart oluşturulur oluşturulmaz çeviriyi ayrı bir kolda (thread) başlatır
        threading.Thread(target=arka_planda_cevir_ve_guncelle, daemon=True).start()

        return kart, ai_yon, onemli_mi, orijinal_baslik

    # --- SIFIR GECİKMELİ DOĞRUDAN XML ÇEKİMİ ---
    def haberleri_cek():
        islem_suruyor[0] = True
        hedef_url = "https://cointelegraph.com/rss"

        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        gelismis_basliklar = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        try:
            req = urllib.request.Request(hedef_url, headers=gelismis_basliklar)
            with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
                xml_verisi = response.read()
            
            root = ET.fromstring(xml_verisi)
            haber_elemanlari = root.findall('.//item')
            
            yeni_haberler = []

            for item in haber_elemanlari:
                guid = item.find('guid').text if item.find('guid') is not None else item.find('title').text
                
                if guid not in kayitli_haber_idleri:
                    pubDate_str = item.find('pubDate').text if item.find('pubDate') is not None else ""
                    
                    try:
                        haber_zaman = parsedate_to_datetime(pubDate_str).timestamp()
                        fark = int(time.time() - haber_zaman)
                        if fark > 43200 and not ilk_yukleme[0]: 
                            continue 
                    except: pass
                    
                    haber_sozlugu = {
                        "guid": guid,
                        "title": item.find('title').text if item.find('title') is not None else "",
                        "description": item.find('description').text if item.find('description') is not None else "",
                        "pubDate": pubDate_str
                    }
                    yeni_haberler.append(haber_sozlugu)
                    kayitli_haber_idleri.add(guid)

            if ilk_yukleme[0] and len(yeni_haberler) > 0:
                liste_alani.controls.clear()
                ilk_yukleme[0] = False
                yeni_haberler = yeni_haberler[:10]

            eklendi = False
            for haber in reversed(yeni_haberler):
                # Ekrana anında düşer! Çeviri arka planda gerçekleşir.
                yeni_kart, ai_yon, onemli_mi, orj_baslik = haber_karti_olustur(haber)
                liste_alani.controls.insert(0, yeni_kart)
                
                ai_gecmis_veriler.insert(0, {"yon": ai_yon, "onemli": onemli_mi, "baslik": orj_baslik})
                if len(ai_gecmis_veriler) > 20: ai_gecmis_veriler.pop()
                    
                eklendi = True

            # Q-AI BEYİN PANELİNİ GÜNCELLEME İŞLEMİ
            if eklendi and sayfa_aktif[0]:
                long_sayisi = sum(1 for v in ai_gecmis_veriler if v["yon"] == "LONG")
                short_sayisi = sum(1 for v in ai_gecmis_veriler if v["yon"] == "SHORT")

                if long_sayisi > short_sayisi:
                    ai_durum_metni.value = "BULLISH (POZİTİF)"
                    ai_durum_metni.color = canli_yesil
                    ai_analiz_metni.value = f"Q-AI: Küresel haber akışında alım iştahı ağırlıkta. ({long_sayisi} Long / {short_sayisi} Short sinyali)"
                elif short_sayisi > long_sayisi:
                    ai_durum_metni.value = "BEARISH (NEGATİF)"
                    ai_durum_metni.color = canli_kirmizi
                    ai_analiz_metni.value = f"Q-AI: Satış baskısı ve düzenleyici endişeler ön planda. ({short_sayisi} Short / {long_sayisi} Long sinyali)"
                else:
                    ai_durum_metni.value = "NÖTR (KONSOLİDE)"
                    ai_durum_metni.color = luks_turuncu
                    ai_analiz_metni.value = "Q-AI: Haber akışı şu an piyasayı agresif yönlendirecek güçte değil."

                son_kritik = next((v for v in ai_gecmis_veriler if v["onemli"]), None)
                if son_kritik:
                    # Q-AI uyarıyı İngilizce baz aldı, o yüzden panele anında İngilizcesini basıyoruz. 
                    # 1 saniye sonra Türkçe çevirisi geldiği için problem yaratmaz.
                    kisa_baslik = son_kritik["baslik"][:25] + "..." if len(son_kritik["baslik"]) > 25 else son_kritik["baslik"]
                    ai_son_uyari.value = kisa_baslik
                    ai_son_uyari.color = canli_kirmizi
                else:
                    ai_son_uyari.value = "Kritik Uyarı Yok"
                    ai_son_uyari.color = gri_metin

                try: ai_yonetim_kapsayici.update()
                except: pass

                try: liste_alani.update()
                except: pass

            canli_led.value = "🟢" 
            try: ust_bar.update()
            except: pass

        except Exception as e:
            if ilk_yukleme[0]:
                liste_alani.controls.clear()
                hata_mesaji = ft.Container(
                    content=ft.Column([
                        ft.Text("⚠️", size=30),
                        ft.Text("Canlı Ağa Ulaşılamadı", color=canli_kirmizi, weight="bold"),
                        ft.Text("Sistem yenileniyor...", color=gri_metin, size=10, text_align="center")
                    ], horizontal_alignment="center", alignment="center"),
                    alignment=ft.Alignment(0, 0), padding=50
                )
                liste_alani.controls.append(hata_mesaji)
                try: liste_alani.update()
                except: pass
        
        islem_suruyor[0] = False

    # --- ARKA PLAN DÖNGÜSÜ (KESİNTİSİZ 10 SANİYE PİNG) ---
    def otomatik_haber_motoru():
        while sayfa_aktif[0]:
            haberleri_cek()
            
            for _ in range(10):
                if not sayfa_aktif[0]: break
                time.sleep(1)

    threading.Thread(target=otomatik_haber_motoru, daemon=True).start()

    ana_kapsayici.content = ft.Column([
        ust_bar,
        ai_yonetim_kapsayici, 
        ft.Container(height=5),
        liste_alani
    ], expand=True, spacing=5)

    return ana_kapsayici