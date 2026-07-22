import flet as ft

def uyari_ekrani(page: ft.Page, kabul_edildi_fonksiyonu):
    page.controls.clear()
    
    # Hata veren ikon yerine uyarı emojisi kullanıldı
    ikon = ft.Text("⚠️", size=70)
    baslik = ft.Text("YASAL UYARI", size=28, weight="bold", color="red")
    
    metin = ft.Text(
        "Bu terminal (Q-AI), tamamen kişisel geliştirme ve analiz amacıyla oluşturulmuştur.\n\n"
        "İçerisinde yer alan yapay zeka verileri, sinyaller ve teknik analiz grafiklerinin hiçbiri YATIRIM TAVSİYESİ DEĞİLDİR.\n\n"
        "Kripto para piyasalarında işlem yapmak yüksek risk taşır. Sistem algoritmalarının ürettiği sonuçlardan kaynaklanabilecek zararlardan geliştirici sorumlu tutulamaz.\n\n"
        "Sisteme giriş yaparak tüm riskleri ve bu metni kabul etmiş sayılırsınız.",
        size=15, 
        text_align="center", 
        color="white70"
    )
    
    buton = ft.ElevatedButton(
        content=ft.Text("OKUDUM VE KABUL EDİYORUM", color="white", weight="bold"),
        bgcolor="green",
        height=50,
        on_click=lambda e: kabul_edildi_fonksiyonu() 
    )
    
    icerik = ft.Container(
        content=ft.Column(
            controls=[ikon, baslik, ft.Container(height=10), metin, ft.Container(height=30), buton],
            alignment="center",
            horizontal_alignment="center"
        ),
        padding=30,
        expand=True,
        bgcolor="#030303"
    )
    
    page.add(icerik)
    page.update()