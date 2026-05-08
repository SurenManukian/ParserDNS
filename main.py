import sys
import json
from datetime import datetime
import sqlite3
from playwright.sync_api import sync_playwright
from PyQt6.QtWidgets import (
    QApplication, QListWidgetItem, QListWidget, QWidget,
    QVBoxLayout, QGridLayout, QPushButton, QLineEdit, QLabel
)


class Search:
    def init_db(self):
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

    def save_price(self, product_name, platform, price, url):
        conn = sqlite3.connect('prices.db')
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO prices (timestamp, product_name, platform, price, url)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), product_name, platform, price, url))
        conn.commit()
        conn.close()

    def get_price_from_product_page(self, url):
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

            product_name = None
            price = None

            all_script_tags = page.query_selector_all('script[type="application/ld+json"]')
            for script_tag in all_script_tags:
                try:
                    data = json.loads(script_tag.inner_text())
                    if isinstance(data, dict) and data.get('@type') == 'Product':
                        product_name = data.get('name')
                        offers = data.get('offers', {})
                        if isinstance(offers, dict):
                            price = offers.get('price')
                        elif isinstance(offers, list) and len(offers) > 0:
                            price = offers[0].get('price')
                        if product_name and price:
                            break
                    if isinstance(data, dict) and '@graph' in data:
                        for item in data['@graph']:
                            if item.get('@type') == 'Product':
                                product_name = item.get('name')
                                offers = item.get('offers', {})
                                if isinstance(offers, dict):
                                    price = offers.get('price')
                                elif isinstance(offers, list) and len(offers) > 0:
                                    price = offers[0].get('price')
                                if product_name and price:
                                    break
                        if product_name and price:
                            break
                    if isinstance(data, list):
                        for item in data:
                            if item.get('@type') == 'Product':
                                product_name = item.get('name')
                                offers = item.get('offers', {})
                                if isinstance(offers, dict):
                                    price = offers.get('price')
                                elif isinstance(offers, list) and len(offers) > 0:
                                    price = offers[0].get('price')
                                if product_name and price:
                                    break
                        if product_name and price:
                            break
                except (json.JSONDecodeError, KeyError, TypeError):
                    continue

            if not product_name:
                h1 = page.query_selector('h1')
                if h1:
                    product_name = h1.inner_text().strip()

            if not price:
                price_selectors = [
                    '.product-buy__price',
                    '.current-price',
                    '.price',
                    '[data-role="price"]'
                ]
                for selector in price_selectors:
                    elem = page.query_selector(selector)
                    if elem:
                        price_text = elem.inner_text().strip()
                        price_text = price_text.replace(' ', '').replace(' ', '').replace(',', '.')
                        import re
                        match = re.search(r'(\d+[\.,]?\d*)', price_text)
                        if match:
                            price = float(match.group(1).replace(',', '.'))
                            break

            browser.close()

            if product_name and price:
                self.save_price(product_name, "DNS", price, url)
                return price
            return None


My_search = Search()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initializeUI()
        self.open_sql()

    def initializeUI(self):
        self.setWindowTitle("V1.0")
        self.resize(600, 900)
        self.setUpMainWindow()
        self.show()

    def setUpMainWindow(self):
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel("Парсер цен из DNS", self))

        grid_layout = QGridLayout()
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Введите ссылку для парсинга")
        grid_layout.addWidget(self.line_edit, 0, 0)
        self.button_url = QPushButton("Поиск")
        self.button_url.clicked.connect(self.save_request)
        grid_layout.addWidget(self.button_url, 0, 1)

        grid_layout.addWidget(QLabel("Ваши товары:", self), 1, 0, 1, 2)
        self.list_widget = QListWidget(self)
        grid_layout.addWidget(self.list_widget, 2, 0, 1, 2)

        main_layout.addLayout(grid_layout)
        main_layout.addStretch()
        self.setLayout(main_layout)

    def open_sql(self):
        conn = sqlite3.connect('prices.db')
        cursor = conn.cursor()
        cursor.execute('SELECT product_name, price, timestamp FROM prices ORDER BY timestamp DESC')
        results = cursor.fetchall()
        conn.close()

        self.list_widget.clear()
        if results:
            for product_name, price, timestamp in results:
                dt = datetime.fromisoformat(timestamp).strftime("%d.%m.%Y %H:%M")
                if product_name is None:
                    text = f"Товар без имени — {price} руб. ({dt})"
                else:
                    text = f"{product_name} — {price} руб. ({dt})"
                self.list_widget.addItem(QListWidgetItem(text))
        else:
            self.list_widget.addItem(QListWidgetItem("Пока что вы не смотрели ни один запрос"))

    def refresh_list(self):
        self.open_sql()

    def save_request(self):
        url = self.line_edit.text()
        if url:
            My_search.get_price_from_product_page(url)
            self.refresh_list()


if __name__ == '__main__':
    My_search.init_db()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
