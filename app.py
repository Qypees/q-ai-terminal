import flet as ft
import os
from dashboard import ana_ekran_olustur

def main(page: ft.Page):
    # --- SAYFA VE VİZYON AYARLARI ---
    page.title = "Q-AI Bulut Terminali"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#030303"
    
    # Bilgisayarda açıldığında telefon/tablet ekranı gibi görünmesi için (isteğe bağlı):
    page.window_width = 450 
    page.window_height = 850
    page.window_resizable = True

    # --- ANA EKRANA YÖNLENDİRİCİ MOTOR ---
    def ana_ekrana_gecis_yap():
        page.controls.clear()
        ana_ekran = ana_ekran_olustur(page)
        page.add(ana_ekran)
        page.update()

    # Uygulama başladığı an Dashboard'u ateşler
    ana_ekrana_gecis_yap()

if __name__ == "__main__":
    # 7/24 BULUT SUNUCUSU İÇİN DİNAMİK PORT VE WEB AYARLARI
    # Render, Railway gibi sunucular "PORT" değişkenini kendisi atar, bulamazsa 8080 kullanır.
    port = int(os.environ.get("PORT", 8080))
    
    # host="0.0.0.0" komutu, terminalini dış dünyaya (buluta) açan asıl anahtardır!
    ft.app(
        target=main, 
        view=ft.AppView.WEB_BROWSER, 
        port=port, 
        host="0.0.0.0"
    )