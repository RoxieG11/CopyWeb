<div align="center">

# 🌐 WebClone v2.0 Pro
### Высокоскоростной анонимный клонёр веб-сайтов и инструмент разведки

[![Язык](https://img.shields.io/badge/%D0%AF%D0%B7%D1%8B%D0%BA-%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9-red.svg)](#)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-PyQt6-brightgreen.svg)](https://riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](../../LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-orange.svg)](#)

*Клонируйте веб-сайты целиком со всеми HTML, CSS, JavaScript, изображениями в высоком разрешении, шрифтами и медиафайлами в один клик. Создавайте полноценные автономные локальные копии, работающие без интернета.*

---

### 🌐 Языки / Languages
[English](../../README.md) • [Türkçe](README.tr.md) • [Español](README.es.md) • [简体中文](README.zh-CN.md) • [हिन्दी](README.hi.md) • [العربية](README.ar.md) • [Português](README.pt.md) • [Русский](README.ru.md) • [日本語](README.ja.md) • [Deutsch](README.de.md) • [Français](README.fr.md)

---

</div>

## ✨ Основные возможности

### 1. 🎨 Премиальный темный интерфейс (PyQt6)
- **Тема Obsidian & Slate:** Стильный, лаконичный и удобный для глаз интерфейс.
- **Многовкладочная панель управления:**
  - 🚀 **Обзор:** Скорость в реальном времени, счетчики файлов и страниц, быстрые действия (*Открыть папку*, *Предпросмотр*, *Открыть index.html*, *Отчет разведки*).
  - ⚙️ **Настройки клонирования:** Глубина ссылок (0-3), выбор типов файлов (изображения, стили, скрипты, шрифты, медиа, документы), структура папок.
  - 🕵️ **Анонимность и скрытность:** Ротация User-Agent, маскировка Referer, имитация действий человека (jitter), поддержка Proxy и Tor.
  - 🔍 **Разведка цели:** Анализ серверной инфраструктуры, стек CMS и фреймворков, проверка заголовков безопасности.
  - 📜 **Консоль в реальном времени:** Подробный лог с быстрым поиском и фильтрацией.
- **Встроенная поддержка смены языка:** Мгновенное переключение языка прямо в шапке программы.

### 2. ⚡ Сверхбыстрая параллельная загрузка
- **Пул потоков:** От 1 до 64 параллельных потоков для максимальной скорости скачивания ресурсов.
- **HTTP/2 и Keep-Alive:** Повторное использование соединений без задержек на повторные рукопожатия.
- **Интеллектуальное кэширование путей:** Минимизация лишних операций ввода-вывода диска.

### 3. 🔍 Глубокая разведка и автоматические отчеты
- **Анализ сервера:** IP-адрес, веб-сервер (Nginx, Apache, Cloudflare), стек технологий (WordPress, Shopify, Next.js, React, Vue, Tailwind CSS, Bootstrap).
- **robots.txt и sitemap.xml:** Автоматический сбор скрытых ссылок и карты сайта.
- **Автоматические отчеты:** Сохранение `recon_report.html` и `recon_report.json` в папку с сайтом.

---

## 🚀 Быстрый старт

### Windows
Дважды щелкните по файлу **`run.bat`** или **`WebClone.bat`**.

### Linux / macOS
```bash
git clone https://github.com/RoxieG11/CopyWeb.git
cd CopyWeb
pip install -r requirements.txt
./run.sh
# или
python3 gui.py
```

---

## 🛡️ Лицензия
Проект распространяется под лицензией **MIT**. Подробности в файле [LICENSE](../../LICENSE).
