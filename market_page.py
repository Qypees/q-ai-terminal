import flet as ft
import time
import threading
import json
import urllib.request

def piyasa_sayfasi_olustur(page, geri_don_fonk):
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

    # --- PİYASA VERİLERİ ---
    tum_coinler_veritabani = [
        {"sembol": "BTC", "isim": "Bitcoin", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "Kurumsal alımlar hızlandı. RSI ve MACD yukarı yönlü momentumu destekliyor."},
        {"sembol": "ETH", "isim": "Ethereum", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "SHORT", "ai_yorum": "Dirençten reddedildi. Kısa vadeli hareketli ortalamalar aşağı kesti."},
        {"sembol": "BNB", "isim": "Binance Coin", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "Launchpool duyurusu hacmi artırdı. Üst direnç hedefleniyor."},
        {"sembol": "SOL", "isim": "Solana", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "Ağ aktivitesi rekor kırıyor. Akıllı para girişi çok güçlü."},
        {"sembol": "XRP", "isim": "Ripple", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "BEKLE", "ai_yorum": "Dava süreci belirsizliği sürüyor. Yön tayini için kırılım beklenmeli."},
        {"sembol": "DOGE", "isim": "Dogecoin", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "SHORT", "ai_yorum": "Meme coin trendi zayıfladı. Satış baskısı devam ediyor."},
        {"sembol": "ADA", "isim": "Cardano", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "SHORT", "ai_yorum": "Geliştirici aktivitesine rağmen fiyat hareketlenemiyor. Zayıf trend."},
        {"sembol": "AVAX", "isim": "Avalanche", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "Alt destekten net bir sekme görüldü. Hacim profili olumlu."},
        {"sembol": "SHIB", "isim": "Shiba Inu", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "BEKLE", "ai_yorum": "Sıkışma formasyonu var, patlama yönü henüz belirsiz."},
        {"sembol": "DOT", "isim": "Polkadot", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "BEKLE", "ai_yorum": "Konsolidasyon evresinde, dar bir bantta sıkıştı."},
        {"sembol": "LINK", "isim": "Chainlink", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "RWA trendi pozitif etkiliyor."},
        {"sembol": "MATIC", "isim": "Polygon", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "SHORT", "ai_yorum": "Diğer Layer-2 projelerinin rekabeti baskı yaratıyor."},
        {"sembol": "TRX", "isim": "TRON", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "Ağdaki USDT transferleri gelirleri artırıyor."},
        {"sembol": "LTC", "isim": "Litecoin", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "BEKLE", "ai_yorum": "Klasik destek noktalarında tutunuyor."},
        {"sembol": "BCH", "isim": "Bitcoin Cash", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "SHORT", "ai_yorum": "Madenci satışları fiyatı baskılıyor."},
        {"sembol": "UNI", "isim": "Uniswap", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "Merkeziyetsiz borsa hacimleri yükselişte."},
        {"sembol": "ATOM", "isim": "Cosmos", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "SHORT", "ai_yorum": "Ekosistem içi enflasyon endişeleri var."},
        {"sembol": "TON", "isim": "Toncoin", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "Telegram entegrasyonu devasa kullanıcı çekiyor."},
        {"sembol": "ICP", "isim": "Internet Comp.", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "AI destekli Web3 projeleri ivme kazandırıyor."},
        {"sembol": "RNDR", "isim": "Render", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "Yapay zeka ve GPU render talebi patlıyor."},
        {"sembol": "FET", "isim": "Fetch.ai", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "AI coin birleşmesi beklentisi pozitif."},
        {"sembol": "INJ", "isim": "Injective", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "SHORT", "ai_yorum": "Geçmişteki sert yükselişin düzeltmesi yaşanıyor."},
        {"sembol": "OP", "isim": "Optimism", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "BEKLE", "ai_yorum": "Base ağı ile olan sinerji takip ediliyor."},
        {"sembol": "ARB", "isim": "Arbitrum", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "BEKLE", "ai_yorum": "Kilit açılımları baskı oluşturmaya devam ediyor."},
        {"sembol": "SUI", "isim": "Sui", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "TVL hızla artıyor."},
        {"sembol": "APT", "isim": "Aptos", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "Kurumsal ortaklıklar ve Asya pazarı ilgisi var."},
        {"sembol": "PEPE", "isim": "Pepe", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "Meme coin sezonunun liderlerinden, momentum yüksek."},
        {"sembol": "WIF", "isim": "dogwifhat", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "Solana ekosisteminin en popüler meme coini."},
        {"sembol": "TIA", "isim": "Celestia", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "SHORT", "ai_yorum": "Airdrop avcılarının satışları devam ediyor."},
        {"sembol": "SEI", "isim": "Sei", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "BEKLE", "ai_yorum": "V2 güncellemesi bekleniyor."},
        {"sembol": "KAS", "isim": "Kaspa", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "PoW madencilerinden güçlü destek var."},
        {"sembol": "STX", "isim": "Stacks", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "Bitcoin DeFi ekosisteminin gelişimi fiyatlıyor."},
        {"sembol": "IMX", "isim": "Immutable", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "Web3 oyun projeleri ağa entegre oluyor."},
        {"sembol": "TAO", "isim": "Bittensor", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "Merkeziyetsiz AI sektörünün öncüsü."},
        {"sembol": "RUNE", "isim": "THORChain", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "Zincirler arası takas hacimleri yüksek."},
        {"sembol": "GALA", "isim": "Gala", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "SHORT", "ai_yorum": "Token ekonomisi haberleri baskıladı."},
        {"sembol": "MANA", "isim": "Decentraland", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "SHORT", "ai_yorum": "Metaverse ilgisi şu an piyasada zayıf."},
        {"sembol": "SAND", "isim": "The Sandbox", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "SHORT", "ai_yorum": "Kullanıcı sayısındaki düşüş trendi etkiliyor."},
        {"sembol": "AXS", "isim": "Axie Infinity", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "BEKLE", "ai_yorum": "Yeni oyun güncellemeleri test ediliyor."},
        {"sembol": "LDO", "isim": "Lido DAO", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "Ethereum staking oranları sürekli artıyor."},
        {"sembol": "THETA", "isim": "Theta Network", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "BEKLE", "ai_yorum": "Video streaming alanında yeni ortaklıklar bekleniyor."},
        {"sembol": "EGLD", "isim": "MultiversX", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "SHORT", "ai_yorum": "Hacim eksikliği fiyatın yükselmesini engelliyor."},
        {"sembol": "FTM", "isim": "Fantom", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "Sonic güncellemesi ile ağ hızlanıyor, ilgi arttı."},
        {"sembol": "ALGO", "isim": "Algorand", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "SHORT", "ai_yorum": "Piyasa genel yükselişlerine tepki vermekte zorlanıyor."},
        {"sembol": "FLOW", "isim": "Flow", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "BEKLE", "ai_yorum": "NFT piyasasındaki durgunluk fiyatı dondurdu."},
        {"sembol": "STRK", "isim": "Starknet", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "SHORT", "ai_yorum": "Airdrop sonrası satış baskısı tam atılamadı."},
        {"sembol": "DYDX", "isim": "dYdX", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "Kendi ağına geçişi hacimleri olumlu etkiledi."},
        {"sembol": "JUP", "isim": "Jupiter", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "Solana'nın en büyük DEX'i, hacim rekorları kırıyor."},
        {"sembol": "PYTH", "isim": "Pyth Network", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "Oracle alanında Chainlink'e güçlü rakip."},
        {"sembol": "ONDO", "isim": "Ondo", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "RWA sektörünün parlayan yıldızı."},
        {"sembol": "FLOKI", "isim": "FLOKI", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "Oyun entegrasyonu topluluğu diri tutuyor."},
        {"sembol": "BONK", "isim": "Bonk", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "SHORT", "ai_yorum": "Meme rekabetinde hacmi diğerlerine kayıyor."},
        {"sembol": "BOME", "isim": "BOOK OF MEME", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "BEKLE", "ai_yorum": "Sert dalgalanmalar sonrası konsolide oluyor."},
        {"sembol": "NOT", "isim": "Notcoin", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "Toncoin ekosistemiyle birlikte ralliye eşlik ediyor."},
        {"sembol": "JASMY", "isim": "JasmyCoin", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "Düzenlemeler pozitif etkiliyor."},
        {"sembol": "WLD", "isim": "Worldcoin", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "SHORT", "ai_yorum": "Düzenleyici baskılar etkili."},
        {"sembol": "PENDLE", "isim": "Pendle", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "Getiri ticareti (yield trading) ilgi görüyor."},
        {"sembol": "CORE", "isim": "Core", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "BEKLE", "ai_yorum": "Bitcoin entegrasyonu takipte."},
        {"sembol": "MKR", "isim": "Maker", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "Geri alımlar fiyatı koruyor."},
        {"sembol": "AAVE", "isim": "Aave", "fiyat": 0.0, "hacim": 0.0, "degisim": 0.0, "ai_yon": "LONG", "ai_yorum": "DeFi borç verme hacimleri canlanıyor."}
    ]

    aktif_coinler = list(tum_coinler_veritabani)

    ana_kapsayici = ft.Container(expand=True, bgcolor=zemin_siyah, padding=10)
    liste_alani = ft.ListView(expand=True, spacing=10)
    fiyat_kontrolleri = {} 

    def hacim_formatla(deger):
        if deger >= 1_000_000_000:
            return f"${deger/1_000_000_000:.2f}B"
        elif deger >= 1_000_000:
            return f"${deger/1_000_000:.2f}M"
        elif deger >= 1_000:
            return f"${deger/1_000:.2f}K"
        return f"${deger:.0f}"

    # --- ÜST BAR ---
    def geri_don(e):
        sayfa_aktif[0] = False
        geri_don_fonk()

    canli_led = ft.Text("🟢", size=10)

    arama_kutusu = ft.TextField(
        hint_text="Coin Ara...",
        bgcolor="#141416",
        color="white",
        border_radius=8,
        height=40,
        content_padding=10,
        visible=False,
    )

    def arama_ac_kapat(e):
        arama_kutusu.visible = not arama_kutusu.visible
        if not arama_kutusu.visible:
            arama_kutusu.value = ""
            arama_yap(None)
        ana_kapsayici.update()

    def arama_yap(e):
        nonlocal aktif_coinler
        sorgu = arama_kutusu.value.upper()
        if sorgu == "":
            aktif_coinler = list(tum_coinler_veritabani)
        else:
            aktif_coinler = [c for c in tum_coinler_veritabani if sorgu in c["sembol"] or sorgu in c["isim"].upper()]
        listeyi_ciz()

    arama_kutusu.on_change = arama_yap

    def manuel_yenile(e):
        canli_led.value = "🟡"
        try: ust_bar.update()
        except: pass
        listeyi_ciz()

    ust_bar = ft.Row([
        ft.Row([
            ft.Container(content=ft.Text("◀️", size=18), on_click=geri_don, padding=10),
            canli_led
        ], spacing=5),
        ft.Text("PİYASA", color=mat_altin, weight="bold", size=14, expand=True, text_align="center"),
        ft.Row([
            ft.Container(content=ft.Text("🔍", size=18), on_click=arama_ac_kapat, padding=10),
            ft.Container(content=ft.Text("🔄", size=18), on_click=manuel_yenile, padding=10),
            ft.Container(content=ft.Text("⚙️", size=18), padding=10),
        ], spacing=0)
    ], alignment="spaceBetween")

    # --- Q-AI MERKEZİ YÖNETİM PANELİ ---
    ai_durum_metni = ft.Text("BULLISH", color=canli_yesil, weight="900", size=14)
    ai_analiz_metni = ft.Text("Sistem piyasayı tarıyor...", color=ai_neon, size=11)
    ai_firsat_metni = ft.Text("Taranıyor...", color="white", weight="bold", size=12)
    ai_oran_metni = ft.Text("0%", color=gri_metin, size=10)

    ai_yonetim_kapsayici = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Row([
                    ft.Text("🧠", size=16),
                    ft.Text("Q-AI MERKEZİ", color=ai_neon, weight="900", size=12)
                ], spacing=5),
                ft.Container(
                    content=ft.Text("OTOMATİK", color="#030303", weight="bold", size=9),
                    bgcolor=ai_neon, padding=3, border_radius=4
                )
            ], alignment="spaceBetween"),
            ft.Container(height=1, bgcolor="#1A2035"), 
            ft.Row([
                ft.Column([
                    ft.Text("PİYASA YÖNÜ", color=gri_metin, size=9, weight="bold"),
                    ai_durum_metni
                ], spacing=0),
                ft.Column([
                    ft.Text("EN İYİ FIRSAT", color=gri_metin, size=9, weight="bold"),
                    ft.Row([ai_firsat_metni, ai_oran_metni], spacing=4)
                ], spacing=0, alignment="end")
            ], alignment="spaceBetween"),
            ai_analiz_metni
        ], spacing=8),
        bgcolor=ai_zemin,
        padding=15,
        border_radius=15,
        # HATA VEREN border KODU SİLİNDİ, YERİNE GÜVENLİ GÖLGE EKLENDİ
        shadow=ft.BoxShadow(blur_radius=8, color="#0A1020")
    )

    # --- SIRALAMA FONKSİYONLARI ---
    mevcut_siralama = "hacim_yuksek"

    def sirala(kriter):
        nonlocal mevcut_siralama
        mevcut_siralama = kriter
        
        if kriter == "fiyat_yuksek": aktif_coinler.sort(key=lambda x: x["fiyat"], reverse=True)
        elif kriter == "fiyat_dusuk": aktif_coinler.sort(key=lambda x: x["fiyat"])
        elif kriter == "hacim_yuksek": aktif_coinler.sort(key=lambda x: x["hacim"], reverse=True)
        elif kriter == "hacim_dusuk": aktif_coinler.sort(key=lambda x: x["hacim"])
        elif kriter == "az": aktif_coinler.sort(key=lambda x: x["sembol"])
        
        listeyi_ciz()

    filtre_bar = ft.Row([
        ft.Container(content=ft.Text("Fiyat ⬇", color=gri_metin, size=11), on_click=lambda e: sirala("fiyat_yuksek"), padding=8, bgcolor=buton_zemin, border_radius=8),
        ft.Container(content=ft.Text("Fiyat ⬆", color=gri_metin, size=11), on_click=lambda e: sirala("fiyat_dusuk"), padding=8, bgcolor=buton_zemin, border_radius=8),
        ft.Container(content=ft.Text("Hacim ⬇", color=gri_metin, size=11), on_click=lambda e: sirala("hacim_yuksek"), padding=8, bgcolor=buton_zemin, border_radius=8),
        ft.Container(content=ft.Text("Hacim ⬆", color=gri_metin, size=11), on_click=lambda e: sirala("hacim_dusuk"), padding=8, bgcolor=buton_zemin, border_radius=8),
        ft.Container(content=ft.Text("A-Z", color=gri_metin, size=11), on_click=lambda e: sirala("az"), padding=8, bgcolor=buton_zemin, border_radius=8),
    ], scroll="auto", spacing=8)

    # --- LİSTEYİ RENDER ETME ---
    def listeyi_ciz():
        fiyat_kontrolleri.clear()
        liste_alani.controls.clear()

        for c in aktif_coinler:
            fiyat_txt = ft.Text(f"${c['fiyat']:,.4f}" if c['fiyat'] < 1 else f"${c['fiyat']:,.2f}", color="white", weight="bold", size=14)
            degisim_txt = ft.Text(f"{'+' if c['degisim'] > 0 else ''}{c['degisim']:.2f}%", color=canli_yesil if c["degisim"] > 0 else canli_kirmizi, size=11)
            hacim_txt = ft.Text(f"Vol: {hacim_formatla(c['hacim'])}", color=gri_metin, size=9)

            ai_bg_renk = "#0b3d14" if c["ai_yon"] == "LONG" else "#3d0b0b" if c["ai_yon"] == "SHORT" else buton_zemin
            
            ai_yorum_kutu = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text("🧠 AI COİN ANALİZİ", color=luks_turuncu, weight="bold", size=11),
                        ft.Container(
                            content=ft.Text(c["ai_yon"], color="white", weight="900", size=10),
                            bgcolor=ai_bg_renk, padding=5, border_radius=5
                        )
                    ], alignment="spaceBetween"),
                    ft.Text(c["ai_yorum"], color=gri_metin, size=11)
                ]),
                bgcolor=ai_zemin, padding=12, border_radius=10, visible=False,
            )

            def coin_tiklandi(e, box=ai_yorum_kutu):
                box.visible = not box.visible
                try: box.update()
                except: pass

            satir = ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Row([
                            ft.Container(
                                content=ft.Text(c["sembol"][0], color="white", weight="bold", size=16),
                                width=38, height=38, bgcolor=buton_zemin, border_radius=19, alignment=ft.Alignment(0, 0)
                            ),
                            ft.Column([
                                ft.Text(c["sembol"], color="white", weight="bold", size=14),
                                hacim_txt
                            ], spacing=0)
                        ], spacing=10),
                        ft.Column([
                            fiyat_txt,
                            degisim_txt
                        ], alignment="end", spacing=0)
                    ], alignment="spaceBetween"),
                    ai_yorum_kutu
                ], spacing=8),
                bgcolor=kutu_zemin, padding=12, border_radius=15, on_click=coin_tiklandi
            )
            
            fiyat_kontrolleri[c["sembol"]] = {"fiyat_txt": fiyat_txt, "degisim_txt": degisim_txt, "hacim_txt": hacim_txt}
            liste_alani.controls.append(satir)
        
        try: liste_alani.update()
        except: pass

    listeyi_ciz()

    # --- GERÇEK BİNANCE API SANİYELİK GÜNCELLEME MOTORU VE AI BEYNİ ---
    def saniyelik_guncelleme_motoru():
        url = "https://api.binance.com/api/v3/ticker/24hr"

        while sayfa_aktif[0]:
            try:
                canli_led.value = "🟡"
                try: ust_bar.update() 
                except: pass

                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = json.loads(response.read().decode())
                
                binance_dict = {item["symbol"]: item for item in data}
                guncellendi = False

                # AI Analiz Değişkenleri
                yesil_sayisi = 0
                kirmizi_sayisi = 0
                en_cok_artan_coin = None
                en_yuksek_degisim = -999

                for c in tum_coinler_veritabani:
                    if not sayfa_aktif[0]: break
                    sembol_usdt = c["sembol"] + "USDT"
                    
                    if sembol_usdt in binance_dict:
                        item = binance_dict[sembol_usdt]
                        yeni_fiyat = float(item["lastPrice"])
                        yeni_degisim = float(item["priceChangePercent"])
                        
                        # AI Hesaplamaları
                        if yeni_degisim > 0: yesil_sayisi += 1
                        else: kirmizi_sayisi += 1

                        if yeni_degisim > en_yuksek_degisim:
                            en_yuksek_degisim = yeni_degisim
                            en_cok_artan_coin = c["sembol"]

                        if c["fiyat"] != yeni_fiyat:
                            c["eski_fiyat"] = c["fiyat"]
                            c["fiyat"] = yeni_fiyat
                            c["degisim"] = yeni_degisim
                            c["hacim"] = float(item["quoteVolume"])
                            guncellendi = True

                # Ekrana Yazma
                if guncellendi and sayfa_aktif[0]:
                    for sembol, kontroller in fiyat_kontrolleri.items():
                        c = next((coin for coin in tum_coinler_veritabani if coin["sembol"] == sembol), None)
                        if c:
                            txt_obje = kontroller["fiyat_txt"]
                            deg_obje = kontroller["degisim_txt"]
                            hac_obje = kontroller["hacim_txt"]

                            txt_obje.value = f"${c['fiyat']:,.4f}" if c['fiyat'] < 1 else f"${c['fiyat']:,.2f}"
                            deg_obje.value = f"{'+' if c['degisim'] > 0 else ''}{c['degisim']:.2f}%"
                            deg_obje.color = canli_yesil if c["degisim"] > 0 else canli_kirmizi
                            hac_obje.value = f"Vol: {hacim_formatla(c['hacim'])}"

                            if c["fiyat"] > c.get("eski_fiyat", 0) and c.get("eski_fiyat", 0) != 0:
                                txt_obje.color = canli_yesil
                            elif c["fiyat"] < c.get("eski_fiyat", 0) and c.get("eski_fiyat", 0) != 0:
                                txt_obje.color = canli_kirmizi

                            try:
                                txt_obje.update()
                                deg_obje.update()
                                hac_obje.update()
                            except: pass

                    # Q-AI YÖNETİM PANELİNİ GÜNCELLE
                    if yesil_sayisi > kirmizi_sayisi:
                        ai_durum_metni.value = f"BULLISH ({yesil_sayisi}/{len(tum_coinler_veritabani)})"
                        ai_durum_metni.color = canli_yesil
                        ai_analiz_metni.value = "Algoritmalar piyasada net bir alım baskısı tespit etti. Long işlemlere ağırlık veriliyor."
                    else:
                        ai_durum_metni.value = f"BEARISH ({kirmizi_sayisi}/{len(tum_coinler_veritabani)})"
                        ai_durum_metni.color = canli_kirmizi
                        ai_analiz_metni.value = "Satış baskısı hakim. Piyasadaki risk oranı yüksek, sermaye korunuyor."
                    
                    if en_cok_artan_coin:
                        ai_firsat_metni.value = en_cok_artan_coin
                        ai_oran_metni.value = f"+{en_yuksek_degisim:.2f}%"
                        ai_oran_metni.color = canli_yesil
                    
                    try: ai_yonetim_kapsayici.update()
                    except: pass

                    try: liste_alani.update()
                    except: pass

                    def rengi_normale_al():
                        time.sleep(0.4)
                        if sayfa_aktif[0]:
                            for sembol, kontroller in fiyat_kontrolleri.items():
                                kontroller["fiyat_txt"].color = "white"
                                try: kontroller["fiyat_txt"].update()
                                except: pass
                    
                    threading.Thread(target=rengi_normale_al, daemon=True).start()

                canli_led.value = "🟢"
                try: ust_bar.update()
                except: pass
                                    
            except Exception as e:
                pass

            time.sleep(2.0) 

    threading.Thread(target=saniyelik_guncelleme_motoru, daemon=True).start()

    ana_kapsayici.content = ft.Column([
        ust_bar,
        arama_kutusu,
        ai_yonetim_kapsayici,  
        ft.Container(height=5),
        filtre_bar,
        ft.Container(height=2),
        liste_alani
    ], expand=True, spacing=5)

    return ana_kapsayici