import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
import pandas as pd
import random

async def run():
    async with async_playwright() as p:
        # Tarayıcıyı başlat (Görünmez mod)
        browser = await p.chromium.launch(headless=True)
        
        # Gerçek bir kullanıcı gibi davranan bir "context" oluştur
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        # Gizlilik eklentisini aktif et
        await stealth_async(page)

        # HEDEF URL (Örnek: Belirli bir mahalledeki aramalar)
        target_url = "https://www.sahibinden.com/kiralik-daire" 
        
        print(f"Tarama başlıyor: {target_url}")
        await page.goto(target_url)
        
        # Yakalanmamak için rastgele bekleme
        await asyncio.sleep(random.uniform(5, 10))

        # VERİ ÇEKME MANTIĞI (Örnek Selectorlar)
        # Burada ilan başlıklarını, fiyatları ve m2 bilgilerini seçiyoruz
        # Not: Selectorlar sitenin güncel yapısına göre güncellenmelidir.
        items = []
        rows = await page.query_selector_all(".searchResultsItem")
        
        for row in rows:
            try:
                title = await row.query_selector(".searchResultsTitleValue")
                price = await row.query_selector(".searchResultsPriceValue")
                items.append({
                    "baslik": await title.inner_text() if title else "N/A",
                    "fiyat": await price.inner_text() if price else "0",
                    # Diğer detayları buraya ekleyebilirsin
                })
            except:
                continue

        # Veriyi kaydet
        df = pd.DataFrame(items)
        df.to_csv("/app/data/ilanlar.csv", index=False)
        print("İşlem tamamlandı. Veri /data klasörüne kaydedildi.")
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())