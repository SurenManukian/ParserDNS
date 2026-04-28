# 🕷️ DNS Price Parser

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://www.python.org/)
[![Playwright](https://img.shields.io/badge/Playwright-1.40%2B-green?logo=playwright)](https://playwright.dev/)
[![SQLite](https://img.shields.io/badge/SQLite-3-blue?logo=sqlite)](https://sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status](https://img.shields.io/badge/Status-Working-brightgreen)]()

Парсер цен товаров из интернет-магазина DNS с автоматическим сохранением данных в SQLite. Использует Playwright для обхода защиты и извлечения JSON-LD.

## 📦 Возможности
- Извлечение цены товара из `application/ld+json`
- Обход антибот-защиты (подмена User-Agent, заголовков, случайный скролл)
- Сохранение истории цен в локальную БД (`prices.db`)
- Поддержка любого URL товара DNS (ввод через консоль)

## 🚀 Установка и запуск

1. **Клонируй репозиторий** (или создай файл `parser.py` с твоим кодом)
 ```git clone https://github.com/SurenManukian/ParserDNS.git```

3. **Установи зависимости:**
   ```bash
   pip install playwright
   playwright install chromium  ```
4. Запусти парсер:
  ```cd ParserDNS```
``` python parser.py```
4. Введи ссылку на товар DNS
Например:
```https://www.dns-shop.ru/product/...```
5. Введи название товара:
Например:
```RTX 5060, IP17 и тд```

# Парсер откроет браузер, найдёт цену и сохранит её в prices.db.

##🙌 Пример вывода

```Введите URL товара из DNS: https://www.dns-shop.ru/product/...
[2026-04-28T12:34:56.789012] Сохранена цена: 199999.0
Цена: 199999.0```

