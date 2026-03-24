import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async
import pandas as pd
import random
import re

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await stealth_async(page)

        # BURAYI GÜNCELLE: Tarayıcıdan kopyaladığın filtrelenmiş URL'yi buraya yapıştır
        target_url = "https://www.sahibinden.com/satilik-daire?a1966=true&address_quarter=23160&address_quarter=23172&address_quarter=23161&address_quarter=23165&address_quarter=23158&address_quarter=51416&address_quarter=23159&address_quarter=51417&address_city=34&pagingSize=50&sorting=address_asc&a118798=1277781&a810=40582&a810=40583&a810=40584&a810=40585&a810=40586&a811=236072&a811=40708&a811=40986&a811=40593&a811=40594&a811=40595&a811=40596&a107889_min=90&address_town=446&a20=38474&a20=1227924&a20=38486&a20=1262199&a20=1255142&a20=38471&a20=38485&price_max=7500000" 
        
        print("Hedef bölge taranıyor...")
        await page.goto(target_url)
        await asyncio.sleep(random.uniform(7, 12)) # Bloklanmamak için uzun bekleme

        items = []
        rows = await page.query_selector_all(".searchResultsItem:not(.nativeAd)")
        
        for row in rows:
            try:
                title = await (await row.query_selector(".searchResultsTitleValue")).inner_text()
                price_raw = await (await row.query_selector(".searchResultsPriceValue")).inner_text()
                details = await row.query_selector_all(".searchResultsAttributeValue")
                
                # Veri Temizleme (Data Cleaning)
                # Fiyatı sadece sayıya çevir (Örn: "15.500.000 TL" -> 15500000)
                price = int(re.sub(r'[^\d]', '', price_raw))
                
                m2 = await details[0].inner_text() if len(details) > 0 else "0"
                rooms = await details[1].inner_text() if len(details) > 1 else "N/A"

                items.append({
                    "Baslik": title.strip(),
                    "Fiyat_TL": price,
                    "Metrekare": int(m2.strip()),
                    "Oda_Sayisi": rooms.strip(),
                    "Birim_m2_Fiyatı": round(price / int(m2.strip())) if int(m2.strip()) > 0 else 0
                })
            except Exception as e:
                continue

        # CSV Kaydı
        df = pd.DataFrame(items)
        # Önemli: Boş veya hatalı verileri temizle
        df = df[df["Fiyat_TL"] > 0]
        df.to_csv("/app/data/temiz_satilik_evler.csv", index=False, encoding='utf-8-sig')
        
        print(f"{len(df)} adet temiz veri kaydedildi.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())