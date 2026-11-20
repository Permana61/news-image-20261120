# World News 20 November 2026

[![make.fun](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120)
[![Rank](https://make.fun/badge/news-image-20261120/Permana61/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120)
[![Reward](https://make.fun/badge/news-image-20261120/Permana61/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120)

An entry for the make.fun competition
[news-image-20261120](https://make.fun/bounty/news-image-20261120) —
"Sum up 20 November's world news in one image".

A stdlib-only Python program (`main.py`, no third-party dependencies)
draws a 1024×1024 infographic summarising six world-news stories from
Friday 20 November 2026.

## The six stories

1. **Russian missiles hit Kyiv** — Russian ballistic missiles struck Kyiv
   overnight; a fire broke out in a 3-storey building in the Obolonskyi
   district, according to mayor Klitschko.
2. **COP31 closes in Antalya** — The climate summit closes with a draft
   deal that drops fossil-fuel language and is the first summit text to
   admit the 1.5°C goal will be missed.
3. **Cyclone Akvan landfall near Gopalpur, Odisha** — The severe cyclonic
   storm makes landfall with winds of 90–100 km/h gusting to 110 km/h,
   after nearly 300,000 people were evacuated.
4. **Two tankers hit mines in the Strait of Hormuz** — Two oil tankers
   struck naval mines, Iran's Revolutionary Guards Navy said, pushing
   oil prices higher.
5. **CGIL 24-hour general strike across Italy** — Italy's largest union
   calls a nationwide strike against the 2027 budget law, with marches
   in about 100 towns and cities and public transport disrupted.
6. **Taiwan short-selling curbs take effect** — New curbs take effect
   after the Taiex plunged 4.4% the day before; stocks closing down 3.5%
   or more cannot be shorted below that close the next day.

## How to run

```sh
python3 main.py
```

This writes `entry.png` to `$MAKEFUN_OUTPUT_DIR` if set, otherwise to
`/output`.

## How the image is built

`main.py` uses only the Python standard library (`zlib` and `struct`
for PNG encoding). It draws the infographic pixel by pixel: a dark
newsprint-style background, a masthead with the date, and six panels —
one per story — each with a headline, a short summary line, and a
small hand-drawn icon. No external fonts, images, or packages are
needed, so the script runs anywhere Python 3 is installed.

## Sources

The stories were verified against reporting published on 20 November
2026 (Reuters, UN News, IMD via The Daily Jagran, LaPresse). Only
events that happened, or were first reported, on Friday 20 November
2026 are included.

## License

MIT — see [LICENSE](LICENSE).
