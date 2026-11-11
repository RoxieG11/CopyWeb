<div align="center">

# 🌐 WebClone v2.0 Pro
### 超高速・完全匿名のWebサイトクローナー＆インテリジェンス調査ツール

[![言語](https://img.shields.io/badge/%E8%A8%80%E8%AA%9E-%E6%97%A5%E6%9C%AC%E8%AA%9E-red.svg)](#)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-PyQt6-brightgreen.svg)](https://riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](../../LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-orange.svg)](#)

*Webサイト全体のHTML、CSS、JavaScript、高解像度画像、フォント、メディアファイルをワンクリックで完全クローン。インターネット接続なしで動作する完璧なローカルコピーを作成します。*

---

### 🌐 多言語 / Languages
[English](../../README.md) • [Türkçe](README.tr.md) • [Español](README.es.md) • [简体中文](README.zh-CN.md) • [हिन्दी](README.hi.md) • [العربية](README.ar.md) • [Português](README.pt.md) • [Русский](README.ru.md) • [日本語](README.ja.md) • [Deutsch](README.de.md) • [Français](README.fr.md)

---

</div>

## ✨ 主な機能

### 1. 🎨 洗練されたプレミアムダークUI (PyQt6)
- **Obsidian & Slate テーマ:** 目に優しく、モダンで高級感のあるダークデザイン。
- **多機能タブパネル:**
  - 🚀 **ダッシュボード:** リアルタイムの速度、ファイル/ページカウンター、総転送量表示、ワンクリッククイックアクション (*フォルダを開く*、*ローカルプレビュー*、*index.html起動*、*調査レポート*)。
  - ⚙️ **クローン設定:** クロール深度 (0〜3)、アセット種別フィルター (画像、CSS、JS、フォント、メディア、ドキュメント)、フォルダレイアウト。
  - 🕵️ **プライバシー＆ステルス:** 動的User-Agentローテーション、Referer偽装、人間模倣ディレイ (ジッター)、Proxy/Tor設定。
  - 🔍 **ターゲットインテリジェンス:** サーバーインフラ解析、CMS/技術スタック自動検出、セキュリティヘッダー診断。
  - 📜 **リアルタイムログコンソール:** 検索・フィルタリングに対応した高レスポンスコンソール。
- **アプリ内言語切り替え:** アプリ上部のドロップダウンから即座に表示言語を変更可能。

### 2. ⚡ 超高速マルチスレッド並行ダウンロード
- **ワーカースレッドプール:** 1〜64の並行スレッドで帯域幅を最大活用。
- **HTTP/2＆コネクションプーリング:** ハンドシェイクの遅延を抑え、高速リクエストを実現。
- **スマートディレクトリキャッシュ:** 不要なディスクI/Oを削減。

### 3. 🔍 ターゲット詳細調査＆自動レポート
- **インフラ解析:** サーバーIP、Webサーバー (Nginx, Apache, Cloudflare, Caddy)、バックエンド環境。
- **技術スタック検出:** WordPress, Shopify, Next.js, React, Vue, Nuxt, Tailwind CSS, Bootstrap, jQueryなど。
- **自動レポート生成:** クローン完了時に独立した `recon_report.html` と `recon_report.json` を自動保存。

---

## 🚀 クイックスタート

### Windows
**`run.bat`** または **`WebClone.bat`** をダブルクリックするだけで自動起動します。

### Linux / macOS
```bash
git clone https://github.com/RoxieG11/CopyWeb.git
cd CopyWeb
pip install -r requirements.txt
./run.sh
# または
python3 gui.py
```

---

## 🛡️ ライセンス
本プロジェクトは **MIT ライセンス** の下で公開されています。詳細は [LICENSE](../../LICENSE) をご覧ください。
