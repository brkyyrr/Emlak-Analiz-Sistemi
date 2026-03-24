import asyncio
from playwright.async_api import async_playwright
# Hata veren satırı şu şekilde güncelliyoruz:
from playwright_stealth import stealth_async
import pandas as pd
import random
import re

async def run():
    async with async_playwright() as p:
        # Tarayıcıyı başlat
        browser = await p.chromium.launch(headless=True)
        
        # Context oluştur (User agent vb. bilgilerle)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        page = await context.new_page()
        
        # Stealth (Gizlilik) modunu aktif et
        # Eğer yukarıdaki import hata vermeye devam ederse 'stealth_async(page)' yerine 'await stealth_async(page)' deneyebiliriz.
        await stealth_async(page)

        # Senin paylaştığın o detaylı URL
        target_url = "https://www.sahibinden.com/satilik-daire?a1966=true&address_quarter=23160&address_quarter=23172&address_quarter=23161&address_quarter=23165&address_quarter=23158&address_quarter=51416&address_quarter=23159&address_quarter=51417&address_city=34&pagingSize=50&sorting=address_asc&a118798=1277781&a810=40582&a810=40583&a810=40584&a810=40585&a810=40586&a811=236072&a811=40708&a811=40986&a811=40593&a811=40594&a811=40595&a811=40596&a107889_min=90&address_town=446&a20=38474&a20=1227924&a20=38486&a20=1262199&a20=1255142&a20=38471&a20=38485&price_max=7500000"
        
        print("Hedeflenen özel bölge taranıyor...")
        await page.goto(target_url)
        
        # Sitenin yüklenmesi ve bot tespiti için bekleme
        await page.wait_for_timeout(random.randint(7000, 12000))

        items = []
        # Tablo satırlarını bul (Sayfa yapısına göre güncel tutulmalı)
        rows = await page.query_selector_all(".searchResultsItem:not(.nativeAd)")
        
        for row in rows:
            try:
                title_elem = await row.query_selector(".searchResultsTitleValue")
                price_elem = await row.query_selector(".searchResultsPriceValue")
                detail_elems = await row.query_selector_all(".searchResultsAttributeValue")
                
                if title_elem and price_elem:
                    title = await title_elem.inner_text()
                    price_raw = await price_elem.inner_text()
                    
                    # Sayısal temizlik
                    price = int(re.sub(r'[^\d]', '', price_raw))
                    m2 = await detail_elems[0].inner_text() if len(detail_elems) > 0 else "0"
                    m2_val = int(m2.strip())
                    
                    items.append({
                        "Baslik": title.strip(),
                        "Fiyat_TL": price,
                        "Metrekare": m2_val,
                        "Birim_m2": round(price / m2_val) if m2_val > 0 else 0
                    })
            except:
                continue

        # DataFrame oluştur ve kaydet
        df = pd.DataFrame(items)
        # Veri temizliği: Kiracı içerenleri hızlıca ele
        df = df[~df['Baslik'].str.contains('kiracı|hisseli', case=False, na=False)]
        
        output_path = "/app/data/analiz_hazir_liste.csv"
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        print(f"İşlem tamam! {len(df)} adet uygun ilan bulundu.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())