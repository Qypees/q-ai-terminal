import flet as ft
import os

from splash import splash_ekrani
from disclaimer import uyari_ekrani
from dashboard import ana_ekran_olustur

def main(page: ft.Page):
    # --- SAYFA VE VİZYON AYARLARI ---
    page.title = "Q-AI Bulut Terminali PRO"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#030303"
    
    page.window_width = 450 
    page.window_height = 850
    page.window_resizable = True
    
    # Tüm sayfalardan çağrılabilecek küresel Snackbar (Alttan çıkan bildirim)
    page.snack_bar = ft.SnackBar(
        content=ft.Text("Sistem Mesajı", color="white", weight="bold"),
        bgcolor="#107C10",
        duration=2000
    )

    # --- SİSTEM GEÇİŞ (ROUTING) MİMARİSİ ---
    def ana_ekrana_gecis_yap():   
        page.controls.clear()
        ana_ekran = ana_ekran_olustur(page)
        page.add(ana_ekran)
        page.update()

    def uyari_ekranina_gecis_yap():
        page.controls.clear()
        uyari_ekrani(page, ana_ekrana_gecis_yap)
        page.update()

    splash_ekrani(page, uyari_ekranina_gecis_yap)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    
    # "target=" kelimesi kaldırıldı, fonksiyon doğrudan birinci parametre (main) olarak verildi.
    if "PORT" in os.environ:
        ft.run(main, view=ft.AppView.WEB_BROWSER, port=port, host="0.0.0.0")
    else:
        ft.run(main)    