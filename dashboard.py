import flet as ft

def ana_ekran_olustur(page: ft.Page):
    
    # 1. ÜST BAR: Logo, Arama Çubuğu ve Profil
    ust_bar = ft.Row(
        controls=[
            ft.Text("🚀 Q-AI", size=22, weight="bold", color="#00ffcc"),
            ft.Container(
                content=ft.TextField(
                    hint_text="Coin Ara (Örn: BTC)...",
                    bgcolor="#111111",
                    border_color="#00ffcc",
                    color="white",
                    height=40,
                    content_padding=10,
                    text_size=14,
                ),
                width=180
            ),
            ft.Text("👤", size=24)
        ],
        alignment="spaceBetween"
    )

    # 2. ZAMAN DİLİMİ (Timeframe) SEÇİCİ
    zaman_dilimleri = ft.Row(
        controls=[
            ft.ElevatedButton(content=ft.Text("15m", color="white"), bgcolor="#222222"),
            ft.ElevatedButton(content=ft.Text("1h", color="black", weight="bold"), bgcolor="#00ffcc"),
            ft.ElevatedButton(content=ft.Text("4h", color="white"), bgcolor="#222222"),
            ft.ElevatedButton(content=ft.Text("1D", color="white"), bgcolor="#222222"),
        ],
        spacing=10
    )

    # 3. TRADINGVIEW GRAFİK ALANI
    grafik_alani = ft.Container(
        content=ft.Column([
            ft.Text("📊 TradingView (BTC/USDT)", size=16, weight="bold", color="#00ffcc"),
            ft.Container(height=20),
            ft.Text("📈 Canlı veri akışı sağlanıyor...", color="white70"),
            ft.Text("Grafik modülü aktif.", color="white38", size=12)
        ], alignment="center", horizontal_alignment="center"),
        bgcolor="#111111",
        height=220,
        border_radius=10
        # ÇÖKMEYE SEBEP OLAN 'alignment=ft.alignment.center' SATIRI BURADAN SİLİNDİ!
    )

    # 4. YAPAY ZEKA SİNYAL VE HABER ÖZETİ MODÜLÜ
    ai_analiz_paneli = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Text("🧠", size=20),
                ft.Text("AI Analiz & Haber Özeti", size=18, weight="bold", color="white")
            ]),
            ft.Divider(color="white24"),
            ft.ListTile(
                leading=ft.Text("🟢", size=20),
                title=ft.Text("BTC - GÜÇLÜ AL SİNYALİ", color="white", weight="bold"),
                subtitle=ft.Text("Kurumsal alım haberleri piyasayı destekliyor. Hedef: $65.500", color="white70")
            ),
            ft.ListTile(
                leading=ft.Text("🔴", size=20),
                title=ft.Text("SOL - DÜZELTME RİSKİ", color="white", weight="bold"),
                subtitle=ft.Text("Ağ yoğunluğu endişeleri artıyor. Destek seviyesi: $135", color="white70")
            )
        ]),
        bgcolor="#111111",
        padding=15,
        border_radius=10
    )

    # 5. TÜM MODÜLLERİ ANA EKRANDA BİRLEŞTİRME
    ana_icerik = ft.Container(
        content=ft.Column(
            controls=[
                ust_bar,
                ft.Container(height=15),
                zaman_dilimleri,
                ft.Container(height=15),
                grafik_alani,
                ft.Container(height=15),
                ai_analiz_paneli
            ],
            scroll="auto"
        ),
        padding=20,
        expand=True,
        bgcolor="#030303"
    )
    
    return ana_icerik