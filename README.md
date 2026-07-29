# Poké Trivia Battle

A turn-based Pokémon battle game where every attack is earned by answering
Pokémon trivia. Answer right → your Pokémon strikes (harder if you're on a
streak, or the question was hard, and stronger still if it's super
effective). Answer wrong or run out the clock → your opponent hits back and
your combo resets. It's an installable PWA — works fully offline once loaded.

## What's included

- **500 trivia questions** across 8 categories: Types, Type Matchups,
  Evolution, Pokédex numbers, Generations, Legendary/Mythical status,
  Abilities, and general franchise trivia — see `data/questions.json`.
- **Campaign mode**: a 10-stage gauntlet (8 trainers → Elite → Champion
  Mewtwo) with a difficulty curve, ending in a Champion title.
- **Endless mode**: infinite random opponents with an increasing multiplier,
  for a high-score chase.
- 6 playable starters, 19 total Pokémon, an original type-effectiveness
  battle system, streak combos, and a Pokédex-HUD visual style.
- Fully installable PWA (manifest + service worker) that works offline after
  the first load, with save data (progress/stats) stored on-device.

## Running it locally

Service workers require a real HTTP origin — opening `index.html` directly
via `file://` will not register the service worker (the game still works,
it just won't cache for offline use). Serve the folder instead:

```bash
# any static file server works, e.g.:
npx serve .
# or
python3 -m http.server 8080
```

Then open the printed URL (e.g. `http://localhost:8080`) in a browser.

## Installing as an app

Once served over `http://localhost` or a real HTTPS domain, open it in
Chrome/Edge/Safari and use "Add to Home Screen" / "Install App" (or tap the
in-app "Install this app" button on the home screen, which appears once the
browser is ready to prompt).

## Deploying to GitHub Pages

This project needs no build step — it's already set up to deploy as-is
(paths are all relative, so it works whether the site lives at the root of
a domain or in a subfolder like `username.github.io/repo-name/`, and a
`.nojekyll` file is included so GitHub doesn't run it through Jekyll).

1. Create a new repo on GitHub (public or private both work for Pages on
   free accounts, as long as it's public — private repos need GitHub Pro/
   Team/Enterprise to publish Pages).
2. From inside this unzipped folder, push it:
   ```bash
   git init
   git add .
   git commit -m "Poké Trivia Battle"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<repo-name>.git
   git push -u origin main
   ```
3. On GitHub: **Settings → Pages → Build and deployment → Source** →
   "Deploy from a branch" → Branch: `main`, folder `/ (root)` → **Save**.
4. Wait ~1 minute, then visit `https://<your-username>.github.io/<repo-name>/`.

That's it — no CI config needed. Push again any time to update the live site.

## Deploying

This is a fully static site — drop the contents of this folder onto any
static host (GitHub Pages, Netlify, Vercel, Cloudflare Pages, etc.) and it
works as-is. No build step, no server, no dependencies.

## Project structure

```
index.html            Main HTML shell
manifest.json          PWA manifest (icons, theme colors, display mode)
service-worker.js       Offline caching (cache-first for app files)
css/style.css           All styling (Pokédex-HUD theme)
js/pokemon.js           Roster stats, type chart, procedural SVG sprites
js/battle.js            Battle engine (damage, type effectiveness, questions)
js/storage.js           localStorage save/load helpers
js/app.js               Screen navigation, UI wiring, PWA install prompt
data/questions.json     The 500 trivia questions
icons/                  App icons (192, 512, maskable 512)
dev/                    Build/test scripts (not needed to run the game):
  gen_questions.py        Regenerates data/questions.json from the fact DB
  make_icons.py           Regenerates the icon PNGs
  test_logic.js           Headless Node test suite for the battle engine
```

## Customizing / extending

- **Add more questions**: edit `dev/gen_questions.py` (it has a hand-curated
  Pokémon fact database + question templates) and re-run
  `python3 dev/gen_questions.py` from the project root to regenerate
  `data/questions.json`. Or hand-edit `data/questions.json` directly — each
  entry is `{ id, category, difficulty, question, options[4], answer(index) }`.
- **Add/adjust Pokémon**: edit the `ROSTER` array in `js/pokemon.js`. The
  `shape` field picks one of the built-in procedural sprite silhouettes
  (`round`, `winged`, `quad`, `humanoid`, `armored`, `serpent`, `tall`).
- **Rebalance difficulty**: `js/battle.js` has the damage formula and
  `stageDifficultyWeights()`. Re-run `node dev/test_logic.js` after changes —
  it simulates full campaigns and flags negative-HP or infinite-battle bugs.

## Notes on the trivia data

Facts (types, Pokédex numbers, evolutions, generations, abilities) were
hand-verified against well-established, stable Pokémon game data — the
question generator (`dev/gen_questions.py`) keeps a single source-of-truth
fact table so every question is templated from a fact that was actually
checked, rather than freely generated per-question.

## Original artwork note

Battle sprites are original, procedurally-drawn geometric shapes (colored by
type), not reproductions of official Pokémon artwork.
