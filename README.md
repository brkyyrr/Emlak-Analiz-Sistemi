# Emlak Analiz Sistemi - v1.0 (Core Scraper)

Bu proje, emlak sitelerinden veri toplamak ve bu verileri LLM (Claude/Gemini) analizi için hazır hale getirmek amacıyla geliştirilmiş bir **Veri Hattı (Data Pipeline)** projesidir.

## 🚀 Özellikler
- **Dockerized Mimari:** Sistem tamamen izole bir Docker konteyneri içinde çalışır.
- **Headless Automation:** Playwright kullanarak tarayıcıyı arka planda (görünmez) çalıştırır.
- **Temel Veri Çekme:** İlan başlığı ve fiyat bilgilerini hedef siteden toplar.

## 📁 Proje Yapısı
- `scraper.py`: Ana bot kodu.
- `Dockerfile`: Konteyner yapılandırması.
- `data/`: Çıktıların (CSV) kaydedildiği klasör.

## 🛠️ Kurulum ve Çalıştırma
1. İmajı oluştur:
   `docker build -t emlak-botu-v1 .`
2. Konteyneri çalıştır:
   `docker run -v ${PWD}/data:/app/data emlak-botu-v1`

## 📊 Analiz
Oluşan `ilanlar.csv` dosyasını Claude'a yükleyerek temel bir fiyat analizi yaptırılabilir.