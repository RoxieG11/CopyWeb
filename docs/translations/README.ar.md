<div align="center">

# 🌐 WebClone v2.0 Pro
### أداة استنساخ مواقع الويب فائقة السرعة وجمع المعلومات الاستخباراتية بهوية مجهولة

[![اللغة](https://img.shields.io/badge/%D8%A7%D9%84%D9%84%D8%BA%D8%A9-%D8%A7%D9%84%D8%B9%D8%B1%D8%A8%D9%8A%D8%A9-green.svg)](#)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![GUI](https://img.shields.io/badge/GUI-PyQt6-brightgreen.svg)](https://riverbankcomputing.com/software/pyqt/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](../../LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-orange.svg)](#)

*استنسخ مواقع الويب بالكامل بنقرة واحدة مع ملفات HTML و CSS و JavaScript والصور عالية الدقة والخطوط والوسائط المتعددة. أنشئ نسخاً محلية مطابقة تعمل دون الحاجة إلى اتصال بالإنترنت.*

---

### 🌐 اللغات / Languages
[English](../../README.md) • [Türkçe](README.tr.md) • [Español](README.es.md) • [简体中文](README.zh-CN.md) • [हिन्दी](README.hi.md) • [العربية](README.ar.md) • [Português](README.pt.md) • [Русский](README.ru.md) • [日本語](README.ja.md) • [Deutsch](README.de.md) • [Français](README.fr.md)

---

</div>

## ✨ الميزات الرئيسية

### 1. 🎨 واجهة داكنة متميزة وأنيقة (PyQt6)
- **مظهر عصري ومريح للعين:** تصميم أسود ورمادي أنيق وبسيط.
- **لوحة تحكم متعددة التبويبات:**
  - 🚀 **نظرة عامة:** سرعة التنزيل اللحظية، عدادات الملفات والصفحات، وأزرار الإجراءات السريعة (*فتح المجلد*، *المعاينة المباشرة*، *فتح التقرير*).
  - ⚙️ **إعدادات الاستنساخ:** عمق الروابط (0-3)، فلاتر أنواع الملفات، وترتيب المجلدات.
  - 🕵️ **الخصوصية وإخفاء الهوية:** تدوير وكيل المستخدم (User-Agent)، تمويه المصدر (Referer)، ومحاكاة السلوك البشري.
  - 🔍 **استخبارات الهدف:** فحص خادم الويب، واكتشاف أنظمة إدارة المحتوى (CMS)، وتقييم أمان الرؤوس.
  - 📜 **وحدة التحكم الحية:** سجل تفاعلي مع إمكانية البحث والتصفية.
- **دعم مدمج لتغيير اللغة:** التبديل الفوري بين اللغات مباشرة من واجهة التطبيق.

### 2. ⚡ تنزيل متزامن فائق السرعة
- **مجموعة مسارات عمل متوازية:** من 1 إلى 64 مساراً متزامناً لتنزيل الملفات بأقصى سرعة.
- **بروتوكول HTTP/2:** استغلال الجلسات المستمرة لتفادي تأخير الاتصال.
- **تخزين مؤقت ذكي للمجلدات:** تحسين عمليات القراءة والكتابة على القرص.

### 3. 🔍 تقارير استخباراتية شاملة
- **تحليل الخادم والبنية التحتية:** عنوان IP، ونوع الخادم (Nginx, Apache, Cloudflare)، والتقنيات المستخدمة.
- **اكتشاف التقنيات:** كشف WordPress, Shopify, Next.js, React, Vue, Tailwind CSS, Bootstrap وغيرها.
- **تقارير تلقائية:** إنشاء تقرير شامل بتنسيقي `recon_report.html` و `recon_report.json`.

---

## 🚀 البدء السريع

### على نظام ويندوز (Windows)
انقر نقراً مزدوجاً فوق الملف **`run.bat`** أو **`WebClone.bat`**.

### على أنظمة لينكس وماك (Linux / macOS)
```bash
git clone https://github.com/RoxieG11/CopyWeb.git
cd CopyWeb
pip install -r requirements.txt
./run.sh
# أو
python3 gui.py
```

---

## 🛡️ الترخيص
هذا المشروع مرخص بموجب ترخيص **MIT**. لمزيد من التفاصيل، راجع ملف [LICENSE](../../LICENSE).
