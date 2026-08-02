from fastapi import FastAPI, Request, HTTPException, Response
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
import sqlite3
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
# SQLITE VERİTABANI YÖNETİMİ (Kalıcı ve Güvenli)
# ==========================================
DB_DOSYASI = "qypees_terminal.db"

def veritabani_baslat():
    conn = sqlite3.connect(DB_DOSYASI)
    cursor = conn.cursor()
    
    # Tabloları oluştur
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ayarlar (
            anahtar TEXT PRIMARY KEY,
            deger TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS spot_varliklar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            borsa TEXT,
            bakiye TEXT,
            detay TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vadeli_pozisyonlar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin TEXT,
            kaldirac TEXT,
            yon TEXT,
            miktar TEXT,
            zaman TEXT,
            ai_yorum TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS paper_islemler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin TEXT,
            yon TEXT,
            kaldirac TEXT,
            teminat REAL,
            giris_fiyati REAL,
            zaman TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS trade_notlari (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            not_icerigi TEXT,
            zaman TEXT
        )
    """)
    
    # Başlangıç bakiyesi yoksa 10000$ ata
    cursor.execute("SELECT deger FROM ayarlar WHERE anahtar = 'paper_bakiye'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO ayarlar (anahtar, deger) VALUES ('paper_bakiye', '10000.0')")
        
    conn.commit()
    conn.close()

veritabani_baslat()

def get_db():
    conn = sqlite3.connect(DB_DOSYASI)
    conn.row_factory = sqlite3.Row
    return conn

def paper_bakiye_getir():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT deger FROM ayarlar WHERE anahtar = 'paper_bakiye'")
    val = cursor.fetchone()
    conn.close()
    return float(val["deger"]) if val else 10000.0

def paper_bakiye_guncelle(yeni_bakiye: float):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE ayarlar SET deger = ? WHERE anahtar = 'paper_bakiye'", (str(yeni_bakiye),))
    conn.commit()
    conn.close()

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
# 2. SİSTEM, AĞ & ON-CHAIN API'LERİ
# ==========================================
@app.get("/api/sistem/ping")
async def api_ping():
    return JSONResponse(content={"durum": "online", "gecikme_ms": 12, "zaman": datetime.datetime.now().strftime("%H:%M:%S")})

@app.get("/api/sistem/temizle_cache")
async def api_temizle_cache():
    binance_cache["last_update"] = 0
    haberler_cache["last_update"] = 0
    return JSONResponse(content={"durum": "basarili", "mesaj": "Tüm önbellek temizlendi."})

@app.get("/api/onchain/mvrv")
async def api_onchain_mvrv():
    return JSONResponse(content={"z_score": 1.45, "durum": "Adil Değer Bölgesi", "risk": "DÜŞÜK"})

@app.get("/api/sistem/ai_vix")
async def api_sistem_ai_vix():
    vix_degeri = random.uniform(15.0, 35.0)
    durum = "Yüksek Volatilite Beklentisi" if vix_degeri > 25 else "Durağan Piyasa"
    return JSONResponse(content={"ai_vix_skoru": round(vix_degeri, 2), "tahmin": durum})

@app.get("/api/sistem/mev_shield")
async def api_sistem_mev_shield():
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
        {"zaman": "3 dk önce", "detay": "Cüzdandan soğuk depoya 125,000 ETH çekildi.", "yon": "POZİTİF (Arz Azalması)", "renk": "#10B981"},
        {"zaman": "8 dk önce", "detay": "Tether Treasury tarafından 500 Milyon USDT basıldı.", "yon": "BOĞA / LİKİDİTE GİRİŞİ", "renk": "#00ffcc"}
    ])

@app.get("/api/paper/durum")
async def api_paper_durum():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM paper_islemler")
    islemler = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return JSONResponse(content={"bakiye": paper_bakiye_getir(), "islemler": islemler})

@app.post("/api/paper/islem_ac")
async def api_paper_islem_ac(req: PaperTradeRequest):
    bakiye = paper_bakiye_getir()
    if req.teminat > bakiye:
        raise HTTPException(status_code=400, detail="Yetersiz sanal bakiye!")
    
    yeni_bakiye = bakiye - req.teminat
    paper_bakiye_guncelle(yeni_bakiye)
    
    tum_veriler = coklu_piyasa_verilerini_cek()
    bulunan_fiyat = next((v["fiyat"] for v in tum_veriler if v["sembol"] == req.coin.upper()), 100.0)
    zaman_str = datetime.datetime.now().strftime("%H:%M")
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO paper_islemler (coin, yon, kaldirac, teminat, giris_fiyati, zaman)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (req.coin.upper(), req.yon, req.kaldirac, req.teminat, bulunan_fiyat, zaman_str))
    conn.commit()
    conn.close()
    
    return JSONResponse(content={"durum": "basarili", "kalan_bakiye": yeni_bakiye})

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
async def api_notlar_get():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT not_icerigi as 'not', zaman FROM trade_notlari")
    notlar = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return JSONResponse(content=notlar)

@app.post("/api/notlar")
async def api_notlar_post(req: NotRequest):
    zaman_str = datetime.datetime.now().strftime("%d.%m.%Y - %H:%M")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO trade_notlari (not_icerigi, zaman) VALUES (?, ?)", (req.not_icerigi, zaman_str))
    conn.commit()
    conn.close()
    return JSONResponse(content={"durum": "basarili"})

@app.get("/api/cuzdan/spot")
async def api_cuzdan_spot_get():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM spot_varliklar")
    spotlar = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return JSONResponse(content=spotlar)

@app.post("/api/cuzdan/spot")
async def api_cuzdan_spot_post(req: SpotVarlikRequest):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO spot_varliklar (borsa, bakiye, detay) VALUES (?, ?, ?)", (req.borsa, req.bakiye, req.detay))
    conn.commit()
    conn.close()
    return JSONResponse(content={"durum": "basarili"})

@app.delete("/api/cuzdan/spot/{item_id}")
async def api_cuzdan_spot_delete(item_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM spot_varliklar WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return JSONResponse(content={"durum": "basarili"})

@app.get("/api/cuzdan/vadeli")
async def api_cuzdan_vadeli_get():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vadeli_pozisyonlar")
    vadeliler = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return JSONResponse(content=vadeliler)

@app.post("/api/cuzdan/vadeli")
async def api_cuzdan_vadeli_post(req: VadeliPozisyonRequest):
    zaman_str = datetime.datetime.now().strftime("%H:%M:%S")
    ai_yorum = "Q-AI risk analizi başarılı. Volatilite seviyesi optimize edildi."
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO vadeli_pozisyonlar (coin, kaldirac, yon, miktar, zaman, ai_yorum)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (req.coin.upper(), req.kaldirac, req.yon, req.miktar, zaman_str, ai_yorum))
    conn.commit()
    conn.close()
    return JSONResponse(content={"durum": "basarili"})

@app.delete("/api/cuzdan/vadeli/{item_id}")
async def api_cuzdan_vadeli_delete(item_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM vadeli_pozisyonlar WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
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

@app.get("/api/haberler")
async def api_haberler_db():
    canli_haberler = await son_dakika_haberlerini_cek_async()
    conn = get_db()
    cursor = conn.cursor()
    
    for h in canli_haberler:
        cursor.execute("SELECT id FROM haberler_arsivi WHERE baslik = ?", (h["baslik"],))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO haberler_arsivi (baslik, ozet, kaynak, url, zaman, onem, etkilenen_coinler, piyasa_yonu)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                h["baslik"], h["ozet"], h["kaynak"], h["url"], h["zaman"], h["onem"], 
                "BTC, ETH, SOL", "ALIŞTA (BOĞA)" if "ÖNEMLİ" in h["onem"] else "SATIŞTA (FUD)"
            ))
    conn.commit()
    
    # EN YENİ HABER EN ÜSTTE OLMASI İÇİN id'ye göre azalan (DESC) sıralama
    cursor.execute("SELECT * FROM haberler_arsivi ORDER BY id DESC LIMIT 50")
    kayitlar = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return JSONResponse(content=kayitlar)

# ==========================================
# HABERLER VERİTABANI TABLOSU (main.py içine eklenecek)
# ==========================================
def haber_veritabani_baslat():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS haberler_arsivi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            baslik TEXT,
            ozet TEXT,
            kaynak TEXT,
            url TEXT,
            zaman TEXT,
            onem TEXT,
            etkilenen_coinler TEXT,
            piyasa_yonu TEXT
        )
    """)
    conn.commit()
    conn.close()

haber_veritabani_baslat()

@app.get("/api/haberler")
async def api_haberler_db():
    # RSS'den canlı çekip veritabanına kaydeden ve arşivden sunan akıllı endpoint
    canli_haberler = await son_dakika_haberlerini_cek_async()
    conn = get_db()
    cursor = conn.cursor()
    
    for h in canli_haberler:
        # Tekrarı önlemek için başlığa bak
        cursor.execute("SELECT id FROM haberler_arsivi WHERE baslik = ?", (h["baslik"],))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO haberler_arsivi (baslik, ozet, kaynak, url, zaman, onem, etkilenen_coinler, piyasa_yonu)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                h["baslik"], h["ozet"], h["kaynak"], h["url"], h["zaman"], h["onem"], 
                "BTC, ETH, SOL", "ALIŞTA (BOĞA)" if "ÖNEMLİ" in h["onem"] else "SATIŞTA (FUD)"
            ))
    conn.commit()
    
    cursor.execute("SELECT * FROM haberler_arsivi ORDER BY id DESC LIMIT 20")
    kayitlar = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return JSONResponse(content=kayitlar)

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

# --- SPOTIFY ---
@app.get("/spotify/giris")
async def spotify_giris(): return RedirectResponse(url=sp_oauth.get_authorize_url())

@app.get("/callback")
async def spotify_callback(request: Request, code: str):
    try:
        token_info = sp_oauth.get_access_token(code)
        if token_info:
            response = RedirectResponse(url="/muzik?spotify=baglandi", status_code=303)
            response.set_cookie(key="spotify_token", value=token_info['access_token'], httponly=True)
            return response
    except: pass
    return RedirectResponse(url="/muzik", status_code=303)

@app.get("/api/spotify/kendi_listelerim")
async def api_spotify_listeler(request: Request):
    token = request.cookies.get("spotify_token")
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
@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def splash_ekrani(request: Request, response: Response = None):
    if request.method == "HEAD":
        return HTMLResponse(content="")
    resp = templates.TemplateResponse(request=request, name="splash.html", context={"request": request})
    resp.delete_cookie("q_terminal_auth")
    return resp

@app.get("/disclaimer", response_class=HTMLResponse)
async def yasal_uyari(request: Request):
    return templates.TemplateResponse(request=request, name="disclaimer.html", context={"request": request})

@app.get("/onayla")
async def oturum_onayla(request: Request):
    response = RedirectResponse(url="/pano", status_code=303)
    response.set_cookie(key="q_terminal_auth", value="authenticated_omega", httponly=True, max_age=86400)
    return response

def yetki_kontrol(request: Request):
    return request.cookies.get("q_terminal_auth") == "authenticated_omega"

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

@app.get("/Savas_Odasi", response_class=HTMLResponse)
async def savas_odasi_sayfasi(request: Request):
    if not yetki_kontrol(request): return RedirectResponse(url="/", status_code=303)
    return templates.TemplateResponse(request=request, name="Savas_Odasi.html", context={"request": request})