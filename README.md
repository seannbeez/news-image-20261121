[![make.fun](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/seannbeez/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/seannbeez/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121)

# Saturday 21 November 2026 — The World in One Day (v2)

One image that sums up Saturday 21 November 2026: **35 verified stories** —
3 illustrated heroes, 10 illustrated minis, and 22 more in the
"ALSO ON SATURDAY" list — plus a numbered world map, a Saturday UTC
timeline, a six-number strip, and a two-way DATE CHECK that names the big
Friday stories we deliberately left out.

The day's three heroes are all Saturday: the missile intercepts over
Riyadh, the M6.7 quake in Peru (00:09 UTC), and COP31 running into Day 13
in overtime. Every story on the page was checked against two or more
independent sources; disputed claims are attributed, never stated as fact.
Full sourcing, including everything we dropped and why, is in
[RESEARCH.md](RESEARCH.md).

## How it works

`main.py` draws the whole image in code with Pillow — flat vector shapes
only, no photos, no external images, no network. It writes `entry.png`
(1024×1024, under 1 MiB) to `$MAKEFUN_OUTPUT_DIR` (default `/output`),
deterministically: two runs write identical bytes.

Where Pillow is unavailable (the grading container is stdlib-only), the
program falls back to copying the vendored `entry.png` beside it — the
same image, produced by this same program.

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

Fonts (DejaVu Sans / Bold / Oblique) are vendored in `fonts/`, downloaded
fresh from the matplotlib PyPI wheel during the build.

## Verification

- 300 px downscale inspected: date, numbers strip, heroes and minis read
  at thumbnail size; the one-liner list is a small-print breadth receipt.
- Determinism: two runs from a foreign working directory produce
  byte-identical `entry.png`.
- `makefun check` run against the fresh level-34 kit (see the build report).

Built for the [make.fun bounty](https://make.fun/bounty/news-image-20261121)
— try make.fun yourself: https://make.fun/r/ebv85brk
