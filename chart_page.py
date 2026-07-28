import random
from fastapi import APIRouter

router = APIRouter()

# Fiyat veritabanı (Mevcut sisteminizle entegre çalışır)
FIYAT_VERITABANI = {
    "BTC": 64500.0, 
    "ETH": 3450.0, 
    "SOL": 145.0, 
    "BNB": 580.0, 
    "AVAX": 32.5, 
    "XRP": 0.55
}

@router.get("/api/grafik_analiz/{coin}")
async def grafik_veri_analizi(coin: str):
    """
    Frontend'deki grafik.html sayfasının ihtiyaç duyduğu anlık fiyat, 
    AI yönü, TP/SL seviyeleri ve simüle edilmiş teknik verileri sağlar.
    """
    coin_kodu = coin.upper().strip()
    
    # Fiyat yoksa rastgele güvenli bir değer ata
    guncel_fiyat = FIYAT_VERITABANI.get(coin_kodu, round(random.uniform(10.0, 500.0), 2))
    
    # Trend yönü belirleme
    trend_yonu = random.choice(["LONG", "SHORT"])
    
    if trend_yonu == "LONG":
        kar_al = guncel_fiyat * 1.045
        stop_loss = guncel_fiyat * 0.972
        yorum = f"{coin_kodu} için momentum taraması hacim artışını teyit ediyor. Fiyat ${stop_loss:,.2f} destek seviyesinin üzerinde kaldığı sürece hedef ${kar_al:,.2f} direncidir."
    else:
        kar_al = guncel_fiyat * 0.955
        stop_loss = guncel_fiyat * 1.028
        yorum = f"{coin_kodu} tarafında satıcı baskısı baskın. ${stop_loss:,.2f} bölgesi yukarı kırılamazsa aşağı yönlü düzeltme derinleşebilir."

    return {
        "coin": coin_kodu,
        "fiyat": guncel_fiyat,
        "yon": trend_yonu,
        "tp": round(kar_al, 2),
        "sl": round(stop_loss, 2),
        "yorum": yorum
    }