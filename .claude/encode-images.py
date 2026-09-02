#!/usr/bin/env python3
"""Re-encode the site's photo assets into AVIF + WebP (+ JPEG fallback where the CSS needs one).

Run from the repo root after replacing any source image:  python3 .claude/encode-images.py
Requires Pillow with AVIF/WebP support (the system Python on this machine has both).

The CSS/HTML reference these outputs via image-set(type()) / <picture><source type>; the plain
url()/<img src> fallbacks point at the originals or the *-1920.jpg, so keep the names below stable.
Masters that the page never loads (e.g. hero-group-48.webp) should be stored lossless, not as PNG.
Desktop hero: 1920w for 1x screens, 2752w (native) for >=1.5dppx. Mobile: 1440w hero, 640w cards.
"""
import os
from PIL import Image

AVIF = dict(quality=55, speed=4)
WEBP = dict(quality=80, method=6)
JPEG = dict(quality=82, optimize=True, progressive=True)


def load(path):
    im = Image.open(path)
    im.load()
    return im.convert("RGB") if im.mode != "RGB" else im


def fit(im, width):
    if width is None or im.width <= width:
        return im
    return im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)


def out(im, path, fmt, **kw):
    im.save(path, fmt, **kw)
    print(f"{os.path.getsize(path) / 1024:7.0f} KB  {im.width}x{im.height}  {path}")


def encode(src, base, width=None, jpg=False):
    im = fit(load(src), width)
    out(im, base + ".avif", "AVIF", **AVIF)
    out(im, base + ".webp", "WEBP", **WEBP)
    if jpg:
        out(im, base + ".jpg", "JPEG", **JPEG)


JOBS = [
    # hero, variant A (master: figma-107/hero-group-48.webp — LOSSLESS WebP of the original 2752x1729
    # PNG, pixel-identical at half the size; never referenced by the page itself)
    ("assets/figma-107/hero-group-48.webp", "assets/figma-107/hero-group-48-1920", 1920, True),
    ("assets/figma-107/hero-group-48.webp", "assets/figma-107/hero-group-48-2752", None, False),
    ("assets/figma-107/hero-group-48-mobile.jpg", "assets/figma-107/hero-group-48-mobile-1440", 1440, False),
    # hero, variant B (source: figma-b-test/hero-art.jpg — the JPEG is also the desktop fallback)
    ("assets/figma-b-test/hero-art.jpg", "assets/figma-b-test/hero-art-1920", 1920, False),
    ("assets/figma-b-test/hero-art.jpg", "assets/figma-b-test/hero-art-2752", None, False),
    ("assets/figma-b-test/hero-art.jpg", "assets/figma-b-test/hero-art-mobile-1440", 1440, True),
    # belief cards (<picture>); originals stay as the <img src> fallback
    ("assets/figma-user/belief-p1.png", "assets/figma-user/belief-p1-1400", 1400, False),
    ("assets/figma-user/belief-p2.png", "assets/figma-user/belief-p2-1400", 1400, False),
    ("assets/figma-user/belief-p1-mobile.jpg", "assets/figma-user/belief-p1-mobile-640", 640, False),
    ("assets/figma-user/belief-p2-mobile.jpg", "assets/figma-user/belief-p2-mobile-640", 640, False),
    ("assets/figma-b-test/belief-p2.jpg", "assets/figma-b-test/belief-p2-1400", 1400, False),
    ("assets/figma-b-test/belief-p2.jpg", "assets/figma-b-test/belief-p2-mobile-640", 640, False),
    # join backdrops
    ("assets/figma-105/e86e3c68173afa66a54ad0875bd7020cae6edbf4.png", "assets/figma-105/join-backdrop-a", None, False),
    ("assets/figma-105/join-backdrop-mobile.jpg", "assets/figma-105/join-backdrop-mobile-1080", 1080, False),
    ("assets/figma-b-test/join-backdrop.jpg", "assets/figma-b-test/join-backdrop-1440", None, False),
    # approach stack cards (desktop; the mobile flipbook keeps its JPEG frames)
    *[(f"assets/figma-user/stack-a-{i}.jpg", f"assets/figma-user/stack-a-{i}", None, False) for i in range(1, 5)],
]

if __name__ == "__main__":
    for src, base, width, jpg in JOBS:
        encode(src, base, width, jpg)
