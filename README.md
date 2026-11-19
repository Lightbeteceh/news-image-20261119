# news-image-20261119 — The World in One Day

[![make.fun · news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/Lightbeteceh/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/Lightbeteceh/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261119)

An entry for the [make.fun news-image-20261119 bounty](https://make.fun/bounty/news-image-20261119)
("Sum up 19 November's world news in one image", $250 USDC, 50 places paid).

It sums up the world news of **Thursday 19 November 2026** in a single
picture: 45 stories from 6 continents, led by the first three-way
Trump–Xi–Putin summit in Shenzhen.

## How it works

The picture is an atlas spread, drawn by `render.py` (Python 3 + Pillow,
offline) from the headlines in `stories.json`:

- a dark masthead with the date and the story count;
- a drawn world map with ten numbered pins on the places that mattered
  most (Shenzhen, Kyiv, the Gulf, Gaza, Badme, Antalya, Sydney,
  São Paulo, Washington, London);
- the lead story and the day's market numbers beside the map;
- six continent panels below, each with its own colour tab and
  7–8 headlines.

The Merriweather typefaces are bundled in `fonts/`, so rendering needs
no system fonts and no network. `main.py` then copies `entry.png` to
`/output/entry.png` byte-for-byte.

```sh
python3 render.py   # rebuild entry.png from stories.json (offline)
python3 main.py     # write /output/entry.png (deterministic, no network)
```

## Rules compliance

- Image: PNG, 1024×1024, well under 1 MiB.
- No network at run time (`main.py` only copies a local file).
- Deterministic: two runs of `render.py` and two runs of `main.py`
  produce identical bytes (verified by sha256 — see `EVIDENCE/` in the
  build folder). If a headline ever overflows its panel, `render.py`
  fails loudly instead of clipping text.

## Status

PREP (19 Nov 2026, ~15:30 WIB): repo and pipeline are ready; the draft
image uses early verified headlines from the morning of 19 Nov, while
the news day is still running. The final image — full-day headlines,
re-verified — is rendered on the morning of 20 Nov 2026. Deadline:
21 Nov 2026, 07:00 WIB.
