#!/usr/bin/env python3
"""Download food images from Unsplash CDN for each recipe."""
import urllib.request
import os
from pathlib import Path

ROOT = Path(__file__).parent.parent
IMG_DIR = ROOT / "images"
IMG_DIR.mkdir(exist_ok=True)

# Specific Unsplash photo IDs paired to each recipe slug
PHOTOS = {
    "vietnamese-lemongrass-chicken": "1569050467447-ce54b3bbc37d",  # noodle bowl
    "moroccan-chickpea-harissa":     "1547592166-23ac45744acd",     # moroccan stew
    "miso-salmon":                   "1467003909585-2f8a72700288",  # salmon fillet
    "sicilian-tuna-beans":           "1529692236671-f1f6cf9683ba",  # bean salad
    "thai-larb":                     "1562802378-063ec186a863",     # thai salad
    "red-lentil-dal":                "1585937421612-70a008356fbe",  # lentil dal
    "baked-mackerel-tomatoes":       "1519708227418-c8fd9a32b7a2",  # fish dish
    "black-bean-tacos":              "1565299585323-38d6b0865b47",  # tacos
    "baked-cod-caponata":            "1476224203421-9ac39bcb3327",  # baked fish
    "korean-turkey-bowl":            "1498654896293-37aacf113fd9",  # rice bowl
    "turkish-red-lentil-soup":       "1547592180-85f173990554",     # soup bowl
    "chicken-chimichurri":           "1598515214211-89d3c73ae83b",  # grilled chicken
    "sardinian-minestrone-farro":    "1534939561116-0fcd8b589e16",  # minestrone
    "lamb-kofta-tabbouleh":          "1529042410759-befb1204b468",  # middle eastern
    "ginger-trout-soba":             "1557872943-16a5ac26437e",     # noodle bowl
}

BASE = "https://images.unsplash.com/photo-{id}?w=900&h=500&q=80&auto=format&fit=crop"

for slug, photo_id in PHOTOS.items():
    dest = IMG_DIR / f"{slug}.jpg"
    if dest.exists():
        print(f"  skip {slug}.jpg (exists)")
        continue
    url = BASE.format(id=photo_id)
    try:
        urllib.request.urlretrieve(url, dest)
        size = dest.stat().st_size // 1024
        print(f"  {slug}.jpg  ({size}KB)")
    except Exception as e:
        print(f"  FAILED {slug}: {e}")

print("Done.")
