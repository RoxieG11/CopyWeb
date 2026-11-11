<div align="center">

# 🌐 WebClone v2.0 Pro
### Clonador de Sitios Web de Alta Velocidad y Herramienta de Reconocimiento Anónimo

[![Idioma](https://img.shields.io/badge/Idioma-Espa%C3%B1ol-yellow.svg)](#)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-PyQt6-brightgreen.svg)](https://riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](../../LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-orange.svg)](#)

*Clona sitios web completos con HTML, CSS, JavaScript, imágenes en alta resolución, fuentes y recursos multimedia con un solo clic. Crea réplicas locales que funcionan sin conexión a Internet.*

---

### 🌐 Idiomas / Languages
[English](../../README.md) • [Türkçe](README.tr.md) • [Español](README.es.md) • [简体中文](README.zh-CN.md) • [हिन्दी](README.hi.md) • [العربية](README.ar.md) • [Português](README.pt.md) • [Русский](README.ru.md) • [日本語](README.ja.md) • [Deutsch](README.de.md) • [Français](README.fr.md)

---

</div>

## ✨ Características Principales

### 1. 🎨 Interfaz Premium y Oscura (PyQt6)
- **Tema Obsidian & Slate:** Interfaz elegante, moderna y cómoda a la vista.
- **Panel Modular Multilenguaje:**
  - 🚀 **Panel de Control:** Velocidad en tiempo real, contadores de archivos, vistas previas rápidas y botones de acción directa.
  - ⚙️ **Configuración:** Profundidad de rastreo (0-3), filtros de tipos de recursos (imágenes, CSS, scripts, fuentes), estructura de carpetas (*Organized* / *Mirror*).
  - 🕵️ **Privacidad y Sigilo:** Rotación dinámica de User-Agent, camuflaje de Referer, retraso humano (*jitter*) y soporte de proxy/Tor.
  - 🔍 **Reconocimiento:** Análisis de infraestructura del servidor, detección de CMS y encabezados de seguridad.
  - 📜 **Consola en Vivo:** Registro detallado con búsqueda y filtrado en tiempo real.
- **Soporte Multilingüe en la Aplicación:** Cambia de idioma en caliente desde la barra superior.

### 2. ⚡ Descargas Paralelas Ultrarrápidas
- **Grupo de Hilos de Trabajo:** De 1 a 64 hilos simultáneos para acelerar la descarga de recursos.
- **HTTP/2 y Conexiones Persistentes:** Reutilización eficiente de conexiones sin sobrecarga de handshake.
- **Caché Inteligente de Directorios:** Reduce lecturas y escrituras redundantes en disco.

### 3. 🔍 Reconocimiento Profundo e Informes Automáticos
- **Informe de Análisis del Objetivo:**
  - 🖥️ **Servidor:** IP, software del servidor web (Nginx, Apache, Cloudflare, Caddy) y motor backend.
  - ⚡ **Pila Tecnológica:** WordPress, Shopify, Next.js, React, Vue, Tailwind CSS, Bootstrap, jQuery, etc.
  - 🛡️ **Seguridad:** Evaluación de encabezados HSTS, CSP, X-Frame-Options.
  - 🤖 **Rastreo:** robots.txt y sitemap.xml automáticos.
  - 📊 **Informes HTML y JSON:** Generación automática de `recon_report.html` y `recon_report.json`.

### 4. 🕵️ Máximo Anonimato y Modo Sigiloso
- **Perfiles Realistas de Navegador:** Windows 11 Chrome, Edge, Firefox, macOS Safari y Linux.
- **Rotación Dinámica:** Cambia la huella digital en cada petición saliente.
- **Client Hints:** Encabezados `Sec-CH-UA` totalmente sincronizados con el User-Agent.
- **Proxy y Tor:** Soporta HTTP, HTTPS, SOCKS5 y Tor (`socks5h://127.0.0.1:9050`) con prueba de latencia e IP en vivo.

---

## 🚀 Inicio Rápido

### En Windows
Haz doble clic en **`run.bat`** o **`WebClone.bat`**.

### En Linux / macOS
```bash
git clone https://github.com/RoxieG11/CopyWeb.git
cd CopyWeb
pip install -r requirements.txt
./run.sh
# o
python3 gui.py
```

---

## 🛡️ Licencia
Distribuido bajo la Licencia **MIT**. Consulta [LICENSE](../../LICENSE) para más detalles.
