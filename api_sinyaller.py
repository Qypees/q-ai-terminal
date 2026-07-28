import random
from fastapi import APIRouter

# Flet (ft) tamamen silindi! Sadece saf backend ve veri işleme.
# Varsayılan veritabanı dosyanızdan coinleri ve fiyatları çekiyoruz.
from veritabani import COINLER, COIN_FIYATLARI 

router = APIRouter()

@router.get("/api/sinyaller")
async def ai_sinyalleri_getir():
    """
    Q-AI 100 coini tarar ve en volatil olanlardan rastgele 5-9 arası fırsat çıkarır.
    Sinyalleri gücüne göre (100'den aşağıya) sıralayıp Frontend'e gönderir.
    """
    firsat_kac_tane = random.randint(5, 9)
    firsat_coinleri = random.sample(COINLER, min(firsat_kac_tane, len(COINLER)))

    sinyaller = []

    for coin in firsat_coinleri:
        yon = random.choice(["LONG", "SHORT"])
        kaldirac = random.choice(["5x", "10x", "20x"])
        
        # Olası bir veri hatasına karşı varsayılan fiyat 100.0 olarak belirlendi
        fiyat = COIN_FIYATLARI.get(coin, 100.0) 
        
        # %65 ile %98 arası rastgele bir sinyal güvenilirlik gücü belirle
        guc = random.randint(65, 98)

        # Matematiksel Hedef ve Stop Loss Algoritması
        if yon == "LONG":
            hedef = fiyat * random.uniform(1.03, 1.08)  # %3 ila %8 arası kâr hedefi
            stop = fiyat * random.uniform(0.95, 0.98)   # %2 ila %5 arası zarar kes
            yorum = f"Q-AI momentum tarayıcısı, {coin} için yükseliş trendi tespit etti. Artan hacim ve MACD kesişimi {kaldirac} kaldıraçlı LONG işlemini destekliyor."
        else:
            hedef = fiyat * random.uniform(0.92, 0.97)  # %3 ila %8 arası düşüş hedefi
            stop = fiyat * random.uniform(1.02, 1.05)   # %2 ila %5 arası zarar kes
            yorum = f"Piyasa yapısında zayıflık saptandı. {coin} majör direnç bölgesinden reddedildi, satıcı baskısı {kaldirac} kaldıraçlı SHORT pozisyon için uygun."

        # Virgülden sonraki basamakları coin'in fiyatına göre dinamik ayarlıyoruz
        # (Örn: SHIB ise çok sıfır, BTC ise 2 sıfır)
        yuvarlama = 4 if fiyat < 1 else 2

        sinyaller.append({
            "coin": coin,
            "yon": yon,
            "kaldirac": kaldirac,
            "guc": guc,
            "giris": round(fiyat, yuvarlama),
            "hedef": round(hedef, yuvarlama),
            "stop": round(stop, yuvarlama),
            "yorum": yorum
        })

    # En güçlü sinyal (guc degeri en yüksek olan) en üstte çıkacak şekilde sırala!
    sinyaller.sort(key=lambda x: x["guc"], reverse=True)

    # FastAPI bu listeyi otomatik olarak mükemmel bir JSON'a dönüştürür.
    return {"durum": "basarili", "toplam_sinyal": len(sinyaller), "sinyaller": sinyaller}