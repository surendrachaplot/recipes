#!/usr/bin/env python3
"""
Add a new recipe item to feed.xml.

Usage:
    python scripts/add_recipe.py \
        --title "Monday — Grilled Salmon" \
        --date "Mon, 25 May 2026 08:00:00 +0000" \
        --guid "surendra-menu-2026w22-mon-grilled-salmon" \
        --description "<p>Recipe HTML here...</p>"
"""

import argparse
import re
import sys
from pathlib import Path

FEED_PATH = Path(__file__).parent.parent / "feed.xml"


def main():
    parser = argparse.ArgumentParser(description="Add a recipe to feed.xml")
    parser.add_argument("--title", required=True)
    parser.add_argument("--date", required=True, help="RFC 2822 date e.g. 'Mon, 25 May 2026 08:00:00 +0000'")
    parser.add_argument("--guid", required=True, help="Unique ID e.g. surendra-menu-2026w22-mon-dish-name")
    parser.add_argument("--description", required=True, help="HTML content for the recipe (will be wrapped in CDATA)")
    parser.add_argument("--category", default="Dinner")
    args = parser.parse_args()

    feed = FEED_PATH.read_text(encoding="utf-8")

    new_item = f"""
    <item>
      <title>{args.title}</title>
      <pubDate>{args.date}</pubDate>
      <guid isPermaLink="false">{args.guid}</guid>
      <category>{args.category}</category>
      <description><![CDATA[
        {args.description}
      ]]></description>
    </item>
"""

    insert_before = "  </channel>"
    if insert_before not in feed:
        print("ERROR: Could not find </channel> closing tag in feed.xml", file=sys.stderr)
        sys.exit(1)

    updated = feed.replace(insert_before, new_item + insert_before, 1)

    # Update lastBuildDate
    from datetime import datetime, timezone
    now_rfc = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")
    updated = re.sub(
        r"<lastBuildDate>.*?</lastBuildDate>",
        f"<lastBuildDate>{now_rfc}</lastBuildDate>",
        updated,
    )

    FEED_PATH.write_text(updated, encoding="utf-8")
    print(f"Added recipe: {args.title}")
    print(f"Feed updated: {FEED_PATH}")


if __name__ == "__main__":
    main()
