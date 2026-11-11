"""HTML ve CSS içindeki URL'leri yeniden yazan ve varlıkları keşfeden yardımcılar."""
from __future__ import annotations

import codecs
import html
import re
from html.parser import HTMLParser
from typing import Callable, Protocol

# ---------------------------------------------------------------- CSS

# @import "a.css" | @import url(a.css) | url(...) | image-set(...)
_CSS_REF_RE = re.compile(
    r"""@import\s+(?:url\(\s*)?(?P<iq>["']?)(?P<iurl>[^"')\s;]+)(?P=iq)\s*\)?"""
    r"""|url\(\s*(?P<q>["']?)(?P<url>.*?)(?P=q)\s*\)"""
    r"""|image-set\(\s*(?P<set>.*?)\)""",
    re.IGNORECASE | re.DOTALL,
)

CssResolver = Callable[[str, str], "str | None"]


def rewrite_css(text: str, resolver: CssResolver) -> str:
    def repl(m: re.Match) -> str:
        if m.group("iurl") is not None:
            new = resolver(m.group("iurl"), "css")
            return f'@import url("{new}")' if new else m.group(0)
        if m.group("url") is not None:
            raw = m.group("url").strip()
            if not raw or raw.startswith(("data:", "#", "about:")):
                return m.group(0)
            new = resolver(raw, "img")
            return f'url("{new}")' if new else m.group(0)
        if m.group("set") is not None:
            items = parse_srcset(m.group("set"))
            new_items = []
            for u, d in items:
                new_u = resolver(u, "img") or u
                new_items.append((new_u, d))
            return f"image-set({build_srcset(new_items)})"
        return m.group(0)

    return _CSS_REF_RE.sub(repl, text)


# ---------------------------------------------------------------- srcset

def parse_srcset(value: str) -> list[tuple[str, str]]:
    """'a.jpg 1x, b.jpg 2x' -> [('a.jpg','1x'), ('b.jpg','2x')]"""
    out: list[tuple[str, str]] = []
    i, n = 0, len(value)
    while i < n:
        while i < n and (value[i].isspace() or value[i] == ","):
            i += 1
        if i >= n:
            break
        j = i
        while j < n and not value[j].isspace():
            j += 1
        url, desc = value[i:j], ""
        if url.endswith(","):
            url = url.rstrip(",")
            i = j
        else:
            k = value.find(",", j)
            k = n if k == -1 else k
            desc = value[j:k].strip()
            i = k + 1
        if url:
            out.append((url, desc))
    return out


def build_srcset(items: list[tuple[str, str]]) -> str:
    return ", ".join(f"{u} {d}".strip() for u, d in items)


# ---------------------------------------------------------------- HTML

DROP = object()  # Etiketin tamamen silinmesi için işaret

_ATTR_NAME_RE = re.compile(r"""([^\s"'>/=]+)(?:\s*=\s*(?:"[^"]*"|'[^']*'|[^\s>]+))?""")


class TagHandler(Protocol):
    def on_tag(self, tag: str, attrs: list[tuple[str, str | None]]): ...
    def on_style_text(self, css: str) -> str: ...


class HtmlRewriter(HTMLParser):
    """HTML'i olduğu gibi geri yazar; sadece handler'ın değiştirdiği etiketleri yeniden kurar.

    Değişmeyen etiketler orijinal metinleriyle korunur (SVG'deki viewBox gibi
    büyük/küçük harf duyarlı nitelikler bozulmaz).
    """

    def __init__(self, handler: TagHandler):
        super().__init__(convert_charrefs=False)
        self.h = handler
        self.out: list[str] = []
        self._in_style = False

    def _emit_tag(self, tag, attrs, selfclose):
        raw = self.get_starttag_text() or ""
        result = self.h.on_tag(tag, list(attrs))
        if result is DROP:
            return
        if result is None:
            self.out.append(raw)
        else:
            self.out.append(self._build(raw, tag, result, selfclose))
        if tag == "style" and not selfclose:
            self._in_style = True

    @staticmethod
    def _build(raw: str, tag: str, attrs, selfclose: bool) -> str:
        orig_tag = raw[1 : 1 + len(tag)] if raw[1 : 1 + len(tag)].lower() == tag else tag
        rest = raw[1 + len(tag) :]
        case_map = {m.group(1).lower(): m.group(1) for m in _ATTR_NAME_RE.finditer(rest)}
        parts = [orig_tag]
        for name, value in attrs:
            name = case_map.get(name, name)
            parts.append(name if value is None else f'{name}="{html.escape(value, quote=True)}"')
        return "<" + " ".join(parts) + (" />" if selfclose else ">")

    # --- HTMLParser geri çağrıları
    def handle_starttag(self, tag, attrs):
        self._emit_tag(tag, attrs, False)

    def handle_startendtag(self, tag, attrs):
        self._emit_tag(tag, attrs, True)

    def handle_endtag(self, tag):
        if tag == "style":
            self._in_style = False
        self.out.append(f"</{tag}>")

    def handle_data(self, data):
        self.out.append(self.h.on_style_text(data) if self._in_style else data)

    def handle_entityref(self, name):
        self.out.append(f"&{name};")

    def handle_charref(self, name):
        self.out.append(f"&#{name};")

    def handle_comment(self, data):
        self.out.append(f"<!--{data}-->")

    def handle_decl(self, decl):
        self.out.append(f"<!{decl}>")

    def unknown_decl(self, data):
        self.out.append(f"<![{data}]>")

    def handle_pi(self, data):
        self.out.append(f"<?{data}>")

    def rewrite(self, text: str) -> str:
        self.feed(text)
        self.close()
        return "".join(self.out)


# ---------------------------------------------------------------- Kodlama

_META_CHARSET_RE = re.compile(rb"""<meta[^>]+charset\s*=\s*["']?\s*([\w\-:.]+)""", re.I)


def _lossless_errors(err: UnicodeError):
    """Kodlama hatasında: kaçırılmış ham baytları geri koy, diğerlerini &#NNN; yap."""
    chunk = err.object[err.start : err.end]
    out = bytearray()
    for ch in chunk:
        o = ord(ch)
        if 0xDC80 <= o <= 0xDCFF:
            out.append(o - 0xDC00)
        else:
            out += f"&#{o};".encode("ascii")
    return bytes(out), err.end


codecs.register_error("webclone", _lossless_errors)


def detect_encoding(content: bytes, content_type: str | None) -> str:
    enc = None
    if content_type and "charset=" in content_type.lower():
        enc = content_type.lower().split("charset=")[-1].split(";")[0].strip(" \"'")
    if not enc:
        m = _META_CHARSET_RE.search(content[:4096])
        if m:
            enc = m.group(1).decode("ascii", "ignore")
    try:
        codecs.lookup(enc or "utf-8")
    except LookupError:
        enc = None
    return enc or "utf-8"


def decode(content: bytes, encoding: str) -> str:
    return content.decode(encoding, "surrogateescape")


def encode(text: str, encoding: str) -> bytes:
    return text.encode(encoding, "webclone")
