"""Gallery page — show photos & videos from a Hugging Face Dataset repo.

Media lives in a separate **HF Dataset** repo (not in this app repo), so the app
stays small and the media can grow freely. Upload your photos/clips to that
dataset via the HF website (drag & drop) — no git needed.

  DATASET_REPO  ←  set this to your dataset, e.g. "yjsimonj/komatsu-media"

How it loads (public dataset → no token needed):
  • images are downloaded eagerly (they are small) and shown in a grid,
  • videos are listed by name and downloaded only when you pick one to play.

Local fallback: if the dataset can't be reached (e.g. offline, or not created
yet), it falls back to scanning a local `gallery/` folder at the repo root.
"""

from __future__ import annotations

import os

# >>> Hugging Face Dataset repo id holding the media <<<
DATASET_REPO = "yjsimonj/gallery"

# Local fallback folder (used only when the dataset is unreachable).
GALLERY_DIR_NAME = "gallery"
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GALLERY_DIR = os.path.join(_REPO_ROOT, GALLERY_DIR_NAME)

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
VIDEO_EXTS = {".mp4", ".mov", ".webm", ".m4v", ".ogg"}

_HF_PREFIX = "hf::"   # marks a dropdown value that must be fetched from the dataset


def _ext(name: str) -> str:
    return os.path.splitext(name)[1].lower()


# ---------------------------------------------------------------------------
# Remote (HF Dataset) access — cached list, lazy per-file download
# ---------------------------------------------------------------------------
def _remote_files() -> list[str] | None:
    """All file names in the dataset, or None if unreachable/not configured."""
    if not DATASET_REPO or "/" not in DATASET_REPO:
        return None
    try:
        from huggingface_hub import list_repo_files
        return list_repo_files(DATASET_REPO, repo_type="dataset")
    except Exception:
        return None


def _download(name: str) -> str | None:
    try:
        from huggingface_hub import hf_hub_download
        return hf_hub_download(DATASET_REPO, name, repo_type="dataset")
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Local fallback
# ---------------------------------------------------------------------------
def _scan_local(exts: set[str]) -> list[str]:
    if not os.path.isdir(GALLERY_DIR):
        return []
    out = []
    for root, _dirs, files in os.walk(GALLERY_DIR):
        for f in files:
            if _ext(f) in exts:
                out.append(os.path.join(root, f))
    return sorted(out)


# ---------------------------------------------------------------------------
# Public API used by the app
# ---------------------------------------------------------------------------
def _using_remote() -> bool:
    return _remote_files() is not None


def gallery_value() -> list[tuple[str, str]]:
    """(image_path, caption) for gr.Gallery. Images are downloaded eagerly."""
    files = _remote_files()
    if files is not None:
        out = []
        for f in sorted(files):
            if _ext(f) in IMAGE_EXTS:
                p = _download(f)
                if p:
                    out.append((p, os.path.basename(f)))
        return out
    return [(p, os.path.relpath(p, GALLERY_DIR)) for p in _scan_local(IMAGE_EXTS)]


def video_choices() -> list[tuple[str, str]]:
    """(label, value) for a gr.Dropdown. Remote values are tagged so they are
    fetched on demand; local values are direct file paths."""
    files = _remote_files()
    if files is not None:
        return [(os.path.basename(f), _HF_PREFIX + f)
                for f in sorted(files) if _ext(f) in VIDEO_EXTS]
    return [(os.path.relpath(p, GALLERY_DIR), p) for p in _scan_local(VIDEO_EXTS)]


def resolve_video(value: str | None) -> str | None:
    """Turn a dropdown value into a local playable path (downloading if remote)."""
    if not value:
        return None
    if value.startswith(_HF_PREFIX):
        return _download(value[len(_HF_PREFIX):])
    return value


def allowed_media_paths() -> list[str]:
    """Folders Gradio must be allowed to serve files from: the local gallery
    folder and the huggingface_hub download cache (where videos/images land)."""
    paths = [GALLERY_DIR]
    try:
        from huggingface_hub import constants
        paths.append(constants.HF_HUB_CACHE)
    except Exception:
        paths.append(os.path.expanduser("~/.cache/huggingface/hub"))
    return [p for p in paths if p]


def status_md() -> str:
    files = _remote_files()
    if files is not None:
        n_img = sum(1 for f in files if _ext(f) in IMAGE_EXTS)
        n_vid = sum(1 for f in files if _ext(f) in VIDEO_EXTS)
        if n_img == 0 and n_vid == 0:
            return (f"<sub>Connected to dataset **{DATASET_REPO}**, but it has no "
                    f"media yet. Upload images/videos there, then press Refresh.</sub>")
        return (f"<sub>From dataset **{DATASET_REPO}**: **{n_img}** image(s), "
                f"**{n_vid}** video(s). Videos download when you pick one.</sub>")
    # local fallback
    n_img, n_vid = len(_scan_local(IMAGE_EXTS)), len(_scan_local(VIDEO_EXTS))
    if n_img == 0 and n_vid == 0:
        return (f"<sub>Dataset `{DATASET_REPO}` unreachable and local "
                f"`{GALLERY_DIR_NAME}/` is empty.</sub>")
    return (f"<sub>Dataset unreachable — showing local `{GALLERY_DIR_NAME}/`: "
            f"**{n_img}** image(s), **{n_vid}** video(s).</sub>")
