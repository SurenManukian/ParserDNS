from playwright.sync_api import sync_playwright
import json
import sqlite3
from datetime import datetime

url = input("Введите URL товара из DNS: ")
tovar = input("Введите название товара(которое добавится в бд): ")
def init_db():
    """Создаёт таблицу prices, если её ещё нет"""
    conn = sqlite3.connect('prices.db')
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            product_name TEXT,
            platform TEXT,
            price REAL,
            url TEXT
        )
    ''')
    conn.commit()
    conn.close()
    
 
def save_price(product_name, platform, price, url):
    """Сохраняет одно измерение в БД"""
    conn = sqlite3.connect('prices.db')
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO prices (timestamp, product_name, platform, price, url)
        VALUES (?, ?, ?, ?, ?)
    ''', (datetime.now().isoformat(), product_name, platform, price, url))
    conn.commit()
    conn.close()

def get_price_from_product_page(url):
    with sync_playwright() as p:
        
        browser = p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        
        
        page.set_extra_http_headers({
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
        })
        
       
        page.goto(url, wait_until='networkidle')  
        page.wait_for_timeout(5000)  
        
       
        page.mouse.wheel(0, 300)
        page.wait_for_timeout(1000)
        
        # Ищем JSON-LD как раньше
        all_script_tags = page.query_selector_all('script')
        product_data = None
        for script_tag in all_script_tags:
            if script_tag.get_attribute('type') == 'application/ld+json':
                json_content = script_tag.inner_text()
                product_data = json.loads(json_content)
                break
        
        if product_data and 'offers' in product_data:
            price = product_data['offers']['price']
            browser.close()
            
            save_price(
                product_name=tovar,   
                platform="DNS",
                price=price,
                url=url
            )
            print(f"[{datetime.now()}] Сохранена цена: {price}")
            return price
        else:
            print("Не удалось найти JSON-LD с ценой.")
            
            page.screenshot(path='debug_screenshot.png')
            with open('debug_page.html', 'w', encoding='utf-8') as f:
                f.write(page.content())
            browser.close()
            return None

if __name__ == '__main__':
    init_db()
    price = get_price_from_product_page(url)
    print(f'Цена: {price}')
   
