# Hafif bir Python imajı seçiyoruz
FROM python:3.11-slim

# Gerekli sistem paketlerini yüklüyoruz
RUN apt-get update && apt-get install -y \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxext6 \
    libxfixes3 libxrandr2 libgbm1 libasound2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Kütüphaneleri kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright tarayıcısını kur
RUN playwright install chromium
RUN playwright install-deps chromium

COPY . .

# Konteyner çalıştığında botu başlat
CMD ["python", "scraper.py"]