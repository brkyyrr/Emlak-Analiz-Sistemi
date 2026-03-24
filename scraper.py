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
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await stealth_async(page)

        target_url = "https://www.sahibinden.com/satilik-daire?a1966=true&address_quarter=23160&address_quarter=23172&address_quarter=23161&address_quarter=23165&address_quarter=23158&address_quarter=51416&address_quarter=23159&address_quarter=51417&address_city=34&pagingSize=50&sorting=address_asc&a118798=1277781&a810=40582&a810=40583&a810=40584&a810=40585&a810=40586&a811=236072&a811=40708&a811=40986&a811=40593&a811=40594&a811=40595&a811=40596&a107889_min=90&address_town=446&a20=38474&a20=1227924&a20=38486&a20=1262199&a20=1255142&a20=38471&a20=38485&price_max=7500000"
        
        print("Hedeflenen özel bölge taranıyor...")
        await page.goto(target_url, wait_until="networkidle") # Sayfanın tamamen yüklenmesini bekle
        
        # Ekran görüntüsü al (Hata olursa ne gördüğümüzü anlamak için /app/data içine atar)
        await page.screenshot(path="/app/data/son_durum.png")
        
        await asyncio.sleep(random.uniform(5, 10))

        items = []
        rows = await page.query_selector_all(".searchResultsItem:not(.nativeAd)")
        
        print(f"Bulunan satır sayısı: {len(rows)}") # Kaç ilan yakaladığını terminalde gör

        for row in rows:
            try:
                # Daha esnek selectorlar
                title_elem = await row.query_selector(".searchResultsTitleValue")
                price_elem = await row.query_selector(".searchResultsPriceValue")
                detail_elems = await row.query_selector_all("td.searchResultsAttributeValue")
                
                if title_elem and price_elem:
                    title = await title_elem.inner_text()
                    price_raw = await price_elem.inner_text()
                    
                    price = int(re.sub(r'[^\d]', '', price_raw))
                    m2 = await detail_elems[0].inner_text() if len(detail_elems) > 0 else "0"
                    m2_val = int(re.sub(r'[^\d]', '', m2)) if m2.strip() else 0
                    
                    items.append({
                        "Baslik": title.strip(),
                        "Fiyat_TL": price,
                        "Metrekare": m2_val,
                        "Birim_m2": round(price / m2_val) if m2_val > 0 else 0
                    })
            except Exception as e:
                continue

        # --- KRİTİK HATA KONTROLÜ ---
        if not items:
            print("⚠️ UYARI: Hiç veri çekilemedi! Site engellemiş veya selector değişmiş olabilir.")
            print("Lütfen 'data/son_durum.png' dosyasını kontrol ederek botun ne gördüğüne bak.")
            return # Programı çökmeden durdur

        df = pd.DataFrame(items)
        
        # Sütun var mı kontrolü
        if 'Baslik' in df.columns:
            df = df[~df['Baslik'].str.contains('kiracı|hisseli', case=False, na=False)]
            df.to_csv("/app/data/analiz_hazir_liste.csv", index=False, encoding='utf-8-sig')
            print(f"✅ İşlem başarılı. {len(df)} ilan kaydedildi.")
        else:
            print("❌ HATA: DataFrame oluşturuldu ama 'Baslik' sütunu bulunamadı.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())