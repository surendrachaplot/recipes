# Surendra's Weekly Menu — RSS Feed

Heart-healthy weekday dinners. No shellfish. No yoghurt. No eggs.

## Live Feed URL

```
https://YOUR-GITHUB-USERNAME.github.io/healthy-recipes-rss/feed.xml
```

## Setup (one time)

1. Create a new GitHub repo named `healthy-recipes-rss`
2. Push this folder to the `main` branch
3. Go to **Settings → Pages → Source → GitHub Actions**
4. The workflow runs automatically and your feed goes live within 1–2 minutes

## Adding a new recipe

```bash
python scripts/add_recipe.py \
  --title "Monday — Grilled Salmon with Herbs" \
  --date "Mon, 25 May 2026 08:00:00 +0000" \
  --guid "surendra-menu-2026w22-mon-grilled-salmon" \
  --description "<p><em>Serves 2.</em></p><h3>Ingredients</h3><ul><li>...</li></ul>"
```

Then commit and push — GitHub Actions redeploys automatically.

## Subscribe

Paste the feed URL into any RSS reader:
- **Reeder** (iOS/Mac)
- **NetNewsWire** (free, Mac/iOS)
- **Feedly** (web/mobile)
- **Inoreader** (web/mobile)

## Recipe constraints

Every recipe in this feed is:
- Heart-healthy (lean protein, omega-3s, olive oil, legumes, whole grains, plenty of veg)
- Free of yoghurt and eggs
- Free of shellfish
- Low in sodium (using low-sodium stock, soy, and canned goods where possible)
