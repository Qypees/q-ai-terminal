import flet as ft
import time
import threading
import urllib.request
import urllib.error
import json
import concurrent.futures

# GITHUB'A YÜKLERKEN ŞİFRE BURADA KESİNLİKLE OLMAMALI
GROQ_API_KEY = "API_SIFRENIZI_BURAYA_GIRIN"

def ai_sohbet_sayfasi_olustur(page: ft.Page, geri_don_fonksiyonu):
    
    def cerceve_olustur(kalinlik, renk):
        kenar = ft.BorderSide(kalinlik, renk)
        return ft.Border(top=kenar, right=kenar, bottom=kenar, left=kenar)

    sohbet_gecmisi = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO, spacing=15)
    sesli_yanit_aktif = False

    def ses_modunu_degistir(e):
        nonlocal sesli_yanit_aktif
        sesli_yanit_aktif = e.control.value
        page.snack_bar.content.value = "🔊 Sesli Yanıt Motoru Aktif!" if sesli_yanit_aktif else "🔇 Sesli Yanıt Motoru Kapalı."
        page.snack_bar.bgcolor = "#00ffcc" if sesli_yanit_aktif else "#EF4444"
        page.snack_bar.open = True
        page.update()

    def sohbeti_temizle(e):
        sohbet_gecmisi.controls.clear()
        sohbet_gecmisi.controls.append(mesaj_balonu_olustur("Sohbet geçmişi temizlendi. Konsey yeni emirlerinizi bekliyor patron!", "ai"))
        page.update()

    def mesaj_balonu_olustur(mesaj, gonderen="ben"):
        if gonderen == "ai":
            balon = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Text("🤖", size=18),
                        bgcolor="#0F172A", padding=8, border_radius=20,
                        border=cerceve_olustur(1, "#00ffcc")
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text("Q-AI KONSEY", weight="bold", color="#00ffcc", size=11),
                                ft.Text("3-Ajan Sentezi", color="#64748B", size=10, italic=True)
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Text(mesaj, color="#E2E8F0", size=14, selectable=True)
                        ], spacing=5),
                        bgcolor="#0A0A0E", padding=15, border_radius=15,
                        border=ft.Border(left=ft.BorderSide(3, "#00ffcc"), bottom=ft.BorderSide(1, "#1A1A24")),
                        shadow=[ft.BoxShadow(blur_radius=20, color="#00ffcc", spread_radius=-12)],
                        width=520
                    )
                ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.START),
                margin=5
            )
        else:
            balon = ft.Container(
                content=ft.Row([
                    ft.Container(
                        content=ft.Text(mesaj, color="white", size=14, selectable=True),
                        bgcolor="#1E1E2E", padding=15, border_radius=15,
                        border=cerceve_olustur(1, "#313244"),
                        width=380
                    ),
                    ft.Container(
                        content=ft.Text("👤", size=18),
                        bgcolor="#1E1E2E", padding=8, border_radius=20,
                        border=cerceve_olustur(1, "#89B4FA")
                    )
                ], alignment=ft.MainAxisAlignment.END, vertical_alignment=ft.CrossAxisAlignment.START),
                margin=5
            )
        return balon

    def konus_motoru(metin):
        def run_tts():
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.say(metin)
                engine.runAndWait()
            except Exception:
                pass
        threading.Thread(target=run_tts, daemon=True).start()

    def mesaj_gonder(metin_degeri=None):
        mesaj = metin_degeri if metin_degeri else mesaj_girdisi.value
        if not mesaj: return
        
        mesaj_girdisi.value = ""
        sohbet_gecmisi.controls.append(mesaj_balonu_olustur(mesaj, "ben"))
        page.update()

        yaziyor_gostergesi = ft.Container(
            content=ft.Row([
                ft.ProgressRing(width=16, height=16, color="#00ffcc", stroke_width=2),
                ft.Text("Konsey toplanıyor (Teknik + Piyasa + Risk)...", color="#00ffcc", size=12, italic=True)
            ]),
            margin=10
        )
        sohbet_gecmisi.controls.append(yaziyor_gostergesi)
        page.update()

        def groq_ajani_cagir(sistem_rolu, model_adi, kullanici_sorusu):
            try:
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {GROQ_API_KEY.strip()}",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0"
                }
                veri = {
                    "model": model_adi, 
                    "messages": [
                        {"role": "system", "content": sistem_rolu},
                        {"role": "user", "content": kullanici_sorusu}
                    ]
                }
                req = urllib.request.Request(url, data=json.dumps(veri).encode('utf-8'), headers=headers)
                with urllib.request.urlopen(req) as response:
                    return json.loads(response.read().decode('utf-8'))['choices'][0]['message']['content']
            except Exception as ex:
                return f"[{model_adi} Hata: {str(ex)}]"

        def konseyi_yonet():
            ai_cevap = ""
            try:
                rol_teknik = "Sen bir kripto teknik analistisin. Sadece fiyata, destek-direnç noktalarına ve formasyonlara odaklan. Çok kısa özet geç."
                model_teknik = "llama-3.1-8b-instant"

                rol_duygu = "Sen bir kripto piyasa araştırmacısısın. Hacimlere, piyasa duyarlılığına, balina hareketlerine ve genel trende odaklan. Kısa özet geç."
                model_duygu = "mixtral-8x7b-32768"

                rol_risk = "Sen bir kripto risk yöneticisisin. Sadece potansiyel düşüş senaryolarına, stop-loss seviyelerine ve risklere odaklan. Kısa özet geç."
                model_risk = "gemma2-9b-it"

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    gorev_teknik = executor.submit(groq_ajani_cagir, rol_teknik, model_teknik, mesaj)
                    gorev_duygu = executor.submit(groq_ajani_cagir, rol_duygu, model_duygu, mesaj)
                    gorev_risk = executor.submit(groq_ajani_cagir, rol_risk, model_risk, mesaj)

                    cevap_teknik = gorev_teknik.result()
                    cevap_duygu = gorev_duygu.result()
                    cevap_risk = gorev_risk.result()

                rol_mudur = (
                    "Sen siberpunk tarzı, zeki bir kripto asistanısın (Adın Q-AI). Kullanıcıya 'patron' de. "
                    "Arka plandaki 3 ajanının sana sunduğu aşağıdaki analizleri oku ve bunları birleştirerek "
                    "kullanıcıya tek, akıcı, kendinden emin ve havalı bir nihai cevap yaz. "
                    "Asla 'Uzmanlar böyle diyor' deme. Analizleri sen yapmışsın gibi doğrudan konuş. Çok uzatma.\n\n"
                    f"Teknik Analiz: {cevap_teknik}\nPiyasa Durumu: {cevap_duygu}\nRisk Analizi: {cevap_risk}"
                )
                
                ai_cevap = groq_ajani_cagir(rol_mudur, "llama-3.1-8b-instant", mesaj)

            except Exception as hata:
                ai_cevap = f"Konsey toplanamadı. Ağ bağlantısı koptu: {str(hata)}"

            sohbet_gecmisi.controls.remove(yaziyor_gostergesi)
            sohbet_gecmisi.controls.append(mesaj_balonu_olustur(ai_cevap, "ai"))
            
            if sesli_yanit_aktif and "Hata" not in ai_cevap:
                konus_motoru(ai_cevap)

            page.update()

        threading.Thread(target=konseyi_yonet, daemon=True).start()

    mesaj_girdisi = ft.TextField(
        hint_text="Q-AI Konseyine bir coin sor veya analiz iste...",
        bgcolor="transparent", border_color="transparent", color="white",
        expand=True, on_submit=lambda e: mesaj_gonder()
    )

    def hizli_soru_butonu(etiket, soru_metni):
        return ft.Container(
            content=ft.Text(etiket, color="#00ffcc", size=12, weight="bold"),
            bgcolor="#0A0A0E", 
            padding=10,
            border_radius=15, 
            border=cerceve_olustur(1, "#1A1A24"),
            on_click=lambda e: mesaj_gonder(soru_metni), ink=True
        )

    hizli_oneriler = ft.Row([
        hizli_soru_butonu("⚡ BTC Analizi", "Bitcoin (BTC) için teknik, piyasa ve risk analizi yap."),
        hizli_soru_butonu("🔮 ETH Durumu", "Ethereum (ETH) güncel durumu nedir, yön neresi?"),
        hizli_soru_butonu("🛡️ Piyasa Riski", "Şu an genel kripto piyasasında risk seviyesi nedir?")
    ], scroll=ft.ScrollMode.AUTO, spacing=10)

    girdi_alani = ft.Container(
        content=ft.Column([
            hizli_oneriler,
            ft.Row([
                mesaj_girdisi,
                ft.Container(
                    content=ft.Text("🚀", size=20),
                    on_click=lambda e: mesaj_gonder(),
                    padding=10, ink=True, border_radius=20,
                    bgcolor="#00ffcc1A"
                )
            ])
        ], spacing=8),
        bgcolor="#0A0A0E", border_radius=20, padding=12, 
        border=cerceve_olustur(1, "#1A1A24")
    )

    ust_bar = ft.Row([
        ft.Row([
            ft.Text("🤖", size=26),
            ft.Column([
                ft.Text("Q-AI KRİPTO ASİSTAN", size=18, weight="900", color="white"),
                ft.Row([
                    ft.Container(width=8, height=8, border_radius=4, bgcolor="#10B981", shadow=ft.BoxShadow(blur_radius=6, color="#10B981")),
                    ft.Text("Konsey Çevrimiçi (3 Ajan)", color="#10B981", size=11, weight="bold")
                ], spacing=5)
            ], spacing=2)
        ]),
        ft.Row([
            # İKON MODÜLÜ TAMAMEN DEVRE DIŞI BIRAKILDI, YERİNE EMOJİ BUTONU EKLENDİ
            ft.Container(content=ft.Text("🗑️", size=20), tooltip="Sohbeti Temizle", on_click=sohbeti_temizle, ink=True, padding=5, border_radius=5),
            ft.Text("Ses:", color="#737373", size=12),
            ft.Switch(value=False, active_color="#00ffcc", on_change=ses_modunu_degistir)
        ], alignment=ft.MainAxisAlignment.END)
    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    sohbet_gecmisi.controls.append(mesaj_balonu_olustur("Sistem Çevrimiçi. Llama-3.1, Mixtral ve Gemma ajanları senkronize edildi. Emrindeyim patron!", "ai"))

    ana_icerik = ft.Container(
        content=ft.Column([
            ust_bar, ft.Divider(color="#1A1A24"),
            ft.Container(content=sohbet_gecmisi, expand=True, padding=5),
            girdi_alani
        ], expand=True),
        bgcolor="#030304", padding=15, expand=True
    )

    return ft.Container(
        content=ft.Column([
            ft.TextButton(content=ft.Text("⬅️ Panoya Dön", color="#3B82F6"), on_click=lambda e: geri_don_fonksiyonu()), 
            ana_icerik
        ], expand=True),
        bgcolor="#030304", padding=10, expand=True
    )