#!/usr/bin/env python3
"""Generate a static recipe website from feed.xml."""

import re
import os
import html
from xml.etree import ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).parent

# Unsplash image keywords per recipe guid (slug fragment → keyword string)
IMAGES = {
    "vietnamese-lemongrass-chicken": "vietnamese,noodles,bowl,chicken",
    "moroccan-chickpea-harissa":     "moroccan,stew,chickpea,spices",
    "miso-salmon":                   "salmon,miso,japanese,fish",
    "sicilian-tuna-beans":           "tuna,beans,italian,salad",
    "thai-larb":                     "thai,chicken,salad,herbs",
    "red-lentil-dal":                "lentil,dal,indian,curry",
    "baked-mackerel-tomatoes":       "mackerel,fish,roasted,tomatoes",
    "black-bean-tacos":              "tacos,avocado,beans,mexican",
    "baked-cod-caponata":            "cod,fish,mediterranean,baked",
    "korean-turkey-bowl":            "korean,bowl,rice,vegetables",
    "turkish-red-lentil-soup":       "soup,lentil,turkish,comfort",
    "chicken-chimichurri":           "grilled,chicken,herbs,chimichurri",
    "sardinian-minestrone-farro":    "minestrone,soup,vegetables,italian",
    "lamb-kofta-tabbouleh":          "kofta,lamb,tabbouleh,middle-eastern",
    "ginger-trout-soba":             "soba,noodles,fish,japanese",
}

GRADIENT_FALLBACKS = [
    "linear-gradient(135deg,#f6d365 0%,#fda085 100%)",
    "linear-gradient(135deg,#a1c4fd 0%,#c2e9fb 100%)",
    "linear-gradient(135deg,#d4fc79 0%,#96e6a1 100%)",
    "linear-gradient(135deg,#ffecd2 0%,#fcb69f 100%)",
    "linear-gradient(135deg,#a18cd1 0%,#fbc2eb 100%)",
    "linear-gradient(135deg,#fad0c4 0%,#ffd1ff 100%)",
    "linear-gradient(135deg,#fddb92 0%,#d1fdff 100%)",
    "linear-gradient(135deg,#e0c3fc 0%,#8ec5fc 100%)",
    "linear-gradient(135deg,#f093fb 0%,#f5576c 100%)",
    "linear-gradient(135deg,#4facfe 0%,#00f2fe 100%)",
    "linear-gradient(135deg,#43e97b 0%,#38f9d7 100%)",
    "linear-gradient(135deg,#fa709a 0%,#fee140 100%)",
    "linear-gradient(135deg,#30cfd0 0%,#330867 100%)",
    "linear-gradient(135deg,#a8edea 0%,#fed6e3 100%)",
    "linear-gradient(135deg,#5ee7df 0%,#b490ca 100%)",
]

CSS = """
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Georgia', serif;
  background: #faf9f7;
  color: #2c2c2c;
  line-height: 1.7;
}

/* NAV */
nav {
  background: #1a1a1a;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  position: sticky; top: 0; z-index: 100;
}
nav a { color: #fff; text-decoration: none; font-family: sans-serif; font-size: .9rem; }
nav .brand { font-size: 1.1rem; font-weight: 700; letter-spacing: .5px; }
nav .rss-link {
  border: 1px solid #ff6600; color: #ff6600; padding: 4px 12px;
  border-radius: 20px; font-size: .8rem;
}
nav .rss-link:hover { background: #ff6600; color: #fff; }

/* HERO */
.hero {
  background: #1a1a1a;
  color: #fff;
  text-align: center;
  padding: 5rem 2rem 4rem;
}
.hero h1 { font-size: clamp(2rem, 5vw, 3.5rem); font-weight: 700; margin-bottom: .75rem; }
.hero p { font-size: 1.1rem; opacity: .8; max-width: 600px; margin: 0 auto; }
.tags { margin-top: 1.5rem; display: flex; gap: .5rem; justify-content: center; flex-wrap: wrap; }
.tag {
  background: rgba(255,255,255,.12); border: 1px solid rgba(255,255,255,.25);
  color: #fff; padding: 4px 14px; border-radius: 20px; font-size: .8rem;
  font-family: sans-serif;
}

/* GRID */
.grid-section { max-width: 1200px; margin: 3rem auto; padding: 0 1.5rem; }
.grid-section h2 { font-size: 1.4rem; margin-bottom: 1.5rem; padding-bottom: .5rem; border-bottom: 2px solid #e8e4de; }

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.75rem;
}

/* CARD */
.card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,.07);
  transition: transform .2s, box-shadow .2s;
  text-decoration: none;
  color: inherit;
  display: flex;
  flex-direction: column;
}
.card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,.12); }

.card-img {
  width: 100%; height: 200px;
  object-fit: cover;
  display: block;
}
.card-img-placeholder {
  width: 100%; height: 200px;
  display: flex; align-items: center; justify-content: center;
  font-size: 3rem;
}
.card-body { padding: 1.25rem 1.5rem 1.5rem; flex: 1; display: flex; flex-direction: column; }
.card-day { font-family: sans-serif; font-size: .75rem; text-transform: uppercase; letter-spacing: 1px; color: #888; margin-bottom: .4rem; }
.card-title { font-size: 1.1rem; font-weight: 700; line-height: 1.3; flex: 1; }
.card-date { font-family: sans-serif; font-size: .78rem; color: #aaa; margin-top: .75rem; }

/* RECIPE PAGE */
.recipe-page { max-width: 800px; margin: 0 auto; padding: 2rem 1.5rem 4rem; }

.recipe-hero-img {
  width: 100%; height: 400px; object-fit: cover;
  border-radius: 12px; margin-bottom: 2rem;
  display: block;
}
.recipe-hero-placeholder {
  width: 100%; height: 400px;
  border-radius: 12px; margin-bottom: 2rem;
  display: flex; align-items: center; justify-content: center; font-size: 6rem;
}

.recipe-meta { font-family: sans-serif; font-size: .85rem; color: #888; margin-bottom: .5rem; }
.recipe-title { font-size: clamp(1.6rem, 4vw, 2.4rem); line-height: 1.2; margin-bottom: 1.5rem; }

.recipe-body { font-size: 1.05rem; }
.recipe-body h3 { font-size: 1.2rem; margin: 2rem 0 .75rem; border-bottom: 1px solid #e8e4de; padding-bottom: .4rem; }
.recipe-body ul, .recipe-body ol { padding-left: 1.5rem; }
.recipe-body li { margin-bottom: .4rem; }
.recipe-body p { margin-bottom: 1rem; }
.recipe-body em { color: #555; }
.recipe-body strong { color: #1a1a1a; }

.back-link {
  display: inline-block; margin-bottom: 2rem;
  font-family: sans-serif; font-size: .85rem; color: #555;
  text-decoration: none; padding: 6px 0;
}
.back-link:hover { color: #000; }

footer {
  text-align: center; padding: 2rem; font-family: sans-serif;
  font-size: .8rem; color: #aaa; border-top: 1px solid #e8e4de;
}
"""

NAV_INDEX  = '<nav><a class="brand" href="./">Weekly Menu</a><a class="rss-link" href="feed.xml">RSS Feed</a></nav>'
NAV_RECIPE = '<nav><a class="brand" href="../">Weekly Menu</a><a class="rss-link" href="../feed.xml">RSS Feed</a></nav>'

FOOTER = '<footer>Heart-healthy weekday dinners &mdash; no shellfish, no yoghurt, no eggs.</footer>'


def slug_from_guid(guid: str) -> str:
    parts = guid.split("-")
    # drop "surendra-menu-2026wXX-day-" prefix
    idx = next((i for i, p in enumerate(parts) if p in ("mon","tue","wed","thu","fri")), 3)
    return "-".join(parts[idx+1:])


def image_keyword(guid: str) -> str:
    s = slug_from_guid(guid)
    for key, kw in IMAGES.items():
        if key in s:
            return kw
    return "healthy,food,dinner"


def day_of_week(pub_date: str) -> str:
    return pub_date.split(",")[0] if "," in pub_date else ""


def short_date(pub_date: str) -> str:
    parts = pub_date.strip().split()
    if len(parts) >= 4:
        return f"{parts[1]} {parts[2]} {parts[3]}"
    return pub_date


def parse_feed():
    tree = ET.parse(ROOT / "feed.xml")
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    items = []
    for item in tree.findall(".//item"):
        guid  = item.findtext("guid", "").strip()
        title = item.findtext("title", "").strip()
        pub   = item.findtext("pubDate", "").strip()
        desc  = item.findtext("description", "").strip()
        items.append({"guid": guid, "title": title, "pub": pub, "desc": desc})
    return items


def build_index(items):
    cards = ""
    for i, item in enumerate(items):
        s     = slug_from_guid(item["guid"])
        kw    = image_keyword(item["guid"])
        grad  = GRADIENT_FALLBACKS[i % len(GRADIENT_FALLBACKS)]
        day   = day_of_week(item["pub"])
        date  = short_date(item["pub"])
        # Strip day prefix from display title
        display = re.sub(r"^(Monday|Tuesday|Wednesday|Thursday|Friday)\s+—\s+", "", item["title"])
        cards += f"""
    <a class="card" href="recipes/{s}.html">
      <img class="card-img" src="images/{s}.jpg" alt="{html.escape(display)}"
           onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">
      <div class="card-img-placeholder" style="display:none;background:{grad}">🍽️</div>
      <div class="card-body">
        <div class="card-day">{day}</div>
        <div class="card-title">{html.escape(display)}</div>
        <div class="card-date">{date}</div>
      </div>
    </a>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Weekly Menu</title>
  <style>{CSS}</style>
</head>
<body>
{NAV_INDEX}
<div class="hero">
  <h1>Weekly Menu</h1>
  <p>Heart-healthy weekday dinners. Fresh, flavourful, and good for your heart.</p>
  <div class="tags">
    <span class="tag">❤️ Heart-healthy</span>
    <span class="tag">🚫 No yoghurt</span>
    <span class="tag">🚫 No eggs</span>
    <span class="tag">🚫 No shellfish</span>
  </div>
</div>
<div class="grid-section">
  <h2>All Recipes</h2>
  <div class="grid">{cards}
  </div>
</div>
{FOOTER}
</body>
</html>"""


def build_recipe_page(item, i):
    s     = slug_from_guid(item["guid"])
    kw    = image_keyword(item["guid"])
    grad  = GRADIENT_FALLBACKS[i % len(GRADIENT_FALLBACKS)]
    date  = short_date(item["pub"])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(item["title"])} — Weekly Menu</title>
  <style>{CSS}</style>
</head>
<body>
{NAV_RECIPE}
<div class="recipe-page">
  <a class="back-link" href="../">← All Recipes</a>
  <img class="recipe-hero-img" src="../images/{s}.jpg" alt="{html.escape(item['title'])}"
       onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">
  <div class="recipe-hero-placeholder" style="display:none;background:{grad}">🍽️</div>
  <div class="recipe-meta">{date}</div>
  <h1 class="recipe-title">{html.escape(item["title"])}</h1>
  <div class="recipe-body">
    {item["desc"]}
  </div>
</div>
{FOOTER}
</body>
</html>"""


def main():
    items = parse_feed()

    # Write CSS
    css_dir = ROOT / "css"
    css_dir.mkdir(exist_ok=True)
    (css_dir / "style.css").write_text(CSS)

    # Write index
    (ROOT / "index.html").write_text(build_index(items))
    print(f"Generated index.html ({len(items)} recipes)")

    # Write recipe pages
    recipes_dir = ROOT / "recipes"
    recipes_dir.mkdir(exist_ok=True)
    for i, item in enumerate(items):
        s = slug_from_guid(item["guid"])
        out = recipes_dir / f"{s}.html"
        out.write_text(build_recipe_page(item, i))
        print(f"  Generated recipes/{s}.html")

    # Move feed.xml into recipes/ so the nav link works
    # (actually keep it at root, just update nav link)
    print("Done.")


if __name__ == "__main__":
    main()
