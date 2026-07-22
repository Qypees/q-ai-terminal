import flet as ft
import time
import threading

def splash_ekrani(page: ft.Page, sonraki_asama):
    page.controls.clear()
    
    # ft.Icon çökmeye sebep olduğu için, terminal simgesini metin olarak (>_) tasarladık
    logo = ft.Text(">_", size=90, color="#00ffcc", weight="bold")
    baslik = ft.Text("Q-AI TERMİNAL", size=32, weight="bold", color="white")
    alt_yazi = ft.Text("Sistem Başlatılıyor...\nAğ Bağlantıları Kuruluyor...", size=16, text_align="center", color="white70")
    yukleniyor = ft.ProgressRing(color="#00ffcc", stroke_width=5)
    
    icerik = ft.Container(
        content=ft.Column(
            controls=[logo, baslik, alt_yazi, ft.Container(height=30), yukleniyor],
            alignment="center",
            horizontal_alignment="center"
        ),
        expand=True,
        bgcolor="#030303"
    )
    
    page.add(icerik)
    page.update()
    
    def bekle_ve_gec():
        time.sleep(3)
        sonraki_asama()
        
    threading.Thread(target=bekle_ve_gec).start()