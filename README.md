# Offrampt

Crypto in Thailand, and the ways out to baht. Ten exits, each a small site of its own:

The home page leads with a financial-access wizard, the existing calculator, local services, and three
interactive cost and resilience tools. Intel, the long view, and research remain available. The menu carries Intel and
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

## Commercial launch

- The homepage wizard selects the calculator's bank filter and amount. A restricted account points to
  the existing resolution guide, not a route around the restriction.
- Existing Hongdam services use their existing purchase pages. Offrampt Landing, Pro and enterprise
  are enquiry-only pilots; do not advertise subscriptions or collect payment until the delivery scope,
  price, fulfilment and checkout are confirmed. Enquiries go to the existing public fleet email.
- Commercial events are dispatched as `offrampt-commercial` and pushed into an existing `dataLayer`
  if one is installed. The payload contains only event and category; no amount, visa or account status.
  An analytics collector and conversion reporting still need configuration.
- Activate approved partner URLs in `data/money.json`; do not use placeholder links. Field testing
  should record provider, date, nationality/visa category, tested capability, evidence and limitations,
  without retaining customer identifiers.
- Run `./publish.sh` (or `./publish.sh --pages` with current build inputs), then `./deploy.sh` from an
  authorized checkout. Confirm English and Thai mobile and desktop rendering, existing calculator
  interaction, checkout links and enquiry email before promotion.
- Next: search-intent landing pages, compact third-party embeds, verified passport/provider matrix,
  subscriptions, attribution and paid-order reconciliation.

## Licence

Text, figures and data CC BY 4.0 (Nan · hongdam.net). Code MIT. See NOTICE.txt.
Nothing here is advice about money, tax or law.
