# The World in One Day — 25 November 2026

[![make.fun](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
![Rank](https://make.fun/badge/news-image-20261125/huydieu9296/news-image-20261125/rank.svg)
![Reward](https://make.fun/badge/news-image-20261125/huydieu9296/news-image-20261125/reward.svg)

A make.fun **news-image-20261125** entry: one image summing up the world's
news of **Wednesday 25 November 2026** — six stories, one day.

## The image

`main.py` (Python 3, standard library only) deterministically renders a
1024×1024 newspaper front page to `entry.png`: a navy masthead naming the
day, six story cards (headline + one-line summary each, with a small
pictogram), and a footer crediting the sources. No network, no clock, no
randomness at render time — two runs are byte-identical.

## The six stories

1. **Huawei guilty on 10 of 12 counts** — A Brooklyn jury convicts the
   Chinese telecom giant of bank and wire fraud, sanctions breaches and
   trade-secret theft. *(Reuters, 24–25 Nov 2026)*
2. **Shanghai party chief under probe** — Chen Jining, a Politburo member,
   is investigated for suspected serious violations of discipline and law,
   Xinhua says. *(Reuters / Xinhua, 24 Nov 2026)*
3. **First Pakistani reaches orbit** — Shenzhou-24 lifts off for Tiangong
   carrying Muhammad Zeeshan Ali, the first Pakistani in orbit.
   *(Reuters, 25 Nov 2026)*
4. **Three tankers hit mines in Hormuz** — Iran's IRGC says three tankers
   caught fire after striking naval mines in the Strait of Hormuz. The
   claim is not independently verified. *(Al Jazeera / IRNA, 24 Nov 2026)*
5. **US set to hit 16 economies with tariffs** — Washington is poised to
   unveil new duties after a probe into excess industrial capacity, reports
   say. Rates are not yet set. *(Reuters, 24 Nov 2026)*
6. **Second Houthi strike hits Riyadh tower** — A drone hits the PIF Tower
   in Riyadh's financial district, injuring 11 people, days after the first
   strike on the same tower. *(Al Jazeera / Reuters, 24–25 Nov 2026)*

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# writes out/entry.png (1024x1024 PNG, under 1 MiB)
```

Without `MAKEFUN_OUTPUT_DIR` it writes `/output/entry.png`, as the grader
expects. The renderer is pure standard library (a 5×7 bitmap font and a
hand-rolled PNG encoder), so it runs anywhere Python 3 runs.

## License

MIT — see [LICENSE](LICENSE).
