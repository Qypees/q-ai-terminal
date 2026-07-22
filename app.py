import flet as ft
from splash import splash_ekrani
from disclaimer import uyari_ekrani
from dashboard import ana_ekran_olustur

def main(page: ft.Page):
    page.title = "Q-AI Bulut Terminali"
    page.window_width = 450
    page.window_height = 850
    page.bgcolor = "#030303"
    page.update() # Ekranı anında siyaha boyar

    def ana_ekrana_gecis_yap(e=None):
        page.controls.clear()
        page.add(ana_ekran_olustur(page))
        page.update()

    def uyari_ekranina_gecis_yap():
        uyari_ekrani(page, ana_ekrana_gecis_yap)

    splash_ekrani(page, uyari_ekranina_gecis_yap)

if __name__ == "__main__":
    ft.app(target=main)