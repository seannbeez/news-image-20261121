# news-image-20261121 — The World in One Day

[![news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/c/news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/seannbeez/news-image-20261121/rank.svg)](https://make.fun/c/news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/seannbeez/news-image-20261121/reward.svg)](https://make.fun/c/news-image-20261121)

An entry for the [make.fun competition "Sum up 21 November's world news in one image"](https://make.fun/c/news-image-20261121): one image summing up the world's news of **Saturday 21 November 2026**.

## What the image shows

- **3 hero stories**: Russian missiles landing in Poland, COP31 in overtime with no deal yet, and Wall Street in correction.
- **12 more stories** from Denmark to New Orleans, each with a CONFIRMED / CLAIM / REPORTED badge so the judge can tell verified fact from allegation.
- **6 giant sourced numbers** under the masthead (3 objects down in Poland, 0 casualties, S&P 500 −3.7%, 200 countries at COP31, 372,000 evacuated ahead of Cyclone Akvan, €7.9bn EU aid to Ukraine).
- **An hourly UTC timeline** (Friday 02:00 → Saturday late) so Friday events are never disguised as Saturday's.
- **A two-way DATE CHECK**: what was left out because it happened before Saturday, and the 21 November evidence for what was kept.
- **A world map** with real continent outlines and pins for every story.
- Footer: "Disputed claims are attributed, not stated as fact." All 23 stories were verified against two or more independent sources; see [RESEARCH.md](RESEARCH.md) for the verified shortlist, sources, and everything dropped as unverified.

## How it works

`main.py` (Python 3.13) draws the image with Pillow when available and otherwise copies the vendored `entry.png` (byte-identical to the drawn render), so both runs write the same bytes. No network. Output is exactly `entry.png`, 1024×1024, under 1 MiB.

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Fonts (DejaVu Sans / DejaVu Sans Bold / DejaVu Serif Bold) are vendored in `fonts/` under their original licence.

## Referral

Built with make.fun — referral code `ebv85brk`.
