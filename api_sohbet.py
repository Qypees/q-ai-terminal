import os
import asyncio
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

# Güvenli Şifre Yüklemesi
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

# FastAPI Yönlendirici (Router)
router = APIRouter()

# Frontend'den Gelecek Veri Modeli
class MesajIstegi(BaseModel):
    mesaj: str

# Asenkron Groq API İstek Fonksiyonu (Eski yavaş urllib yerine süper hızlı httpx)
async def groq_ajani_cagir(client: httpx.AsyncClient, sistem_rolu: str, model_adi: str, kullanici_sorusu: str) -> str:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    veri = {
        "model": model_adi,
        "messages": [
            {"role": "system", "content": sistem_rolu},
            {"role": "user", "content": kullanici_sorusu}
        ],
        "temperature": 0.7,
        "max_tokens": 800
    }
    
    try:
        response = await client.post(url, headers=headers, json=veri, timeout=20.0)
        response.raise_for_status()
        data = response.json()
        return data['choices'][0]['message']['content']
    except Exception as ex:
        return f"[{model_adi} İşlem Hatası: {str(ex)}]"


# HTML'den Gelen Fetch('/api/sohbet') İsteğini Karşılayan Uç Nokta
@router.post("/api/sohbet")
async def ai_sohbet_api(istek: MesajIstegi):
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="Kritik Hata: GROQ API Key bulunamadı.")
        
    kullanici_mesaji = istek.mesaj
    
    # httpx.AsyncClient ile bağlantı havuzunu açık tutarak hızı katlıyoruz
    async with httpx.AsyncClient() as client:
        
        # 1. Aşama: 3 Alt Ajanın Rolleri ve Modelleri
        rol_teknik = "Sen bir kripto teknik analistisin. Sadece fiyata, destek-direnç noktalarına ve formasyonlara odaklan. Çok kısa özet geç."
        model_teknik = "llama-3.1-8b-instant"

        rol_duygu = "Sen bir kripto piyasa araştırmacısısın. Hacimlere, piyasa duyarlılığına, balina hareketlerine ve genel trende odaklan. Kısa özet geç."
        model_duygu = "mixtral-8x7b-32768"

        rol_risk = "Sen bir kripto risk yöneticisisin. Sadece potansiyel düşüş senaryolarına, stop-loss seviyelerine ve risklere odaklan. Kısa özet geç."
        model_risk = "gemma2-9b-it"
        
        # 3 Ajanı Asenkron olarak AYNI ANDA (Paralel) çalıştırıyoruz!
        # Eskiden biri bitmeden diğeri başlamıyordu veya thread karmaşası oluyordu.
        gorevler = [
            groq_ajani_cagir(client, rol_teknik, model_teknik, kullanici_mesaji),
            groq_ajani_cagir(client, rol_duygu, model_duygu, kullanici_mesaji),
            groq_ajani_cagir(client, rol_risk, model_risk, kullanici_mesaji)
        ]
        
        sonuclar = await asyncio.gather(*gorevler)
        cevap_teknik, cevap_duygu, cevap_risk = sonuclar
        
        # 2. Aşama: Ana Beyin (Müdür / Q-AI)
        rol_mudur = (
            "Sen siberpunk tarzı, zeki bir kripto asistanısın (Adın Q-AI). Kullanıcıya her zaman 'Patron' diye hitap et. "
            "Arka plandaki 3 ajanının sana sunduğu aşağıdaki analizleri oku ve bunları birleştirerek "
            "kullanıcıya tek, akıcı, kendinden emin ve havalı bir nihai rapor yaz. "
            "Asla 'Uzmanlar böyle diyor' veya 'Ajanlarım böyle dedi' deme. Analizleri doğrudan sen yapmışsın gibi konuş. "
            "Önemli kısımları **kalın** yazarak Markdown formatında şık bir çıktı ver. Çok uzatma, net ve vurucu ol.\n\n"
            f"--- TEKNİK İSTİHBARAT ---\n{cevap_teknik}\n\n"
            f"--- PİYASA DUYARLILIĞI ---\n{cevap_duygu}\n\n"
            f"--- RİSK PROTOKOLÜ ---\n{cevap_risk}"
        )
        
        nihai_cevap = await groq_ajani_cagir(client, rol_mudur, "llama-3.1-8b-instant", kullanici_mesaji)
        
    # Frontend'deki sohbet.html'e veriyi JSON formatında geri döndür
    return {"yanit": nihai_cevap}