import flet as ft
import os

# Tüm zincirin parçalarını ana motora dahil ediyoruz
from splash import splash_ekrani
from disclaimer import uyari_ekrani
from dashboard import ana_ekran_olustur

def main(page: ft.Page):
    # --- SAYFA VE VİZYON AYARLARI ---
    page.title = "Q-AI Bulut Terminali"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#030303"
    
    # Bilgisayarda açıldığında telefon/tablet ekranı gibi görünmesi için:
    page.window_width = 450 
    page.window_height = 850
    page.window_resizable = True

    # --- SİSTEM GEÇİŞ (ROUTING) MİMARİSİ ---
    
    # 3. Adım: Yasal uyarı kabul edilince ana paneli (Dashboard) yükle
    def ana_ekrana_gecis_yap():
        page.controls.clear()
        ana_ekran = ana_ekran_olustur(page)
        page.add(ana_ekran)
        page.update()
        # Not: Dashboard zaten kendi içinde market, haberler, grafik ve ai modüllerini çağırıyor.

    # 2. Adım: Splash bitince Yasal Uyarı (Disclaimer) ekranını yükle
    def uyari_ekranina_gecis_yap():
        page.controls.clear()
        # disclaimer.py'deki uyari_ekrani fonksiyonu bizden page ve kabul_edildi_fonksiyonu bekler
        uyari_ekrani(page, ana_ekrana_gecis_yap)
        page.update()

    # 1. Adım: Uygulama başladığı an Splash (Açılış Animasyonu) ekranını ateşler
    # splash.py 3 saniye animasyon oynatıp otomatik olarak uyari_ekranina_gecis_yap fonksiyonunu tetikler.
    splash_ekrani(page, uyari_ekranina_gecis_yap)


if __name__ == "__main__":
    # 7/24 BULUT SUNUCUSU İÇİN DİNAMİK PORT VE WEB AYARLARI
    # Render, Railway gibi sunucular "PORT" değişkenini kendisi atar, bulamazsa 8080 kullanır.
    port = int(os.environ.get("PORT", 8080))
    
    # host="0.0.0.0" komutu, terminalini dış dünyaya (buluta) açan asıl anahtardır.
    ft.app(
        target=main, 
        view=ft.AppView.WEB_BROWSER, 
        port=port, 
        host="0.0.0.0"
    )