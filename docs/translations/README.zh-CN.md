<div align="center">

# 🌐 WebClone v2.0 Pro
### 超高速、全匿名网站克隆与目标情报侦察工具

[![语言](https://img.shields.io/badge/%E8%AF%AD%E8%A8%80-%E7%AE%80%E4%BD%93%E4%B8%AD%E6%96%87-red.svg)](#)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-PyQt6-brightgreen.svg)](https://riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](../../LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-orange.svg)](#)

*一键完整克隆网站的所有 HTML、CSS、JavaScript、高清图像、字体与多媒体资源。生成完全离线可用的本地镜像网站。*

---

### 🌐 多语言 / Languages
[English](../../README.md) • [Türkçe](README.tr.md) • [Español](README.es.md) • [简体中文](README.zh-CN.md) • [हिन्दी](README.hi.md) • [العربية](README.ar.md) • [Português](README.pt.md) • [Русский](README.ru.md) • [日本語](README.ja.md) • [Deutsch](README.de.md) • [Français](README.fr.md)

---

</div>

## ✨ 核心特性

### 1. 🎨 极简高级暗黑界面 (PyQt6)
- **曜石暗黑主题:** 优雅舒适的高级暗黑视觉设计。
- **多标签分类面板:**
  - 🚀 **控制面板:** 实时下载速度、文件/页面计数器、总下载量仪表盘与一键快捷动作 (*打开文件夹*、*本地预览*、*打开主页*、*侦察报告*)。
  - ⚙️ **克隆设置:** 爬取深度 (0-3)、资源类型选择 (图片、样式表、脚本、字体、媒体、文档)、存储布局 (分类整理 / 服务器镜像)。
  - 🕵️ **隐私与隐身:** 动态 User-Agent 轮换、来源 Referer 伪装、随机行为延时 (Jitter) 与 Proxy/Tor 代理配置。
  - 🔍 **目标情报侦察:** 目标服务器 IP、CMS/技术栈识别、robots.txt 及站点地图提取。
  - 📜 **实时控制台:** 带搜索与过滤功能的高性能终端日志。
- **内置多语言一键切换:** 界面内直接支持中文、英语、土耳其语、西班牙语、德语与俄语即时切换。

### 2. ⚡ 高并发多线程下载
- **并发线程池:** 1 到 64 个并发工作线程，最大化利用带宽高速下载。
- **HTTP/2 与连接复用:** Keep-Alive 会话池杜绝重复握手延迟。
- **智能目录缓存:** 消除冗余磁盘 I/O，写入更流畅。
- **流式解压支持:** 自动处理 Brotli、Gzip、Deflate 和 Zstandard 压缩包。

### 3. 🔍 深度目标侦察与报告生成
- **自动化目标分析报告:**
  - 🖥️ **基础设施:** 服务器 IP 地址、Web 服务器软件 (Nginx, Apache, Cloudflare, Caddy 等)、后端框架。
  - ⚡ **技术栈识别:** WordPress, Shopify, Next.js, React, Vue, Nuxt, Tailwind CSS, Bootstrap, jQuery 等。
  - 🛡️ **安全响应头分析:** HSTS, CSP, X-Frame-Options 完整评估。
  - 🤖 **站点结构提取:** 自动探测 robots.txt 与 sitemap.xml。
  - 📊 **可视化报告:** 克隆完成后自动生成独立的 `recon_report.html` 与 `recon_report.json`。

### 4. 🕵️ 极致匿名与防检测模式
- **真实浏览器指纹库:** 覆盖 Windows 11 Chrome, Edge, Firefox, macOS Safari 及 Linux。
- **动态指纹伪装:** 每次请求动态更换 User-Agent 与对应的 Client Hints (`Sec-CH-UA`)。
- **Proxy 与 Tor 代理集成:** 全面支持 HTTP、HTTPS、SOCKS5 与 Tor (`socks5h://127.0.0.1:9050`)，内建 IP 与延迟测试工具。

---

## 🚀 快速开始

### Windows 系统
直接双击运行 **`run.bat`** 或 **`WebClone.bat`** 即可。

### Linux / macOS 系统
```bash
git clone https://github.com/RoxieG11/CopyWeb.git
cd CopyWeb
pip install -r requirements.txt
./run.sh
# 或
python3 gui.py
```

---

## 🛡️ 开源协议
本项目采用 **MIT** 许可证，详情请参阅 [LICENSE](../../LICENSE) 文件。
