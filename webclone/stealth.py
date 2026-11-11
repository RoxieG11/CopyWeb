"""WebClone Gizlilik ve Anonimlik Modülü.

Gelişmiş User-Agent rotasyonu, Client Hints (Sec-CH-UA), HTTP başlık taklidi,
Referer kamuflajı, Proxy yönetimi (HTTP/HTTPS/SOCKS5/Tor) ve insan davranışı taklidi.
"""
from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlsplit


@dataclass(frozen=True)
class BrowserProfile:
    name: str
    user_agent: str
    sec_ch_ua: str
    sec_ch_ua_mobile: str
    sec_ch_ua_platform: str
    platform_name: str
    accept: str
    accept_language: str
    accept_encoding: str = "gzip, deflate, br, zstd"


# Gerçekçi ve güncel tarayıcı parmak izleri
PROFILES: list[BrowserProfile] = [
    BrowserProfile(
        name="Chrome (Windows 11)",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        sec_ch_ua='"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        sec_ch_ua_mobile="?0",
        sec_ch_ua_platform='"Windows"',
        platform_name="Windows",
        accept="text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        accept_language="tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    ),
    BrowserProfile(
        name="Firefox (Windows 11)",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
        sec_ch_ua="",  # Firefox Client Hints göndermez
        sec_ch_ua_mobile="?0",
        sec_ch_ua_platform='"Windows"',
        platform_name="Windows",
        accept="text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        accept_language="tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    ),
    BrowserProfile(
        name="Edge (Windows 11)",
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0",
        sec_ch_ua='"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        sec_ch_ua_mobile="?0",
        sec_ch_ua_platform='"Windows"',
        platform_name="Windows",
        accept="text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        accept_language="tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    ),
    BrowserProfile(
        name="Chrome (macOS)",
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        sec_ch_ua='"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        sec_ch_ua_mobile="?0",
        sec_ch_ua_platform='"macOS"',
        platform_name="macOS",
        accept="text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        accept_language="tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    ),
    BrowserProfile(
        name="Safari (macOS)",
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Safari/605.1.15",
        sec_ch_ua="",
        sec_ch_ua_mobile="?0",
        sec_ch_ua_platform='"macOS"',
        platform_name="macOS",
        accept="text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        accept_language="tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    ),
    BrowserProfile(
        name="Firefox (Linux)",
        user_agent="Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0",
        sec_ch_ua="",
        sec_ch_ua_mobile="?0",
        sec_ch_ua_platform='"Linux"',
        platform_name="Linux",
        accept="text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        accept_language="tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    ),
]

REFERER_PRESETS: dict[str, str] = {
    "google": "https://www.google.com/",
    "duckduckgo": "https://duckduckgo.com/",
    "bing": "https://www.bing.com/",
    "yandex": "https://yandex.com.tr/",
    "twitter": "https://t.co/",
    "none": "",
}


class StealthManager:
    """İstek başlıklarını, gizliliği, vekil sunucuları (proxy) ve insan gecikmelerini yönetir."""

    def __init__(
        self,
        profile_name: str = "random",
        proxy: str | None = None,
        referer_mode: str = "google",
        min_delay: float = 0.0,
        max_delay: float = 0.0,
        rotate_ua: bool = False,
    ):
        self.profile_name = profile_name
        self.proxy = proxy.strip() if proxy else None
        self.referer_mode = referer_mode
        self.min_delay = max(0.0, min_delay)
        self.max_delay = max(self.min_delay, max_delay)
        self.rotate_ua = rotate_ua
        self._current_profile = self._resolve_profile(profile_name)

    def _resolve_profile(self, name: str) -> BrowserProfile:
        if name == "random" or not name:
            return random.choice(PROFILES)
        for p in PROFILES:
            if p.name.lower() == name.lower() or name.lower() in p.name.lower():
                return p
        # Özel veya bulunamazsa varsayılan Windows Chrome
        return PROFILES[0]

    def get_profile(self) -> BrowserProfile:
        if self.rotate_ua:
            return random.choice(PROFILES)
        return self._current_profile

    def get_headers(
        self,
        url: str,
        is_page: bool = True,
        kind: str = "page",
        custom_referer: str | None = None,
    ) -> dict[str, str]:
        """Hedef istek için güvenli ve gerçekçi HTTP başlıkları oluşturur."""
        prof = self.get_profile()

        headers: dict[str, str] = {
            "User-Agent": prof.user_agent,
            "Accept-Language": prof.accept_language,
            "Accept-Encoding": prof.accept_encoding,
            "DNT": "1",
            "Sec-GPC": "1",
            "Upgrade-Insecure-Requests": "1" if is_page else "0",
        }

        # Client Hints (Chrome / Edge için)
        if prof.sec_ch_ua:
            headers["sec-ch-ua"] = prof.sec_ch_ua
            headers["sec-ch-ua-mobile"] = prof.sec_ch_ua_mobile
            headers["sec-ch-ua-platform"] = prof.sec_ch_ua_platform

        # Sec-Fetch Metadata
        if is_page:
            headers["Accept"] = prof.accept
            headers["Sec-Fetch-Dest"] = "document"
            headers["Sec-Fetch-Mode"] = "navigate"
            headers["Sec-Fetch-Site"] = "cross-site" if not custom_referer else "same-origin"
            headers["Sec-Fetch-User"] = "?1"
        else:
            headers["Sec-Fetch-Site"] = "same-origin"
            if kind == "css":
                headers["Accept"] = "text/css,*/*;q=0.1"
                headers["Sec-Fetch-Dest"] = "style"
                headers["Sec-Fetch-Mode"] = "no-cors"
            elif kind == "js":
                headers["Accept"] = "*/*"
                headers["Sec-Fetch-Dest"] = "script"
                headers["Sec-Fetch-Mode"] = "no-cors"
            elif kind == "img":
                headers["Accept"] = "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
                headers["Sec-Fetch-Dest"] = "image"
                headers["Sec-Fetch-Mode"] = "no-cors"
            elif kind == "font":
                headers["Accept"] = "*/*"
                headers["Sec-Fetch-Dest"] = "font"
                headers["Sec-Fetch-Mode"] = "cors"
            else:
                headers["Accept"] = "*/*"
                headers["Sec-Fetch-Dest"] = "empty"
                headers["Sec-Fetch-Mode"] = "cors"

        # Referer
        ref = self.get_referer(url, custom_referer)
        if ref:
            headers["Referer"] = ref

        return headers

    def get_referer(self, target_url: str, custom_referer: str | None = None) -> str:
        if custom_referer:
            return custom_referer
        mode = self.referer_mode.lower()
        if mode in REFERER_PRESETS:
            return REFERER_PRESETS[mode]
        if mode == "self":
            parts = urlsplit(target_url)
            return f"{parts.scheme}://{parts.netloc}/"
        if mode.startswith("http://") or mode.startswith("https://"):
            return mode
        return ""

    def apply_delay(self) -> float:
        """Gerekiyorsa rastgele insan gecikmesi uygular ve uyunan süreyi döndürür."""
        if self.max_delay <= 0:
            return 0.0
        delay = random.uniform(self.min_delay, self.max_delay)
        time.sleep(delay)
        return delay

    def get_proxy_dict(self) -> dict[str, str] | None:
        """`requests` kütüphanesinin anlayacağı vekil sunucu sözlüğü üretir."""
        if not self.proxy:
            return None
        px = self.proxy.strip()
        if not px:
            return None
        # Şema yoksa varsayılan http:// ekle
        if "://" not in px:
            px = f"http://{px}"
        # socks5:// -> DNS sızıntılarını önlemek için socks5h:// tercih et
        if px.startswith("socks5://"):
            px = "socks5h://" + px[9:]
        return {
            "http": px,
            "https": px,
        }

    @staticmethod
    def test_proxy(proxy_url: str, timeout: float = 8.0) -> dict[str, Any]:
        """Vekil sunucunun çalışıp çalışmadığını test eder ve dış IP adresini döndürür."""
        import requests

        px = proxy_url.strip()
        if "://" not in px:
            px = f"http://{px}"
        if px.startswith("socks5://"):
            px = "socks5h://" + px[9:]

        proxies = {"http": px, "https": px}
        t0 = time.monotonic()
        try:
            r = requests.get(
                "https://api.ipify.org?format=json",
                proxies=proxies,
                timeout=timeout,
                headers={"User-Agent": PROFILES[0].user_agent},
            )
            r.raise_for_status()
            ip = r.json().get("ip", "Bilinmiyor")
            elapsed = time.monotonic() - t0
            return {"ok": True, "ip": ip, "latency": round(elapsed * 1000, 1), "error": None}
        except Exception as e:  # noqa: BLE001
            return {"ok": False, "ip": None, "latency": None, "error": str(e)}
