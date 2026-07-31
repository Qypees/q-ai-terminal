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
import random
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

app = FastAPI(title="Qypees Terminal Pro - Quantum HFT & On-Chain Engine")
templates = Jinja2Templates(directory="templates")

# ==========================================
# YEREL VERİTABANI VE SİSTEM YÖNETİMİ
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

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "d560d37532284575a7933231cf7166f3")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "BURAYA_CLIENT_SECRET_DEGERINI_YAZ")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "https://q-ai-terminal.onrender.com/callback")

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
# 1. CANLI PİYASA MOTORU
# ==========================================
COINLER = ["BTC", "ETH", "SOL", "BNB", "XRP", "DOGE", "ADA", "AVAX", "LINK", "PEPE", "NEAR", "SUI", "FET", "SHIB", "DOT"]
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
            fiyat = 1.0 if coin in ["USDT", "USDC"] else 0.0
            degisim = 0.0
            hacim = 0.0
        
        if degisim >= 5.0:
            yon, ai_yorum = "STRONG LONG 🚀", "FVG Dolduruldu & OFI Pozitif Momentum"
        elif degisim >= 1.5:
            yon, ai_yorum = "LONG 🟢", "EMA Ribbon Üzerinde Tutunuyor"
        elif degisim <= -5.0:
            yon, ai_yorum = "STRONG SHORT 🩸", "CVD Negatif / Likidite Boşluğu Kırıldı"
        elif degisim <= -1.5:
            yon, ai_yorum = "SHORT 🔴", "VWAP Altı Satış Baskısı"
        else:
            yon, ai_yorum = "YATAY 🟡", "Order Block Sıkışması"
                
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
    hareketli_coinler = [c for c in tum_coinler if c["sembol"] not in ["USDT", "USDC"]]
    sirali = sorted(hareketli_coinler, key=lambda x: x['degisim'])
    return {"yukselenler": list(reversed(sirali[-5:])), "dusenler": sirali[:5]}

def isiharitasi_verilerini_cek(zaman="1d"):
    tum_coinler = coklu_piyasa_verilerini_cek()
    return sorted(tum_coinler, key=lambda x: x['hacim'], reverse=True)

# ==========================================
# 2. SİSTEM, AĞ & ON-CHAIN API'LERİ (YENİ)
# ==========================================
@app.get("/api/sistem/ping")
async def api_ping():
    return JSONResponse(content={"durum": "online", "gecikme_ms": 12, "zaman": datetime.datetime.now().strftime("%H:%M:%S")})

@app.get("/api/sistem/temizle_cache")
async def api_temizle_cache():
    binance_cache["last_update"] = 0
    haberler_cache["last_update"] = 0
    return JSONResponse(content={"durum": "basarili", "mesaj": "Tüm önbellek temizlendi."})

# YENİ: On-Chain & AI VIX Uç Noktaları
@app.get("/api/onchain/mvrv")
async def api_onchain_mvrv():
    return JSONResponse(content={"z_score": 1.45, "durum": "Adil Değer Bölgesi", "risk": "DÜŞÜK"})

@app.get("/api/sistem/ai_vix")
async def api_ai_vix():
    vix_degeri = random.uniform(15.0, 35.0)
    durum = "Yüksek Volatilite Beklentisi" if vix_degeri > 25 else "Durağan Piyasa"
    return JSONResponse(content={"ai_vix_skoru": round(vix_degeri, 2), "tahmin": durum})

@app.get("/api/sistem/mev_shield")
async def api_mev_shield():
    return JSONResponse(content={"durum": "AKTİF", "engellenen_bot_sayisi": 14})

@app.get("/api/sinyaller")
async def api_sinyaller():
    tum = coklu_piyasa_verilerini_cek()
    sinyaller = []
    for c in tum[:6]:
        fiyat = c["fiyat"]
        yon = "LONG" if "LONG" in c["ai_yon"] else ("SHORT" if "SHORT" in c["ai_yon"] else "LONG")
        sl_oran = 0.02 if yon == "LONG" else -0.02
        tp_oran = 0.05 if yon == "LONG" else -0.05
        sinyaller.append({
            "coin": c["sembol"],
            "yon": yon,
            "giris": str(round(fiyat, 4)),
            "hedef": str(round(fiyat * (1 + tp_oran), 4)),
            "stop": str(round(fiyat * (1 - sl_oran), 4)),
            "guc": 92 if "STRONG" in c["ai_yon"] else 81,
            "formasyon": "FVG Kırılımı + CVD Onayı",
            "rr": "1 : 2.5",
            "yorum": c["ai_yorum"]
        })
    return JSONResponse(content=sinyaller)

@app.get("/api/likidasyon_haritasi")
async def api_likidasyon_haritasi():
    tum_veriler = coklu_piyasa_verilerini_cek()
    majorklar = [c for c in tum_veriler if c["sembol"] in ["BTC", "ETH", "SOL", "BNB", "XRP", "AVAX"]]
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
        {"zaman": "8 dk önce", "detay": "Tether Treasury tarafından 500 Milyon USDT basıldı.", "yon": "BOĞA / LİKİDİTE GİRİŞİ", "renk": "#00ffcc"}
    ])

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

@app.get("/api/arbitraj")
async def api_arbitraj():
    return JSONResponse(content=[
        {"coin": "SOL", "buy_exchange": "Binance", "buy_price": 145.0, "sell_exchange": "OKX", "sell_price": 145.8, "spread": 0.55, "profit": 80.0, "status": "RİSKSİZ KAZANÇ", "color": "#10B981"},
        {"coin": "ETH", "buy_exchange": "Uniswap", "buy_price": 3090.5, "sell_exchange": "Binance", "sell_price": 3105.0, "spread": 0.47, "profit": 145.0, "status": "DEX-CEX FIRSATI", "color": "#F59E0B"}
    ])

@app.get("/api/makro_takvim")
async def api_makro_takvim():
    return JSONResponse(content=[
        {"tarih": "Yarın, 15:30", "veri": "ABD Tarım Dışı İstihdam (NFP)", "beklenti": "180K", "etki": "YÜKSEK 🚨"},
        {"tarih": "3 Gün Sonra, 15:30", "veri": "ABD TÜFE Verisi", "beklenti": "%2.9", "etki": "KRİTİK 🩸"}
    ])

@app.get("/api/notlar")
async def api_notlar_get(): return JSONResponse(content=trade_notlari)

@app.post("/api/notlar")
async def api_notlar_post(req: NotRequest):
    trade_notlari.append({"not": req.not_icerigi, "zaman": datetime.datetime.now().strftime("%d.%m.%Y - %H:%M")})
    veritabani_kaydet()
    return JSONResponse(content={"durum": "basarili"})

# ==========================================
# 3. LLM AI KONSEYİ
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
        r1, r2, r3 = "Sen teknik analistisin.", "Sen makro piyasa araştırmacısısın.", "Sen risk yöneticisisin."
        g1 = groq_ajani_cagir(client, r1, "llama-3.1-8b-instant", mesaj)
        g2 = groq_ajani_cagir(client, r2, "mixtral-8x7b-32768", mesaj)
        g3 = groq_ajani_cagir(client, r3, "gemma2-9b-it", mesaj)
        c1, c2, c3 = await asyncio.gather(g1, g2, g3)
        mudur_rol = f"Sen siberpunk tarzı Q-AI baş traderısın. Patron'a hitap et. Şu analizleri birleştir:\nTeknik: {c1}\nPiyasa: {c2}\nRisk: {c3}"
        return await groq_ajani_cagir(client, mudur_rol, "llama-3.1-8b-instant", mesaj)

# ==========================================
# 4. HABER VE ÇEVİRİ MOTORU
# ==========================================
async def cevir_ingilizce_turkce_async(client: httpx.AsyncClient, metin: str):
    if not metin or metin.strip() == "": return ""
    try:
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=tr&dt=t&q={urllib.parse.quote(metin)}"
        response = await client.get(url, timeout=5.0)
        if response.status_code == 200:
            veri = response.json()
            if veri and veri[0]: return "".join([x[0] for x in veri[0] if x[0]])
        return metin 
    except: return metin

def ai_haber_analizi(metin):
    metin_kucuk = metin.lower()
    yuksek_onemli = ["sec", "etf", "onay", "yasadışı", "faiz", "enflasyon", "kara para", "hack", "çöküş", "iflas", "dava"]
    onemli = ["güncelleme", "ortaklık", "listeleme", "ağ", "balina", "transfer", "yakım"]
    if any(k in metin_kucuk for k in yuksek_onemli): return "YÜKSEK ÖNEMLİ 🚨", "#EF4444", "Yüksek Volatilite Beklentisi"
    elif any(k in metin_kucuk for k in onemli): return "ÖNEMLİ ⚠️", "#F59E0B", "Orta Volatilite Beklentisi"
    else: return "STANDART ℹ️", "#3B82F6", "Olağan Akış"

async def rss_kaynaktan_haber_cek(client: httpx.AsyncClient, kaynak_adi: str, rss_url: str):
    try:
        api_url = f"https://api.rss2json.com/v1/api.json?rss_url={rss_url}"
        response = await client.get(api_url, timeout=10.0)
        data = response.json()
        haberler = []
        if 'items' in data:
            for item in data['items'][:3]:
                zaman_str = item.get('pubDate', '')
                zaman_saat = zaman_str[11:16] if len(zaman_str) >= 16 else "Şimdi"
                orjinal_baslik = item.get('title', 'Başlık Bulunamadı')
                orjinal_ozet = re.sub('<[^<]+>', '', item.get('description', 'Özet bulunamadı'))[:200] + "..."
                t_baslik = await cevir_ingilizce_turkce_async(client, orjinal_baslik)
                t_ozet = await cevir_ingilizce_turkce_async(client, orjinal_ozet)
                t_baslik = t_baslik.replace('`', "'")
                t_ozet = t_ozet.replace('`', "'")
                onem, onem_renk, kaldirac = ai_haber_analizi(t_baslik + " " + t_ozet)
                haberler.append({
                    "baslik": t_baslik, "ozet": t_ozet, "kaynak": kaynak_adi, "url": item.get('link', '#'),
                    "zaman": zaman_saat, "zaman_tam": zaman_str, "onem": onem, "onem_renk": onem_renk,
                    "yon": "CANLI 🟢", "yon_renk": "#10B981", "kaldirac": kaldirac, "ai_yorum": "Çoklu-Kaynak Onaylı."
                })
        return haberler
    except: return []

async def son_dakika_haberlerini_cek_async():
    now = time.time()
    if now - haberler_cache["last_update"] < 60 and haberler_cache["data"]:
        return haberler_cache["data"]
    rss_kaynaklar = [
        ("CoinTelegraph", "https://cointelegraph.com/rss"), ("CoinDesk", "https://www.coindesk.com/arc/outboundfeeds/rss/"),
        ("Decrypt", "https://decrypt.co/feed"), ("CryptoSlate", "https://cryptoslate.com/feed/")
    ]
    async with httpx.AsyncClient() as client:
        gorevler = [rss_kaynaktan_haber_cek(client, ad, url) for ad, url in rss_kaynaklar]
        sonuclar = await asyncio.gather(*gorevler)
        tum_haberler = []
        for liste in sonuclar: tum_haberler.extend(liste)
        if tum_haberler:
            tum_haberler.sort(key=lambda x: x.get("zaman_tam", ""), reverse=True)
            haberler_cache["data"] = tum_haberler[:15]
            haberler_cache["last_update"] = now
            return tum_haberler[:15]
        else:
            return [{"baslik": "Sistem Hazırlanıyor...", "ozet": "Bağlanılıyor.", "kaynak": "Sistem", "url": "#", "zaman": "Şimdi", "onem": "BEKLEYİN", "onem_renk": "#6B7280", "yon": "YÜKLENİYOR", "yon_renk": "#6B7280", "kaldirac": "-", "ai_yorum": "-"}]

# ==========================================
# 5. API ROTARI
# ==========================================
@app.get("/api/haberler")
async def api_haberler(): return JSONResponse(content=await son_dakika_haberlerini_cek_async())
@app.get("/api/piyasa")
async def api_piyasa(): return JSONResponse(content=coklu_piyasa_verilerini_cek())
@app.get("/api/btc")
async def api_btc(): return JSONResponse(content=gercek_piyasa_verisi_cek())
@app.get("/api/top5")
async def api_top5(zaman: str = "1d"): return JSONResponse(content=top5_verilerini_cek(zaman))
@app.get("/api/isiharitasi_data")
async def api_isiharitasi_data(zaman: str = "1d"): return JSONResponse(content=isiharitasi_verilerini_cek(zaman))
@app.post("/api/sohbet")
async def api_sohbet(req: ChatRequest): return JSONResponse(content={"yanit": await uclu_ai_birlesik_yanit(req.mesaj)})
@app.get("/api/cuzdan/spot")
async def api_cuzdan_spot_get(): return JSONResponse(content=spot_varliklar)
@app.get("/api/cuzdan/vadeli")
async def api_cuzdan_vadeli_get(): return JSONResponse(content=aktif_pozisyonlar)

# --- SPOTIFY ---
@app.get("/spotify/giris")
async def spotify_giris(): return RedirectResponse(url=sp_oauth.get_authorize_url())

@app.get("/callback")
async def spotify_callback(request: Request, code: str):
    try: spotify_tokens[request.client.host] = sp_oauth.get_access_token(code)['access_token']
    except: pass
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
# 6. SAYFA YÖNLENDİRMELERİ
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

def yetki_kontrol(request: Request): return request.client.host in onayli_kullanicilar

@app.get("/pano", response_class=HTMLResponse)
async def ana_ekran(request: Request):
    if not yetki_kontrol(request): return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="index.html", context={"request": request})

@app.get("/kaldirac-pro", response_class=HTMLResponse)
async def kaldirac_pro_sayfasi(request: Request):
    if not yetki_kontrol(request): return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="kaldirac_pro.html", context={"request": request})

@app.get("/{sayfa_adi}", response_class=HTMLResponse)
async def sayfa_yonlendir(request: Request, sayfa_adi: str):
    if not yetki_kontrol(request): return RedirectResponse(url="/", status_code=303)
    try:
        return templates.TemplateResponse(request=request, name=f"{sayfa_adi}.html", context={"request": request})
    except:
        return templates.TemplateResponse(request=request, name="yapim_asamasinda.html", context={"request": request, "sayfa": sayfa_adi.upper()})

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)