<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Q-AI Terminal | Güvenli Bağlantı</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800;900&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #020203; color: white; overflow: hidden; margin: 0; }
        
        /* Arka Plan Matrix Tarzı Akan Kod Efekti */
        .matrix-bg {
            background: radial-gradient(circle at center, #0a192f 0%, #020203 100%);
            position: relative;
        }
        
        /* Neon Titreşim Animasyonu */
        .cyber-glow {
            text-shadow: 0 0 20px rgba(0,255,204,0.6), 0 0 40px rgba(0,255,204,0.2);
            animation: glitch 3s infinite;
        }

        @keyframes glitch {
            0%, 100% { opacity: 1; transform: translate(0); }
            31% { transform: translate(-2px, 2px); }
            32% { transform: translate(2px, -2px); }
            33% { transform: translate(0); }
        }

        .pulse-btn {
            background: linear-gradient(135deg, #00ffcc 0%, #00b399 100%);
            box-shadow: 0 0 30px rgba(0,255,204,0.4);
            transition: all 0.3s ease;
        }
        .pulse-btn:hover {
            transform: scale(1.08);
            box-shadow: 0 0 50px rgba(0,255,204,0.8);
        }
    </style>
</head>
<body class="matrix-bg h-screen w-screen flex items-center justify-center cursor-pointer select-none" onclick="window.location.href='/disclaimer'">

    <div class="flex flex-col items-center text-center p-8 relative z-10 max-w-2xl">
        
        <!-- Üst Güvenlik Simgesi -->
        <div class="w-20 h-20 rounded-full bg-[#00ffcc]/10 border border-[#00ffcc] flex items-center justify-center text-4xl mb-6 shadow-[0_0_20px_rgba(0,255,204,0.3)] animate-pulse">
            🛡️
        </div>

        <!-- Siberpunk Başlık -->
        <h1 class="text-6xl md:text-7xl font-black text-[#00ffcc] tracking-widest mb-3 cyber-glow">Q-AI KERNEL</h1>
        <p class="text-gray-400 text-xs md:text-sm tracking-widest uppercase mb-10 font-bold">Kripto İstihbarat & Algoritmik Sinyal Ağ Geçidi v4.2</p>
        
        <!-- Şok Edici Uyarı Yazısı -->
        <div class="bg-[#0A0A0E] border border-red-500/50 p-4 rounded-xl mb-8 text-red-400 text-xs tracking-wider font-bold shadow-[0_0_15px_rgba(239,68,68,0.2)]">
            ⚠️ GÜVENLİ BAĞLANTI KURULDU: Şifreli Veri Akışı Aktif. Yetkisiz Erişim Denemeleri Kaydedilmektedir.
        </div>

        <!-- Tıklama Butonu -->
        <div class="pulse-btn text-[#030304] font-black px-10 py-5 rounded-full text-base tracking-wider uppercase">
            ⚡ DEVAM ETMEK İÇİN EKRANA TIKLAYINIZ ⚡
        </div>
        
    </div>

</body>
</html>