# -*- coding: utf-8 -*-
"""fetch.py — pull the raw series the site is drawn from, into data/raw/.

    python3 tools/fetch.py            # fetch what is missing or older than a day
    python3 tools/fetch.py --all      # refetch everything

Sources (all public; two keyed, keys read from ~/.config/nanobotco/keys.json):
  Bitkub tradingview history  — daily BTC/THB, ETH/THB, USDT/THB since 2018 (licensed Thai exchange)
  Bitkub v3 ticker            — every THB pair, now
  Binance public data API     — daily BTCUSDT, ETHUSDT since 2017 (global price)
  Bank of Thailand API        — daily USD/THB reference, bank buying/selling (31-day windows)
  DefiLlama stablecoins       — stablecoin supply by chain, now and history
  mempool.space               — bitcoin block fee rates
  CoinGecko (demo key)        — top coins by market cap, priced in THB
"""
import json, os, sys, time, datetime as dt, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
os.makedirs(RAW, exist_ok=True)
KEYS = json.load(open(os.path.expanduser("~/.config/nanobotco/keys.json")))
UA = {"User-Agent": "offrampt.net data build (hello@offrampt.net)"}
FORCE = "--all" in sys.argv


def get(url, headers=None, tries=3):
    h = dict(UA); h.update(headers or {})
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=40) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 502, 503, 504) and i < tries - 1:
                time.sleep(4 * (i + 1)); continue
            raise
        except Exception:
            if i < tries - 1:
                time.sleep(3); continue
            raise


def fresh(name, hours=20):
    p = os.path.join(RAW, name)
    return (not FORCE) and os.path.exists(p) and (time.time() - os.path.getmtime(p)) < hours * 3600


def save(name, obj, src):
    obj = {"source": src, "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "data": obj}
    json.dump(obj, open(os.path.join(RAW, name), "w"), separators=(",", ":"))
    print("  ", name, "ok")


def bitkub_history():
    now = int(time.time())
    for sym in ("BTC_THB", "ETH_THB", "USDT_THB", "USDC_THB", "SOL_THB", "XRP_THB", "KUB_THB"):
        name = "bitkub_%s.json" % sym.lower()
        if fresh(name): continue
        d = get("https://api.bitkub.com/tradingview/history?symbol=%s&resolution=1D&from=1420070400&to=%d" % (sym, now))
        if d.get("s") != "ok":
            print("  ", sym, "no data"); continue
        rows = [[dt.datetime.utcfromtimestamp(t).strftime("%Y-%m-%d"), o, h, l, c, v]
                for t, o, h, l, c, v in zip(d["t"], d["o"], d["h"], d["l"], d["c"], d["v"])]
        save(name, rows, "Bitkub tradingview/history, resolution 1D, " + sym)


def bitkub_ticker():
    if fresh("bitkub_ticker.json", 1): return
    save("bitkub_ticker.json", get("https://api.bitkub.com/api/v3/market/ticker"), "Bitkub api/v3/market/ticker")


def binance_history():
    for sym in ("BTCUSDT", "ETHUSDT"):
        name = "binance_%s.json" % sym.lower()
        if fresh(name): continue
        rows, start = [], 1502928000000
        while True:
            k = get("https://data-api.binance.vision/api/v3/klines?symbol=%s&interval=1d&startTime=%d&limit=1000" % (sym, start))
            if not k: break
            for r in k:
                rows.append([dt.datetime.utcfromtimestamp(r[0] / 1000).strftime("%Y-%m-%d"),
                             float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[5])])
            if len(k) < 1000: break
            start = k[-1][0] + 86400000
            time.sleep(0.3)
        save(name, rows, "Binance data-api.binance.vision klines 1d " + sym)


def bot_fx():
    """Daily USD/THB from the Bank of Thailand, 31 days a call. Appends to what is on disk."""
    name = "bot_usd_thb.json"
    p = os.path.join(RAW, name)
    have = json.load(open(p))["data"] if os.path.exists(p) else []
    by = {r["period"]: r for r in have}
    tok = KEYS["bot_api"]["token"]
    start = dt.date(2017, 8, 1)
    if have:
        start = dt.date.fromisoformat(max(by)) - dt.timedelta(days=7)
    end = dt.date.today()
    if fresh(name) and have: return
    d0 = start
    n = 0
    while d0 <= end:
        d1 = min(d0 + dt.timedelta(days=30), end)
        url = ("https://gateway.api.bot.or.th/Stat-ExchangeRate/v2/DAILY_AVG_EXG_RATE/"
               "?start_period=%s&end_period=%s&currency=USD" % (d0, d1))
        try:
            d = get(url, {"Authorization": tok})
            for r in d["result"]["data"]["data_detail"]:
                if r.get("mid_rate"):
                    by[r["period"]] = {k: r.get(k) for k in ("period", "buying_sight", "buying_transfer", "selling", "mid_rate")}
        except Exception as e:
            print("   BOT", d0, "failed:", e)
        d0 = d1 + dt.timedelta(days=1)
        n += 1
        time.sleep(0.25)
    rows = [by[k] for k in sorted(by)]
    save(name, rows, "Bank of Thailand API Stat-ExchangeRate v2 DAILY_AVG_EXG_RATE, USD (%d calls)" % n)


def stablecoins():
    if not fresh("llama_stablecoins.json"):
        save("llama_stablecoins.json", get("https://stablecoins.llama.fi/stablecoins?includePrices=true"),
             "DefiLlama stablecoins.llama.fi/stablecoins")
    if not fresh("llama_stable_total.json"):
        save("llama_stable_total.json", get("https://stablecoins.llama.fi/stablecoincharts/all"),
             "DefiLlama stablecoins.llama.fi/stablecoincharts/all")
    for sid, sym in (("1", "usdt"), ("2", "usdc")):
        name = "llama_%s_chains.json" % sym
        if fresh(name): continue
        d = get("https://stablecoins.llama.fi/stablecoin/" + sid)
        keep = {}
        for chain, v in d.get("chainBalances", {}).items():
            tok = v.get("tokens", [])
            keep[chain] = [[t["date"], (t.get("circulating") or {}).get("peggedUSD", 0)] for t in tok[::7]] + \
                          ([[tok[-1]["date"], (tok[-1].get("circulating") or {}).get("peggedUSD", 0)]] if tok else [])
        save(name, keep, "DefiLlama stablecoins.llama.fi/stablecoin/" + sid + " (weekly sample)")


def mempool():
    if fresh("mempool_fees.json"): return
    for period in ("all", "3y"):
        try:
            d = get("https://mempool.space/api/v1/mining/blocks/fee-rates/" + period)
            if d:
                save("mempool_fees.json", d, "mempool.space /api/v1/mining/blocks/fee-rates/" + period); return
        except Exception as e:
            print("   mempool", period, e)


def hashrate():
    if not fresh("mempool_hashrate.json"):
        save("mempool_hashrate.json", get("https://mempool.space/api/v1/mining/hashrate/1m"), "mempool.space /api/v1/mining/hashrate/1m")
    if not fresh("mempool_hashrate_3y.json", hours=72):  # the intel page's doubling time
        save("mempool_hashrate_3y.json", get("https://mempool.space/api/v1/mining/hashrate/3y"), "mempool.space /api/v1/mining/hashrate/3y")


def coingecko():
    if fresh("cg_markets.json", 6): return
    k = KEYS["coingecko_demo"]
    d = get(k["base"] + "/coins/markets?vs_currency=thb&order=market_cap_desc&per_page=100&page=1&price_change_percentage=24h,7d,1y",
            {k["header"]: k["key"]})
    save("cg_markets.json", d, "CoinGecko /coins/markets vs_currency=thb (demo key)")
    try:
        g = get(k["base"] + "/global", {k["header"]: k["key"]})
        save("cg_global.json", g, "CoinGecko /global (demo key)")
    except Exception as e:
        print("   cg global", e)


if __name__ == "__main__":
    for f in (bitkub_history, bitkub_ticker, binance_history, bot_fx, stablecoins, mempool, hashrate, coingecko):
        print(f.__name__)
        try:
            f()
        except Exception as e:
            print("   FAILED", f.__name__, e)
