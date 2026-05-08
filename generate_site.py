#!/usr/bin/env python3
"""Generate a simple text-only static recipe website from feed.xml."""

import re
from xml.etree import ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).parent

CSS = """
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: Georgia, serif; max-width: 720px; margin: 0 auto; padding: 2rem 1.5rem 4rem; color: #222; line-height: 1.75; background: #fff; }
nav { margin-bottom: 2.5rem; padding-bottom: 1rem; border-bottom: 1px solid #ddd; display: flex; justify-content: space-between; align-items: baseline; }
nav .brand { font-size: 1.1rem; font-weight: bold; text-decoration: none; color: #222; }
nav .rss { font-size: .85rem; color: #888; text-decoration: none; }
nav .rss:hover { color: #c30; }
h1 { font-size: 1.6rem; margin-bottom: .25rem; }
.subtitle { color: #666; font-size: .95rem; margin-bottom: 2rem; }
ul.recipe-list { list-style: none; }
ul.recipe-list li { padding: .75rem 0; border-bottom: 1px solid #eee; display: flex; align-items: center; gap: 1rem; }
ul.recipe-list li:last-child { border-bottom: none; }
ul.recipe-list .thumb { width: 64px; height: 64px; object-fit: cover; border-radius: 6px; flex-shrink: 0; background: #eee; }
ul.recipe-list .meta { flex: 1; min-width: 0; }
ul.recipe-list a { text-decoration: none; color: #222; font-size: 1.05rem; }
ul.recipe-list a:hover { text-decoration: underline; color: #c30; }
.date { display: block; font-size: .8rem; color: #aaa; margin-top: .1rem; }
.back { display: inline-block; margin-bottom: 2rem; font-size: .9rem; color: #888; text-decoration: none; }
.back:hover { color: #222; }
h2 { font-size: 1.5rem; margin-bottom: .25rem; }
.recipe-date { font-size: .85rem; color: #888; margin-bottom: 1.5rem; }
.recipe-hero { width: 100%; max-height: 380px; object-fit: cover; border-radius: 8px; margin-bottom: 2rem; display: block; }
.recipe-body h3 { font-size: 1.1rem; margin: 1.75rem 0 .6rem; }
.recipe-body ul, .recipe-body ol { padding-left: 1.4rem; }
.recipe-body li { margin-bottom: .35rem; }
.recipe-body p { margin-bottom: .9rem; }
.recipe-body em { color: #555; }
footer { margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #ddd; font-size: .8rem; color: #aaa; }
"""


def strip_day(title: str) -> str:
    return re.sub(r"^(Monday|Tuesday|Wednesday|Thursday|Friday)\s+—\s+", "", title)


def slug_from_guid(guid: str) -> str:
    parts = guid.split("-")
    idx = next((i for i, p in enumerate(parts) if p in ("mon","tue","wed","thu","fri")), 3)
    return "-".join(parts[idx+1:])


def short_date(pub_date: str) -> str:
    parts = pub_date.strip().split()
    return f"{parts[1]} {parts[2]} {parts[3]}" if len(parts) >= 4 else pub_date


def parse_feed():
    tree = ET.parse(ROOT / "feed.xml")
    items = []
    for item in tree.findall(".//item"):
        items.append({
            "guid":  item.findtext("guid", "").strip(),
            "title": item.findtext("title", "").strip(),
            "pub":   item.findtext("pubDate", "").strip(),
            "desc":  item.findtext("description", "").strip(),
        })
    return items


def has_image(slug: str) -> bool:
    return (ROOT / "images" / f"{slug}.jpg").exists()


def build_index(items):
    rows = ""
    for item in reversed(items):
        s    = slug_from_guid(item["guid"])
        date = short_date(item["pub"])
        img  = f'<img class="thumb" src="images/{s}.jpg" alt="" loading="lazy">' if has_image(s) else ''
        rows += f'  <li>{img}<div class="meta"><a href="recipes/{s}.html">{strip_day(item["title"])}</a><span class="date">{date}</span></div></li>\n'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Recipe List</title>
  <style>{CSS}</style>
</head>
<body>
  <nav>
    <a class="brand" href="./">Recipe List</a>
    <a class="rss" href="feed.xml">RSS Feed</a>
  </nav>
  <ul class="recipe-list">
{rows}  </ul>
</body>
</html>"""


def build_recipe_page(item):
    s    = slug_from_guid(item["guid"])
    date = short_date(item["pub"])
    hero = f'<img class="recipe-hero" src="../images/{s}.jpg" alt="{strip_day(item["title"])}">' if has_image(s) else ''
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{strip_day(item["title"])} — Recipe List</title>
  <style>{CSS}</style>
</head>
<body>
  <nav>
    <a class="brand" href="../">Recipe List</a>
    <a class="rss" href="../feed.xml">RSS Feed</a>
  </nav>
  <a class="back" href="../">← All Recipes</a>
  {hero}
  <h2>{strip_day(item["title"])}</h2>
  <p class="recipe-date">{date}</p>
  <div class="recipe-body">
    {item["desc"]}
  </div>
</body>
</html>"""


def main():
    items = parse_feed()

    (ROOT / "index.html").write_text(build_index(items))
    print(f"Generated index.html ({len(items)} recipes)")

    recipes_dir = ROOT / "recipes"
    recipes_dir.mkdir(exist_ok=True)
    for item in items:
        s   = slug_from_guid(item["guid"])
        out = recipes_dir / f"{s}.html"
        out.write_text(build_recipe_page(item))
        print(f"  {s}.html")

    print("Done.")


if __name__ == "__main__":
    main()
