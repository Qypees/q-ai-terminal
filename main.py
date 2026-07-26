from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import requests
import uvicorn
import datetime
import urllib.parse
import time
import re
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json
import os

app = FastAPI(title="Qypees Terminal Core")
templates = Jinja2Templates(directory="templates")

# ==========================================
# YEREL VERİTABANI SİSTEMİ (JSON) - SİMÜLASYON KAYIT
# ==========================================
DB_DOSYASI = "cuzdan.json"

def veritabani_yukle():
    if os.path.exists(DB_DOSYASI):
        with open(DB_DOSYASI, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"spot": [], "vadeli": []}

def veritabani_kaydet():
    veri = {"spot": spot_varliklar, "vadeli": aktif_pozisyonlar}
    with open(DB_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=4)

db_veri = veritabani_yukle()
spot_varliklar = db_veri["spot"]
aktif_pozisyonlar = db_veri["vadeli"]

onayli_kullanicilar = set()
spotify_tokens = {}

# Spotify API Kimlik Bilgileri
SPOTIFY_CLIENT_ID = "d560d37532284575a7933231cf7166f3"
SPOTIFY_CLIENT_SECRET = "BURAYA_CLIENT_SECRET_DEGERINI_YAZ"
SPOTIFY_REDIRECT_URI = "https://q-ai-terminal.onrender.com/callback"

sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="user-read-playback-state,user-modify-playback-state,playlist-read-private,playlist-read-collaborative"
)

class ChatRequest(BaseModel):
    mesaj: str

class SpotVarlikRequest(BaseModel):
    borsa: str
    bakiye: str
    detay: str

class VadeliPozisyonRequest(BaseModel):
    coin: str
    kaldirac: str
    yon: str
    miktar: str

# ==========================================
# 1. ANA ÇEKİRDEK VERİTABANI (200 COIN)
# ==========================================
COIN_FIYATLARI = {
    # Mevcut 100 Coin
    "BTC": 64500.0, "ETH": 3100.0, "USDT": 1.0, "BNB": 580.0, "SOL": 145.0,
    "USDC": 1.0, "XRP": 0.60, "TON": 6.5, "DOGE": 0.15, "ADA": 0.45,
    "SHIB": 0.000025, "AVAX": 35.0, "DOT": 7.0, "LINK": 14.0, "BCH": 450.0,
    "TRX": 0.11, "MATIC": 0.70, "NEAR": 6.5, "UNI": 7.5, "LTC": 85.0,
    "ICP": 12.0, "DAI": 1.0, "FET": 2.1, "RNDR": 8.5, "APT": 9.0,
    "SUI": 1.2, "ARB": 1.1, "OP": 2.5, "PEPE": 0.000008, "WIF": 2.8,
    "INJ": 25.0, "FIL": 5.5, "GRT": 0.30, "LDO": 2.0, "STX": 2.2,
    "TAO": 400.0, "MNT": 1.2, "CRO": 0.12, "XLM": 0.10, "ATOM": 8.5,
    "OKB": 45.0, "XMR": 130.0, "HBAR": 0.10, "VET": 0.035, "MKR": 2800.0,
    "IMX": 2.0, "KAS": 0.15, "THETA": 2.2, "AAVE": 95.0, "QNT": 105.0,
    "SNX": 2.5, "BSV": 65.0, "ALGO": 0.18, "EGLD": 40.0, "RUNE": 5.5,
    "TIA": 10.0, "BONK": 0.000015, "FLOKI": 0.00015, "BGB": 1.1, "GALA": 0.04,
    "SAND": 0.45, "MANA": 0.45, "AERO": 1.0, "JUP": 1.1, "PYTH": 0.45,
    "STRK": 1.2, "DYDX": 2.1, "SEI": 0.55, "GMX": 30.0, "CFX": 0.22,
    "BLUR": 0.40, "FTM": 0.80, "WLD": 4.5, "ORDI": 35.0, "SATS": 0.0003,
    "ZETA": 1.5, "PENDLE": 5.5, "ENS": 22.0, "XTZ": 0.95, "EOS": 0.80,
    "CHZ": 0.11, "APE": 1.2, "ILV": 85.0, "IOTA": 0.22, "AXS": 7.5,
    "COMP": 55.0, "NEO": 14.5, "MINA": 0.85, "FLOW": 0.95, "WEMIX": 1.5,
    "CAKE": 2.5, "KAVA": 0.70, "GNO": 300.0, "ONDO": 0.95, "BOME": 0.012,
    "JASMY": 0.02, "ROSE": 0.09, "GLM": 0.45, "CORE": 1.8, "RON": 2.8,

    # Yeni Eklenen 100 Coin (Veritabanı 200'e Yükseltildi)
    "ZEC": 25.0, "DASH": 30.0, "XEC": 0.00004, "KSM": 35.0, "ENJ": 0.3,
    "BAT": 0.25, "ZIL": 0.02, "RVN": 0.03, "HOT": 0.002, "1INCH": 0.4,
    "LRC": 0.25, "YFI": 7000.0, "SUSHI": 1.2, "CRV": 0.45, "CHR": 0.3,
    "ALICE": 1.5, "REEF": 0.002, "DENT": 0.001, "CKB": 0.015, "TFUEL": 0.08,
    "ONT": 0.25, "IOST": 0.01, "SKL": 0.08, "CVC": 0.15, "SXP": 0.35,
    "OCEAN": 0.9, "BAND": 1.5, "NKN": 0.1, "COTI": 0.1, "CTSI": 0.2,
    "AR": 25.0, "KDA": 1.2, "LUNC": 0.0001, "USTC": 0.02, "ZEN": 12.0,
    "CELO": 0.8, "GTC": 1.5, "MTL": 1.8, "DGB": 0.01, "ICX": 0.25,
    "OMG": 0.8, "QTUM": 3.5, "SC": 0.008, "BNT": 0.7, "STORJ": 0.6,
    "ANT": 5.5, "BAL": 4.0, "REN": 0.08, "KNC": 0.6, "NMR": 20.0,
    "UMA": 2.8, "RLC": 2.5, "MASK": 3.5, "GAL": 3.0, "API3": 2.2,
    "DAR": 0.15, "TLM": 0.02, "GHST": 1.5, "LPT": 15.0, "RAD": 1.8,
    "SUPER": 1.0, "RSR": 0.006, "ALPHA": 0.15, "BEL": 0.8, "LIT": 1.2,
    "UNFI": 4.5, "BAKE": 0.3, "DODO": 0.2, "PERP": 1.2, "BADGER": 4.0,
    "TRB": 80.0, "TWT": 1.2, "SFP": 0.8, "XVS": 8.0, "MBOX": 0.35,
    "FRONT": 0.8, "FORTH": 3.5, "OGN": 0.15, "LINA": 0.008, "AKRO": 0.005,
    "OXT": 0.08, "STPT": 0.05, "DATA": 0.05, "TROY": 0.003, "VITE": 0.02,
    "WRX": 0.2, "WTC": 0.02, "GXS": 0.3, "AION": 0.02, "LTO": 0.15,
    "VTHO": 0.003, "FIO": 0.03, "TCT": 0.01, "PNT": 0.15, "DOCK": 0.02,
    "HIVE": 0.35, "TKO": 0.4, "COS": 0.01, "KEY": 0.006, "MDT": 0.05
}
COINLER = list(COIN_FIYATLARI.keys())

# ==========================================
# 2. CANLI BİNANCE VE ÖNBELLEK SİSTEMİ (%100 GERÇEK PİYASA OKUMA)
# ==========================================
binance_cache = {"data": [], "last_update": 0}
haberler_cache = {"data": [], "last_update": 0}

def get_live_binance_data():
    now = time.time()
    if now - binance_cache["last_update"] > 3:
        try:
            res = requests.get("https://api.binance.com/api/v3/ticker/24hr", timeout=5)
            binance_cache["data"] = res.json()
            binance_cache["last_update"] = now
        except:
            pass
    return binance_cache["data"]

def coklu_piyasa_verilerini_cek():
    live_data = get_live_binance_data()
    piyasa_verileri = []
    binance_dict = {item['symbol']: item for item in live_data}
    
    for coin in COINLER:
        symbol_usdt = f"{coin}USDT"
        if symbol_usdt in binance_dict:
            b_data = binance_dict[symbol_usdt]
            fiyat = float(b_data['lastPrice'])
            degisim = float(b_data['priceChangePercent'])
            hacim = float(b_data['quoteVolume']) / 1000000
        else:
            fiyat = 1.0 if coin in ["USDT", "USDC", "DAI"] else 0.0
            degisim = 0.0
            hacim = 0.0
        
        # %100 GERÇEK VERİYE DAYALI MATEMATİKSEL YORUM SİSTEMİ (Rastgelelik KALDIRILDI)
        if degisim >= 7.0:
            yon = "STRONG LONG 🚀"
            ai_yorum = "Güçlü Trend / Hacim Kırılımı"
        elif degisim >= 2.0:
            yon = "LONG 🟢"
            ai_yorum = "Pozitif İvme"
        elif degisim <= -7.0:
            yon = "STRONG SHORT 🩸"
            ai_yorum = "Sert Düşüş / Destek Kaybı"
        elif degisim <= -2.0:
            yon = "SHORT 🔴"
            ai_yorum = "Negatif Baskı"
        else:
            yon = "YATAY 🟡"
            if hacim > 250:
                ai_yorum = "Yüksek Hacimli Sıkışma"
            else:
                ai_yorum = "Düşük Hacimli Konsolidasyon"
                
        piyasa_verileri.append({"sembol": coin, "fiyat": fiyat, "degisim": degisim, "hacim": hacim, "ai_yon": yon, "ai_yorum": ai_yorum})
    
    piyasa_verileri.sort(key=lambda x: x["hacim"], reverse=True)
    return piyasa_verileri

def gercek_piyasa_verisi_cek():
    live_data = get_live_binance_data()
    for item in live_data:
        if item['symbol'] == "BTCUSDT": return {"sembol": "BTC/USDT", "fiyat": float(item['lastPrice'])}
    return {"sembol": "BTC/USDT", "fiyat": 64000.0}

def top5_verilerini_cek(zaman="1d"):
    tum_coinler = coklu_piyasa_verilerini_cek()
    hareketli_coinler = [c for c in tum_coinler if c["sembol"] not in ["USDT", "USDC", "DAI"]]
    sirali = sorted(hareketli_coinler, key=lambda x: x['degisim'])
    return {"yukselenler": list(reversed(sirali[-5:])), "dusenler": sirali[:5]}

def isiharitasi_verilerini_cek(zaman="1d"):
    tum_coinler = coklu_piyasa_verilerini_cek()
    hareketli_coinler = [c for c in tum_coinler if c["sembol"] not in ["USDT", "USDC", "DAI"]]
    return sorted(hareketli_coinler, key=lambda x: x['hacim'], reverse=True)

# ==========================================
# 3. AI BİRLEŞİK BEYİN VE HABERLER
# ==========================================
def cevir_ingilizce_turkce(metin):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=tr&dt=t&q={urllib.parse.quote(metin)}"
        response = requests.get(url, timeout=3)
        return "".join([x[0] for x in response.json()[0]])
    except:
        return metin 

def ai_haber_analizi(metin):
    metin_kucuk = metin.lower()
    yuksek_onemli = ["sec", "etf", "onay", "yasadışı", "faiz", "enflasyon", "kara para", "hack", "çöküş", "iflas", "yasak", "dava"]
    onemli = ["güncelleme", "ortaklık", "listeleme", "ağ", "balina", "transfer", "entegrasyon", "yakım"]
    if any(kelime in metin_kucuk for kelime in yuksek_onemli): onem, onem_renk, kaldirac = "YÜKSEK ÖNEMLİ 🚨", "#EF4444", "Temel Analiz: Yüksek Volatilite Beklentisi"
    elif any(kelime in metin_kucuk for kelime in onemli): onem, onem_renk, kaldirac = "ÖNEMLİ ⚠️", "#F59E0B", "Temel Analiz: Orta Volatilite Beklentisi"
    else: onem, onem_renk, kaldirac = "STANDART ℹ️", "#3B82F6", "Temel Analiz: Olağan Akış"
    return onem, onem_renk, "GERÇEK ZAMANLI 🟢", "#10B981", kaldirac, "Piyasa analizi güncel."

def son_dakika_haberlerini_cek():
    now = time.time()
    if now - haberler_cache["last_update"] < 60 and haberler_cache["data"]:
        if haberler_cache["data"][0]["kaynak"] != "AI Sistem": return haberler_cache["data"]
    try:
        url = "https://api.rss2json.com/v1/api.json?rss_url=https://cointelegraph.com/rss"
        response = requests.get(url, timeout=10)
        data = response.json()
        if 'items' not in data: raise ValueError("RSS Okunamadı")
        haberler = []
        for item in data['items'][:12]:
            zaman = item['pubDate'][11:16]
            turkce_baslik = cevir_ingilizce_turkce(item['title'])
            turkce_ozet = cevir_ingilizce_turkce(re.sub('<[^<]+>', '', item['description'])[:250] + "...")
            onem, onem_renk, yon, yon_renk, kaldirac, ai_yorum = ai_haber_analizi(turkce_baslik + " " + turkce_ozet)
            haberler.append({"baslik": turkce_baslik, "ozet": turkce_ozet, "kaynak": "CoinTelegraph", "url": item['link'], "zaman": zaman, "onem": onem, "onem_renk": onem_renk, "yon": yon, "yon_renk": yon_renk, "kaldirac": kaldirac, "ai_yorum": ai_yorum})
        haberler_cache["data"] = haberler
        haberler_cache["last_update"] = now
        return haberler
    except:
        return [{"baslik": "Veri Çekiliyor...", "ozet": "Haber akışı güncelleniyor.", "kaynak": "Sistem", "url": "#", "zaman": "Şimdi", "onem": "BEKLEYİN", "onem_renk": "#6B7280", "yon": "YÜKLENİYOR", "yon_renk": "#6B7280", "kaldirac": "-", "ai_yorum": "İletişim kuruluyor."}]

def uclu_ai_birlesik_yanit(mesaj: str):
    mesaj_k = mesaj.lower()
    btc_veri = gercek_piyasa_verisi_cek()
    btc_fiyat = btc_veri["fiyat"]
    if any(k in mesaj_k for k in ["selam", "merhaba", "hi", "naber", "günaydın"]):
        return f"Merhaba Patron! Q-AI Terminal Çekirdek Sistemi tam kapasiteyle emrinizde. Şu an Bitcoin (BTC) anlık olarak **${btc_fiyat:,.2f}** seviyesinde işlem görüyor."
    elif "btc" in mesaj_k or "bitcoin" in mesaj_k:
        return f"👑 **Q-AI Kurumsal Piyasa Raporu: Bitcoin (BTC)**\n\n• **Anlık Fiyat:** ${btc_fiyat:,.2f}\n• **Sistem Notu:** Ekrandaki tüm veriler Binance API'sinden gelen filtrelenmemiş, gerçek verilerdir."
    else:
        return f"🔍 **Q-AI Değerlendirmesi:** '{mesaj}' talebiniz incelendi. İşlemlerinizi Binance üzerinden manuel yaparken Terminal verilerini referans alabilirsiniz."

# ==========================================
# 4. JSON API UÇ NOKTALARI 
# ==========================================
@app.get("/api/piyasa")
async def api_piyasa(): return JSONResponse(content=coklu_piyasa_verilerini_cek())

@app.get("/api/btc")
async def api_btc(): return JSONResponse(content=gercek_piyasa_verisi_cek())

@app.get("/api/haberler")
async def api_haberler(): return JSONResponse(content=son_dakika_haberlerini_cek())

@app.get("/api/top5")
async def api_top5(zaman: str = "1d"): return JSONResponse(content=top5_verilerini_cek(zaman))

@app.get("/api/isiharitasi_data")
async def api_isiharitasi_data(zaman: str = "1d"): return JSONResponse(content=isiharitasi_verilerini_cek(zaman))

@app.post("/api/sohbet")
async def api_sohbet(req: ChatRequest): return JSONResponse(content={"yanit": uclu_ai_birlesik_yanit(req.mesaj)})

@app.get("/api/cuzdan/spot")
async def api_cuzdan_spot_get(): return JSONResponse(content=spot_varliklar)

@app.post("/api/cuzdan/spot")
async def api_cuzdan_spot_post(req: SpotVarlikRequest):
    spot_varliklar.append({"borsa": req.borsa, "bakiye": req.bakiye, "detay": req.detay if req.detay else "Detay girilmedi"})
    veritabani_kaydet()
    return JSONResponse(content={"durum": "basarili"})

@app.delete("/api/cuzdan/spot/{index}")
async def api_cuzdan_spot_delete(index: int):
    if 0 <= index < len(spot_varliklar): 
        spot_varliklar.pop(index)
        veritabani_kaydet()
    return JSONResponse(content={"durum": "silindi"})

@app.get("/api/cuzdan/vadeli")
async def api_cuzdan_vadeli_get(): return JSONResponse(content=aktif_pozisyonlar)

@app.post("/api/cuzdan/vadeli")
async def api_cuzdan_vadeli_post(req: VadeliPozisyonRequest):
    coin = req.coin.upper()
    yon = req.yon
    kaldirac = req.kaldirac
    ai_yorum = f"Terminal Kaydı: {coin} / {kaldirac}X {yon}. Bu işlem borsaya iletilmemiş, manuel takibiniz için panoya kaydedilmiştir."
    aktif_pozisyonlar.append({"coin": coin, "kaldirac": kaldirac, "yon": yon, "miktar": req.miktar, "zaman": datetime.datetime.now().strftime("%H:%M"), "ai_yorum": ai_yorum})
    veritabani_kaydet()
    return JSONResponse(content={"durum": "basarili"})

@app.delete("/api/cuzdan/vadeli/{index}")
async def api_cuzdan_vadeli_delete(index: int):
    if 0 <= index < len(aktif_pozisyonlar): 
        aktif_pozisyonlar.pop(index)
        veritabani_kaydet()
    return JSONResponse(content={"durum": "silindi"})

# --- SPOTIFY API NOKTALARI ---
@app.get("/spotify/giris")
async def spotify_giris():
    auth_url = sp_oauth.get_authorize_url()
    return RedirectResponse(url=auth_url)

@app.get("/callback")
async def spotify_callback(request: Request, code: str):
    try:
        token_info = sp_oauth.get_access_token(code)
        spotify_tokens[request.client.host] = token_info['access_token']
    except Exception as e:
        print("Spotify Token Hatası:", e)
    return RedirectResponse(url="/muzik?spotify=baglandi", status_code=303)

@app.get("/api/spotify/kendi_listelerim")
async def api_spotify_listeler(request: Request):
    token = spotify_tokens.get(request.client.host)
    if not token:
        return JSONResponse(content={"durum": "hata", "mesaj": "Spotify bağlantısı yok."})
    try:
        sp = spotipy.Spotify(auth=token)
        kullanici_listeleri = sp.current_user_playlists(limit=6) 
        listeler = []
        for item in kullanici_listeleri['items']:
            listeler.append({
                "id": item['id'],
                "isim": item['name']
            })
        return JSONResponse(content={"durum": "basarili", "listeler": listeler})
    except Exception as e:
        return JSONResponse(content={"durum": "hata", "mesaj": str(e)})

# ==========================================
# 5. GÜVENLİK VE YÖNLENDİRME KONTROLÜ
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def splash_ekrani(request: Request): 
    onayli_kullanicilar.discard(request.client.host)
    return templates.TemplateResponse(request=request, name="splash.html", context={"request": request})

@app.get("/disclaimer", response_class=HTMLResponse)
async def yasal_uyari_sayfasi(request: Request): 
    return templates.TemplateResponse(request=request, name="disclaimer.html", context={"request": request})

@app.get("/onayla")
async def oturum_onayla(request: Request):
    onayli_kullanicilar.add(request.client.host)
    return RedirectResponse(url="/pano", status_code=303)

def yetki_kontrol(request: Request):
    return request.client.host in onayli_kullanicilar

@app.get("/pano", response_class=HTMLResponse)
async def ana_ekran(request: Request): 
    if not yetki_kontrol(request): return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="index.html", context={"request": request})

@app.get("/piyasa", response_class=HTMLResponse)
async def piyasa_sayfasi(request: Request): 
    if not yetki_kontrol(request): return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="piyasa.html", context={"request": request})

@app.get("/haberler", response_class=HTMLResponse)
async def haberler_sayfasi(request: Request): 
    if not yetki_kontrol(request): return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="haberler.html", context={"request": request})

@app.get("/sinyaller", response_class=HTMLResponse)
async def sinyaller_sayfasi(request: Request): 
    if not yetki_kontrol(request): return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="sinyaller.html", context={"request": request})

@app.get("/top5", response_class=HTMLResponse)
async def top5_sayfasi(request: Request): 
    if not yetki_kontrol(request): return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="top5.html", context={"request": request})

@app.get("/isiharitasi", response_class=HTMLResponse)
async def isiharitasi_sayfasi(request: Request): 
    if not yetki_kontrol(request): return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="isiharitasi.html", context={"request": request})

@app.get("/cuzdan", response_class=HTMLResponse)
async def cuzdan_sayfasi(request: Request): 
    if not yetki_kontrol(request): return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="cuzdan.html", context={"request": request})

@app.get("/sohbet", response_class=HTMLResponse)
async def sohbet_sayfasi(request: Request): 
    if not yetki_kontrol(request): return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="sohbet.html", context={"request": request})

@app.get("/muzik", response_class=HTMLResponse)
async def muzik_sayfasi(request: Request): 
    if not yetki_kontrol(request): return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="muzik.html", context={"request": request})

@app.get("/{sayfa_adi}", response_class=HTMLResponse)
async def sayfa_yonlendir(request: Request, sayfa_adi: str):
    if not yetki_kontrol(request): return RedirectResponse(url="/", status_code=303)
    try: return templates.TemplateResponse(request=request, name=f"{sayfa_adi}.html", context={"request": request})
    except: return templates.TemplateResponse(request=request, name="yapim_asamasinda.html", context={"request": request, "sayfa": sayfa_adi.upper()})

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)