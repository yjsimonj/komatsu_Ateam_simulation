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

import re

# >>> Paste your Canva view/embed link between the quotes <<<
CANVA_EMBED_URL = ""


def _to_embed(url: str) -> str | None:
    """Normalise any Canva design link to the view?embed form used for iframes.

    Canva view links look like  design/<DESIGN_ID>/<TOKEN>/view?...  — both the
    design id and the token are kept; trailing /view or /edit is dropped and
    /view?embed is appended.
    """
    url = (url or "").strip()
    if not url:
        return None
    m = re.search(r"canva\.com/design/([^/?#]+)(?:/([^/?#]+))?", url)
    if not m:
        return url if "canva.com" in url else None
    parts = ["https://www.canva.com/design", m.group(1)]
    seg2 = m.group(2)
    if seg2 and seg2 not in ("view", "edit", "watch"):
        parts.append(seg2)
    return "/".join(parts) + "/view?embed"


def embed_html() -> str:
    """Responsive, view-only Canva iframe (fullscreen enabled), or a setup hint."""
    src = _to_embed(CANVA_EMBED_URL)
    if not src:
        return (
            "<div style='padding:24px;border:1px dashed #c9a23a;border-radius:10px;"
            "background:#fffbe9;color:#7a5b00;font-size:15px;line-height:1.6;'>"
            "📑 <b>No slides linked yet.</b><br>"
            "Paste your Canva <i>view</i> link into <code>CANVA_EMBED_URL</code> in "
            "<code>ui/slides.py</code>.<br>"
            "In Canva: <b>Share → set \"Anyone with the link → Can view\" → copy the "
            "link</b> (editing stays disabled for viewers)."
            "</div>"
        )
    return (
        "<div style='position:relative;width:100%;height:0;padding-top:62%;"
        "box-shadow:0 2px 12px rgba(0,0,0,0.14);border-radius:10px;overflow:hidden;'>"
        f"<iframe src='{src}' loading='lazy' "
        "style='position:absolute;top:0;left:0;width:100%;height:100%;border:none;' "
        "allowfullscreen='allowfullscreen' allow='fullscreen'></iframe>"
        "</div>"
        "<p style='font-size:13px;color:#666;margin-top:8px;'>"
        "← → 화살표로 넘기고, 우하단 전체화면 버튼으로 확대하세요. (보기 전용 · 편집 불가)"
        "</p>"
    )
