# Offrampt

Crypto in Thailand, and the ways out to baht. Ten exits, each a small site of its own:

The home page leads with the intel (dated notes and trends computed at each build), the calculator,
banking help from Hongdam, Chiang Mai Visa Desk and Mot Dang, and the long view. The menu carries Intel and
four exits; the other six are reference pages, linked from the footer.

## Intel

Notes live in `data/intel/notes/`, one JSON file each, English and Thai; the format and the rules for the words
are in `data/intel/brief.md`. `python3 tools/intel_check.py --all` checks them. `tools/intel_publish.sh <note>`
checks one, builds with every gate, deploys and commits. Pages: `/intel/`, `/intel/<slug>/`, feeds at
`/intel/feed.xml` and `/th/intel/feed.xml`, all notes at `/intel/notes.json`. A build reads the live
notes.json back, so a note already published stays when a checkout without it builds. Services on the home
page come from `data/ours.json`; Hongdam's prices are read from https://hongdam.net/api/services at build.

| Exit | Page | What |
|---|---|---|
| 1 | Tools | off-ramp calculator, address checker, baht converter |
| 2 | Ramp | crypto to baht, by situation: visiting, living here without a Thai bank, banked here |
| 3 | Cards | crypto cards, Thai and foreign exchanges, other rails, wallets |
| 4 | Scams | the numbers, how they work, where to report, cases |
| 5 | Networks | which network, an address checker, stablecoins by chain, fees in baht |
| 6 | Markets | bitcoin and USDT in baht since 2018, the Thai premium, the USDT-to-baht spread |
| 7 | Rules | the SEC decree, licensed operators, blocked platforms, tax, bank accounts and freezes |
| 8 | How | hashing, keys, blocks, mining, stablecoins, the 21 million, with working models |
| 9 | History | 1976 to now, Thai events marked |
| 10 | Words | English and Thai |

**Live:** https://offrampt.net/

## Build

```
python3 tools/fetch.py       # prices and rates into data/raw/ (Bitkub, Binance, BOT, DefiLlama, mempool, CoinGecko)
python3 tools/compute.py     # every number the pages print, into build/facts.json, with checks
python3 tools/draw.py        # the pictures (numpy + Pillow; the Thai one through headless Chrome)
python3 tools/figures.py     # the charts, as inline SVG
./publish.sh                 # all of it, checked, into docs/
./deploy.sh                  # docs/ to Cloudflare Pages, project offrampt
python3 tools/serve.py       # preview on :8861
```

Live figures on the pages come from the `offrampt-rates` worker (Bitkub, CoinGecko and the Bank of
Thailand, every fifteen minutes); the baked figures stand when it cannot be reached.

## Money

`data/money.json` holds receiving addresses and referral links. A null slot renders nothing; a
filled one appears at the next build, with the disclosure beside it. A referral keyed by a route's
`pid` in `data/routes.json` turns that calculator row's Open button into a Sign up link.

## Licence

Text, figures and data CC BY 4.0 (Nan · hongdam.net). Code MIT. See NOTICE.txt.
Nothing here is advice about money, tax or law.
