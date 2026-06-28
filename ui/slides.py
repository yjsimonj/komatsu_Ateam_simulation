"""Slides page — embed a Canva presentation in view-only mode.

Paste your Canva *view* link into CANVA_EMBED_URL below. The page shows the deck
in Canva's embedded viewer: visitors can click through slides and go fullscreen
(zoom), but they cannot edit it.

How to get the link (and set permissions) in Canva:
  1. Open your design → top-right **Share**.
  2. Under "Collaboration link" (or "Public view link") set access to
     **Anyone with the link → Can view**.
  3. Either copy that view link directly, OR use **Share → More → Embed** and
     copy the link it gives.
  4. Paste it into CANVA_EMBED_URL below (any of these forms works):
       https://www.canva.com/design/DAFxxxxxxxx/view
       https://www.canva.com/design/DAFxxxxxxxx/view?utm_content=...
       https://www.canva.com/design/DAFxxxxxxxx/xxxx/view?embed
"""

from __future__ import annotations

import os
import re
import urllib.request

# Default Canva link. You usually don't need to touch this — to change the deck
# WITHOUT editing code, set the CANVA_EMBED_URL **environment variable**:
#   Hugging Face Space → Settings → "Variables and secrets" → New variable
#   name = CANVA_EMBED_URL, value = your Canva view link. (No commit needed.)
# The env var, if set, overrides the value below.
CANVA_EMBED_URL = "https://www.canva.com/design/DAHNzzW7u0Y/MfiAERgN0uuu-jdszorX0Q/edit"


def _source_url() -> str:
    """The active Canva link: env var wins, else the constant above."""
    return (os.environ.get("CANVA_EMBED_URL") or CANVA_EMBED_URL or "").strip()


_resolved: dict[str, str] = {}


def _expand(url: str) -> str:
    """Follow short links (e.g. canva.link/…) to the real canva.com/design URL."""
    if "canva.com/design" in url:
        return url
    if url in _resolved:
        return _resolved[url]
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=6) as r:
            final = r.geturl()
    except Exception:
        final = url
    _resolved[url] = final
    return final


def _to_embed(url: str) -> str | None:
    """Normalise any Canva design link to the view?embed form used for iframes.

    Canva view links look like  design/<DESIGN_ID>/<TOKEN>/view?...  — both the
    design id and the token are kept; trailing /view or /edit is dropped and
    /view?embed is appended.
    """
    url = (url or "").strip()
    if not url:
        return None
    url = _expand(url)
    m = re.search(r"canva\.com/design/([^/?#]+)(?:/([^/?#]+))?", url)
    if not m:
        return url if "canva" in url else None
    parts = ["https://www.canva.com/design", m.group(1)]
    seg2 = m.group(2)
    if seg2 and seg2 not in ("view", "edit", "watch"):
        parts.append(seg2)
    return "/".join(parts) + "/view?embed"


def embed_html() -> str:
    """Responsive, view-only Canva iframe (fullscreen enabled), or a setup hint."""
    src = _to_embed(_source_url())
    if not src:
        return (
            "<div style='padding:24px;border:1px dashed #c9a23a;border-radius:10px;"
            "background:#fffbe9;color:#7a5b00;font-size:15px;line-height:1.6;'>"
            "📑 <b>No slides linked yet.</b><br>"
            "Set the <code>CANVA_EMBED_URL</code> variable (Space → Settings → "
            "Variables) or edit it in <code>ui/slides.py</code>.<br>"
            "In Canva: <b>Share → set \"Anyone with the link → Can view\" → copy the "
            "link</b> (editing stays disabled for viewers)."
            "</div>"
        )
    raw = _source_url()
    return (
        "<div style='position:relative;width:100%;height:0;padding-top:62%;"
        "box-shadow:0 2px 12px rgba(0,0,0,0.14);border-radius:10px;overflow:hidden;'>"
        f"<iframe src='{src}' loading='lazy' "
        "style='position:absolute;top:0;left:0;width:100%;height:100%;border:none;' "
        "allowfullscreen='allowfullscreen' allow='fullscreen'></iframe>"
        "</div>"
        "<p style='font-size:13px;color:#666;margin-top:8px;'>"
        "← → 화살표로 넘기고, 우하단 전체화면 버튼으로 확대하세요. (보기 전용 · 편집 불가) · "
        f"<a href='{raw}' target='_blank' rel='noopener'>슬라이드가 안 보이면 새 탭에서 열기 ↗</a>"
        "</p>"
    )
