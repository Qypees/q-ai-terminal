from fastapi import FastAPI, Request, HTTPException
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
import httpx
import asyncio
from dotenv import load_dotenv

# Güvenli Ortam Değişkenleri Yüklemesi
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

app = FastAPI(title="Qypees Terminal Pro Core - 100x Enterprise Suite")
templates = Jinja2Templates(directory="templates")

# ==========================================
# YEREL VERİTABANI SİSTEMİ (JSON) - 100X MODÜL DESTEKLİ
# ==========================================
DB_DOSYASI = "cuzdan.json"

def veritabani_yukle():
    if os.path.exists(DB_DOSYASI):
        try:
            with open(DB_DOSYASI, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"spot": [], "vadeli": [], "paper_bakiye": 10000.0, "paper_islemler": [], "notlar": []}

def veritabani_kaydet():
    veri = {
        "spot": spot_varliklar, 
        "vadeli": aktif_pozisyonlar,
        "paper_bakiye": paper_bakiye,
        "paper_islemler": paper_islemler,
        "notlar": trade_notlari
    }
    try:
        with open(DB_DOSYASI, "w", encoding="utf-8") as f:
            json.dump(veri, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print("Veritabanı Kayıt Hatası:", e)

db_veri = veritabani_yukle()
spot_varliklar = db_veri.get("spot", [])
aktif_pozisyonlar = db_veri.get("vadeli", [])
paper_bakiye = db_veri.get("paper_bakiye", 10000.0)
paper_islemler = db_veri.get("paper_islemler", [])
trade_notlari = db_veri.get("notlar", [])

onayli_kullanicilar = set()
spotify_tokens = {}

# Spotify Kimlik Bilgileri
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "d560d37532284575a7933231cf7166f3")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "BURAYA_CLIENT_SECRET_DEGERINI_YAZ")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "https://q-ai-terminal.onrender.com/callback")

sp_oauth = SpotifyOAuth(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET,
    redirect_uri=SPOTIFY_REDIRECT_URI,
    scope="user-read-playback-state,user-modify-playback-state,playlist-read-private,playlist-read-collaborative"
)

# Pydantic İstek Modelleri
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

class PaperTradeRequest(BaseModel):
    coin: str
    yon: str
    kaldirac: str
    teminat: float

class RiskHesapRequest(BaseModel):
    giris_fiyati: float
    yon: str
    risk_istahi: str

class NotRequest(BaseModel):
    not_icerigi: str

# ==========================================
# 1. ANA ÇEKİRDEK VERİTABANI (200+ COİN)
# ==========================================
COIN_FIYATLARI = {
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
# 2. CANLI BİNANCE VE GELİŞMİŞ PİYASA MOTORU
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
            ai_yorum = "Yüksek Hacimli Sıkışma" if hacim > 250 else "Düşük Hacimli Konsolidasyon"
                
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
# 3. 100X KURUMSAL ÖZELLİK MODÜLLERİ (API UÇ NOKTALARI)
# ==========================================
@app.get("/api/likidasyon_haritasi")
async def api_likidasyon_haritasi():
    tum_veriler = coklu_piyasa_verilerini_cek()
    majorklar = [c for c in tum_veriler if c["sembol"] in ["BTC", "ETH", "SOL", "BNB", "XRP", "AVAX", "DOGE", "ADA"]]
    likidasyon_raporu = []
    for m in majorklar:
        fiyat = m["fiyat"]
        likidasyon_raporu.append({
            "coin": m["sembol"],
            "anlik_fiyat": fiyat,
            "yogun_short_patlatma": round(fiyat * 1.022, 2),
            "yogun_long_patlatma": round(fiyat * 0.978, 2),
            "risk_durumu": "KRİTİK BÖLGE 🚨" if abs(m["degisim"]) > 4 else "STABİL 🟢"
        })
    return JSONResponse(content=likidasyon_raporu)

@app.get("/api/balina_akimlari")
async def api_balina_akimlari():
    return JSONResponse(content=[
        {"zaman": "Az önce", "detay": "Binance borsasına 4,250 BTC aktarıldı.", "yon": "NEGATİF (Satış Baskısı)", "renk": "#EF4444"},
        {"zaman": "3 dk önce", "detay": "Cüzdanlardan soğuk depoya 125,000 ETH çekildi.", "yon": "POZİTİF (Arz Azalması)", "renk": "#10B981"},
        {"zaman": "8 dk önce", "detay": "Tether Treasury tarafından 500 Milyon USDT basıldı.", "yon": "BOĞA / LİKİDİTE GİRİŞİ", "renk": "#00ffcc"},
        {"zaman": "12 dk önce", "detay": "Whale Alert: Coinbase Pro'ya 45,000 SOL transfer edildi.", "yon": "ORTA SEVİYE RİSK", "renk": "#F59E0B"}
    ])

@app.get("/api/multitf_matris")
async def api_multitf_matris():
    tum_veriler = coklu_piyasa_verilerini_cek()
    majorklar = [c for c in tum_veriler if c["sembol"] in ["BTC", "ETH", "SOL", "BNB", "XRP", "AVAX", "ADA", "DOGE"]]
    matris_sonuc = []
    for m in majorklar:
        deg = m["degisim"]
        matris_sonuc.append({
            "coin": m["sembol"],
            "fiyat": m["fiyat"],
            "tf_15m": "AL 🟢" if deg > 0 else "SAT 🔴",
            "tf_1h": "GÜÇLÜ AL 🚀" if deg > 2 else ("NÖTR 🟡" if deg > -2 else "SAT 🔴"),
            "tf_4h": "BOĞA 📈" if deg > 1 else "AYI 📉",
            "tf_1d": m["ai_yon"]
        })
    return JSONResponse(content=matris_sonuc)

@app.post("/api/portfoy_doktoru")
async def api_portfoy_doktoru():
    toplam_spot_kalem = len(spot_varliklar)
    toplam_vadeli_poz = len(aktif_pozisyonlar)
    rapor = f"🩺 **Q-AI Portföy Sağlık Raporu (100x Denetim)**\n\n• **Spot Kalem:** {toplam_spot_kalem}\n• **Vadeli Pozisyon:** {toplam_vadeli_poz}\n• **Risk Puanı:** {'7.8 / 10 (Dikkat)' if toplam_vadeli_poz > 2 else '3.2 / 10 (Güvenli)'}\n• **Analiz:** "
    rapor += "⚠️ **Yüksek Kaldıraç Uyarısı!** Açık vadeli pozisyonların toplam portföye oranla risk sınırını zorluyor." if toplam_vadeli_poz > 3 else "✅ **Stabil Varlık Dağılımı.** Risk yönetimi kurumsal standartlarda ilerliyor."
    return JSONResponse(content={"rapor": rapor})

@app.get("/api/paper/durum")
async def api_paper_durum():
    return JSONResponse(content={"bakiye": paper_bakiye, "islemler": paper_islemler})

@app.post("/api/paper/islem_ac")
async def api_paper_islem_ac(req: PaperTradeRequest):
    global paper_bakiye
    if req.teminat > paper_bakiye:
        raise HTTPException(status_code=400, detail="Yetersiz sanal bakiye!")
    paper_bakiye -= req.teminat
    tum_veriler = coklu_piyasa_verilerini_cek()
    bulunan_fiyat = next((v["fiyat"] for v in tum_veriler if v["sembol"] == req.coin.upper()), 100.0)
    paper_islemler.append({
        "coin": req.coin.upper(), "yon": req.yon, "kaldirac": req.kaldirac,
        "teminat": req.teminat, "giris_fiyati": bulunan_fiyat, "zaman": datetime.datetime.now().strftime("%H:%M")
    })
    veritabani_kaydet()
    return JSONResponse(content={"durum": "basarili", "kalan_bakiye": paper_bakiye})

@app.post("/api/risk_hesapla")
async def api_risk_hesapla(req: RiskHesapRequest):
    fiyat = req.giris_fiyati
    carpim = 0.02 if req.risk_istahi == "DUSUK" else (0.04 if req.risk_istahi == "ORTA" else 0.07)
    if req.yon.upper() == "LONG":
        sl, tp = fiyat * (1 - carpim), fiyat * (1 + (carpim * 2))
    else:
        sl, tp = fiyat * (1 + carpim), fiyat * (1 - (carpim * 2))
    return JSONResponse(content={"giris": fiyat, "yon": req.yon.upper(), "stop_loss": round(sl, 4), "take_profit": round(tp, 4), "risk_odul_orani": "1 : 2"})

@app.get("/api/makro_takvim")
async def api_makro_takvim():
    return JSONResponse(content=[
        {"tarih": "Yarın, 15:30", "veri": "ABD Tarım Dışı İstihdam (NFP)", "beklenti": "180K", "etki": "YÜKSEK 🚨"},
        {"tarih": "3 Gün Sonra, 15:30", "veri": "ABD TÜFE Verisi", "beklenti": "%2.9", "etki": "KRİTİK 🩸"},
        {"tarih": "Gelecek Hafta", "veri": "FOMC Faiz Karar Açıklaması", "beklenti": "Sabit (%5.25)", "etki": "YÜKSEK 🚨"}
    ])

@app.get("/api/notlar")
async def api_notlar_get(): return JSONResponse(content=trade_notlari)

@app.post("/api/notlar")
async def api_notlar_post(req: NotRequest):
    trade_notlari.append({"not": req.not_icerigi, "zaman": datetime.datetime.now().strftime("%d.%m.%Y - %H:%M")})
    veritabani_kaydet()
    return JSONResponse(content={"durum": "basarili"})

# ==========================================
# 4. GERÇEK ZAMANLI LLM KONSEY MOTORU (GROQ)
# ==========================================
async def groq_ajani_cagir(client: httpx.AsyncClient, sistem_rolu: str, model_adi: str, kullanici_sorusu: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    veri = {
        "model": model_adi,
        "messages": [{"role": "system", "content": sistem_rolu}, {"role": "user", "content": kullanici_sorusu}],
        "temperature": 0.7, "max_tokens": 800
    }
    try:
        response = await client.post(url, headers=headers, json=veri, timeout=20.0)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as ex:
        return f"[{model_adi} İşlem Hatası: {str(ex)}]"

async def uclu_ai_birlesik_yanit(mesaj: str):
    btc_fiyat = gercek_piyasa_verisi_cek()["fiyat"]
    if not GROQ_API_KEY:
        return f"👑 **Q-AI Kurumsal Bilgilendirme:** API anahtarı eksik. Bitcoin (BTC): **${btc_fiyat:,.2f}**"
    async with httpx.AsyncClient() as client:
        r1, r2, r3 = "Sen teknik analistisin.", "Sen piyasa araştırmacısısın.", "Sen risk yöneticisisin."
        g1 = groq_ajani_cagir(client, r1, "llama-3.1-8b-instant", mesaj)
        g2 = groq_ajani_cagir(client, r2, "mixtral-8x7b-32768", mesaj)
        g3 = groq_ajani_cagir(client, r3, "gemma2-9b-it", mesaj)
        c1, c2, c3 = await asyncio.gather(g1, g2, g3)
        mudur_rol = f"Sen siberpunk tarzı Q-AI asistanısın. Patron'a hitap et. Şu analizleri birleştir:\nTeknik: {c1}\nPiyasa: {c2}\nRisk: {c3}"
        return await groq_ajani_cagir(client, mudur_rol, "llama-3.1-8b-instant", mesaj)

# ==========================================
# 5. HABERLER VE ÇEVİRİ
# ==========================================
def cevir_ingilizce_turkce(metin):
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=tr&dt=t&q={urllib.parse.quote(metin)}"
        response = requests.get(url, timeout=3)
        return "".join([x[0] for x in response.json()[0]])
    except:
        return metin 

def son_dakika_haberlerini_cek():
    now = time.time()
    if now - haberler_cache["last_update"] < 60 and haberler_cache["data"]:
        return haberler_cache["data"]
    try:
        url = "https://api.rss2json.com/v1/api.json?rss_url=https://cointelegraph.com/rss"
        response = requests.get(url, timeout=10)
        data = response.json()
        haberler = []
        for item in data['items'][:12]:
            t_baslik = cevir_ingilizce_turkce(item['title'])
            t_ozet = cevir_ingilizce_turkce(re.sub('<[^<]+>', '', item['description'])[:250] + "...")
            haberler.append({"baslik": t_baslik, "ozet": t_ozet, "kaynak": "CoinTelegraph", "url": item['link'], "zaman": item['pubDate'][11:16], "onem": "ÖNEMLİ ⚠️", "onem_renk": "#F59E0B", "yon": "CANLI 🟢", "kaldirac": "Genel Akış", "ai_yorum": "Analiz güncel."})
        haberler_cache["data"] = haberler
        haberler_cache["last_update"] = now
        return haberler
    except:
        return [{"baslik": "Haberler güncelleniyor...", "ozet": "Bağlantı bekleniyor.", "kaynak": "Sistem", "url": "#", "zaman": "Şimdi", "onem": "BEKLEYİN", "onem_renk": "#6B7280", "yon": "YÜKLENİYOR", "kaldirac": "-", "ai_yorum": "-"}]

# ==========================================
# 6. API UÇ NOKTALARI
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
async def api_sohbet(req: ChatRequest): return JSONResponse(content={"yanit": await uclu_ai_birlesik_yanit(req.mesaj)})

@app.get("/api/cuzdan/spot")
async def api_cuzdan_spot_get(): return JSONResponse(content=spot_varliklar)

@app.post("/api/cuzdan/spot")
async def api_cuzdan_spot_post(req: SpotVarlikRequest):
    spot_varliklar.append({"borsa": req.borsa, "bakiye": req.bakiye, "detay": req.detay or "Detay yok"})
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
    aktif_pozisyonlar.append({"coin": req.coin.upper(), "kaldirac": req.kaldirac, "yon": req.yon, "miktar": req.miktar, "zaman": datetime.datetime.now().strftime("%H:%M")})
    veritabani_kaydet()
    return JSONResponse(content={"durum": "basarili"})

@app.delete("/api/cuzdan/vadeli/{index}")
async def api_cuzdan_vadeli_delete(index: int):
    if 0 <= index < len(aktif_pozisyonlar):
        aktif_pozisyonlar.pop(index)
        veritabani_kaydet()
    return JSONResponse(content={"durum": "silindi"})

# --- SPOTIFY ---
@app.get("/spotify/giris")
async def spotify_giris(): return RedirectResponse(url=sp_oauth.get_authorize_url())

@app.get("/callback")
async def spotify_callback(request: Request, code: str):
    try:
        spotify_tokens[request.client.host] = sp_oauth.get_access_token(code)['access_token']
    except:
        pass
    return RedirectResponse(url="/muzik?spotify=baglandi", status_code=303)

@app.get("/api/spotify/kendi_listelerim")
async def api_spotify_listeler(request: Request):
    token = spotify_tokens.get(request.client.host)
    if not token: return JSONResponse(content={"durum": "hata", "mesaj": "Bağlantı yok"})
    try:
        sp = spotipy.Spotify(auth=token)
        listeler = [{"id": i['id'], "isim": i['name']} for i in sp.current_user_playlists(limit=6)['items']]
        return JSONResponse(content={"durum": "basarili", "listeler": listeler})
    except Exception as e:
        return JSONResponse(content={"durum": "hata", "mesaj": str(e)})

# ==========================================
# 7. SAYFA YÖNLENDİRMELERİ
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def splash_ekrani(request: Request):
    onayli_kullanicilar.discard(request.client.host)
    return templates.TemplateResponse(request=request, name="splash.html", context={"request": request})

@app.get("/disclaimer", response_class=HTMLResponse)
async def yasal_uyari(request: Request):
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
async def piyasa(request: Request):
    if not yetki_kontrol(request): return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="piyasa.html", context={"request": request})

@app.get("/haberler", response_class=HTMLResponse)
async def haberler(request: Request):
    if not yetki_kontrol(request): return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="haberler.html", context={"request": request})

@app.get("/sinyaller", response_class=HTMLResponse)
async def sinyaller(request: Request):
    if not yetki_kontrol(request): return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="sinyaller.html", context={"request": request})

@app.get("/top5", response_class=HTMLResponse)
async def top5(request: Request):
    if not yetki_kontrol(request): return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="top5.html", context={"request": request})

@app.get("/isiharitasi", response_class=HTMLResponse)
async def isiharitasi(request: Request):
    if not yetki_kontrol(request): return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="isiharitasi.html", context={"request": request})

@app.get("/cuzdan", response_class=HTMLResponse)
async def cuzdan(request: Request):
    if not yetki_kontrol(request): return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="cuzdan.html", context={"request": request})

@app.get("/sohbet", response_class=HTMLResponse)
async def sohbet(request: Request):
    if not yetki_kontrol(request): return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="sohbet.html", context={"request": request})

@app.get("/muzik", response_class=HTMLResponse)
async def muzik(request: Request):
    if not yetki_kontrol(request): return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="muzik.html", context={"request": request})

@app.get("/{sayfa_adi}", response_class=HTMLResponse)
async def sayfa_yonlendir(request: Request, sayfa_adi: str):
    if not yetki_kontrol(request): return RedirectResponse(url="/", status_code=303)
    try:
        return templates.TemplateResponse(request=request, name=f"{sayfa_adi}.html", context={"request": request})
    except:
        return templates.TemplateResponse(request=request, name="yapim_asamasinda.html", context={"request": request, "sayfa": sayfa_adi.upper()})

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)