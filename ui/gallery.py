"""Gallery page — show photos & videos the user drops into a folder.

Put your images and clips into the `gallery/` folder at the repo root (create
sub-folders if you like — they are scanned recursively). The Gallery tab lists
every image in a grid and lets you play any video from a dropdown. Press
**Refresh** after adding new files.

On Hugging Face Spaces the files must be committed to the repo; large media is
stored via git-lfs (see .gitattributes).
"""

from __future__ import annotations

import os

# Folder scanned for media. Rename here if you want a different folder name.
GALLERY_DIR_NAME = "gallery"
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GALLERY_DIR = os.path.join(_REPO_ROOT, GALLERY_DIR_NAME)

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
VIDEO_EXTS = {".mp4", ".mov", ".webm", ".m4v", ".ogg"}


def _scan(exts: set[str]) -> list[str]:
    """Return sorted absolute paths of files under GALLERY_DIR with given exts."""
    if not os.path.isdir(GALLERY_DIR):
        return []
    out = []
    for root, _dirs, files in os.walk(GALLERY_DIR):
        for f in files:
            if os.path.splitext(f)[1].lower() in exts:
                out.append(os.path.join(root, f))
    return sorted(out)


def list_images() -> list[str]:
    return _scan(IMAGE_EXTS)


def list_videos() -> list[str]:
    return _scan(VIDEO_EXTS)


def _rel(path: str) -> str:
    """Short label = path relative to the gallery folder."""
    return os.path.relpath(path, GALLERY_DIR)


def gallery_value() -> list[tuple[str, str]]:
    """(image_path, caption) pairs for gr.Gallery."""
    return [(p, _rel(p)) for p in list_images()]


def video_choices() -> list[tuple[str, str]]:
    """(label, value=path) pairs for a gr.Dropdown of videos."""
    return [(_rel(p), p) for p in list_videos()]


def status_md() -> str:
    n_img, n_vid = len(list_images()), len(list_videos())
    if not os.path.isdir(GALLERY_DIR):
        return (f"<sub>No `{GALLERY_DIR_NAME}/` folder yet — create it at the repo "
                f"root and drop images/videos in.</sub>")
    if n_img == 0 and n_vid == 0:
        return (f"<sub>`{GALLERY_DIR_NAME}/` is empty. Drop images "
                f"({', '.join(sorted(IMAGE_EXTS))}) or videos "
                f"({', '.join(sorted(VIDEO_EXTS))}) in, then press Refresh.</sub>")
    return f"<sub>Found **{n_img}** image(s) and **{n_vid}** video(s) in `{GALLERY_DIR_NAME}/`.</sub>"
