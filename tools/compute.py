# -*- coding: utf-8 -*-
"""compute.py — every number the pages print, from data/raw, into build/facts.json.

Checks at the bottom gate the build: a series that comes back short or a figure that
lands outside sense stops publish.sh before a page is written.
"""
import json, os, sys, math, statistics as st, datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw")
BUILD = os.path.join(ROOT, "build")
os.makedirs(BUILD, exist_ok=True)


def raw(name):
    return json.load(open(os.path.join(RAW, name)))


def pct(v, q):
    v = sorted(v)
    i = (len(v) - 1) * q
    lo, hi = math.floor(i), math.ceil(i)
    return v[lo] + (v[hi] - v[lo]) * (i - lo)


F = {"fetched": {}}
for n in os.listdir(RAW):
    if n.endswith(".json"):
        r = raw(n)
        F["fetched"][n[:-5]] = {"at": r["fetched_at"], "source": r["source"]}

# ---------------------------------------------------------------- daily series
bk_btc = {r[0]: r[4] for r in raw("bitkub_btc_thb.json")["data"]}
bk_eth = {r[0]: r[4] for r in raw("bitkub_eth_thb.json")["data"]}
bk_usdt = {r[0]: r[4] for r in raw("bitkub_usdt_thb.json")["data"]}
bk_usdt_vol = {r[0]: r[5] for r in raw("bitkub_usdt_thb.json")["data"]}
bn_btc = {r[0]: r[4] for r in raw("binance_btcusdt.json")["data"]}
bn_eth = {r[0]: r[4] for r in raw("binance_ethusdt.json")["data"]}
fx_rows = raw("bot_usd_thb.json")["data"]
fx_by = {r["period"]: r for r in fx_rows}

# BOT publishes on Thai banking days; carry the last published day forward.
fx = {}
last = None
d = dt.date(2017, 8, 1)
end = dt.date.today()
while d <= end:
    k = d.isoformat()
    if k in fx_by:
        last = fx_by[k]
    if last:
        fx[k] = last
    d += dt.timedelta(days=1)


def f(x):
    return float(x) if x not in (None, "") else None


# --- 1. the Thai premium on bitcoin: Bitkub close vs Binance close x BOT mid
prem = []
for k in sorted(bk_btc):
    if k in bn_btc and k in fx:
        g = bn_btc[k] * f(fx[k]["mid_rate"])
        prem.append((k, (bk_btc[k] / g - 1) * 100))
pv = [p for _, p in prem]
F["premium"] = {
    "days": len(prem), "from": prem[0][0], "to": prem[-1][0],
    "median": round(st.median(pv), 2), "p10": round(pct(pv, .1), 2), "p90": round(pct(pv, .9), 2),
    "within_1pct": round(100 * sum(1 for p in pv if abs(p) <= 1) / len(pv), 1),
    "by_year": {},
}
for y in range(2018, end.year + 1):
    v = [p for k, p in prem if k.startswith(str(y))]
    if v:
        F["premium"]["by_year"][y] = {"median": round(st.median(v), 2), "p10": round(pct(v, .1), 2),
                                      "p90": round(pct(v, .9), 2), "days": len(v)}
top = max(F["premium"]["by_year"].items(), key=lambda kv: kv[1]["median"])
F["premium"]["hot_year"] = {"year": top[0], **top[1]}

# --- 2. the off-ramp spread: USDT sold on Bitkub vs the banks' buying rate for a dollar transfer
spread = []
for k in sorted(bk_usdt):
    if k in fx and f(fx[k].get("buying_transfer")):
        r = fx[k]
        spread.append((k, bk_usdt[k], f(r["mid_rate"]), f(r["buying_transfer"]), f(r["selling"])))
F["usdt"] = {
    "days": len(spread), "from": spread[0][0], "to": spread[-1][0],
    "vs_mid_median": round(st.median([(u / m - 1) * 100 for _, u, m, b, s in spread]), 2),
    "vs_tt_median": round(st.median([(u / b - 1) * 100 for _, u, m, b, s in spread]), 2),
    "vs_tt_p10": round(pct([(u / b - 1) * 100 for _, u, m, b, s in spread], .1), 2),
    "vs_tt_p90": round(pct([(u / b - 1) * 100 for _, u, m, b, s in spread], .9), 2),
    "beat_tt_share": round(100 * sum(1 for _, u, m, b, s in spread if u > b) / len(spread), 1),
    "bank_margin_median": round(st.median([(m / b - 1) * 100 for _, u, m, b, s in spread]), 2),
    "by_year": {},
}
for y in range(2018, end.year + 1):
    v = [(u / b - 1) * 100 for k, u, m, b, s in spread if k.startswith(str(y))]
    w = [(u / m - 1) * 100 for k, u, m, b, s in spread if k.startswith(str(y))]
    if v:
        F["usdt"]["by_year"][y] = {"vs_tt": round(st.median(v), 2), "vs_mid": round(st.median(w), 2), "days": len(v)}
# what 1,000 USDT fetched last close, against a 1,000 dollar wire at the banks' buying rate
lk = spread[-1]
F["usdt"]["last"] = {"date": lk[0], "bitkub": lk[1], "mid": lk[2], "tt": lk[3],
                     "thb_1000_usdt": round(1000 * lk[1]), "thb_1000_wire": round(1000 * lk[3])}
recent = [s for s in spread if s[0] >= (end - dt.timedelta(days=365)).isoformat()]
F["usdt"]["year_vs_tt"] = round(st.median([(u / b - 1) * 100 for _, u, m, b, s in recent]), 2)
F["usdt"]["year_thb_per_10k"] = round(10000 * st.median([(u - b) for _, u, m, b, s in recent]))

# --- 3. prices in baht
lb = max(bk_btc)
F["btc"] = {"date": lb, "thb": bk_btc[lb], "first_date": min(bk_btc), "first_thb": bk_btc[min(bk_btc)]}
hi = max(bk_btc.items(), key=lambda kv: kv[1])
F["btc"]["ath_thb"] = hi[1]; F["btc"]["ath_date"] = hi[0]
F["btc"]["from_ath_pct"] = round((bk_btc[lb] / hi[1] - 1) * 100, 1)
F["btc"]["multiple_since_first"] = round(bk_btc[lb] / bk_btc[min(bk_btc)], 1)
yr = (dt.date.fromisoformat(lb) - dt.timedelta(days=365)).isoformat()
F["btc"]["year_ago_thb"] = bk_btc.get(yr)
F["eth"] = {"date": max(bk_eth), "thb": bk_eth[max(bk_eth)]}
F["fx"] = {"date": fx_rows[-1]["period"], "mid": f(fx_rows[-1]["mid_rate"]),
           "tt": f(fx_rows[-1]["buying_transfer"]), "selling": f(fx_rows[-1]["selling"]),
           "min": min((f(r["mid_rate"]), r["period"]) for r in fx_rows if r["period"] >= "2018"),
           "max": max((f(r["mid_rate"]), r["period"]) for r in fx_rows if r["period"] >= "2018")}

# --- 4. stablecoins
sc = raw("llama_stablecoins.json")["data"]["peggedAssets"]
tot = sum((a["circulating"].get("peggedUSD") or 0) for a in sc)
top = sorted(sc, key=lambda a: -(a["circulating"].get("peggedUSD") or 0))[:10]
F["stable"] = {"total_usd": round(tot), "count": len(sc), "top": []}
for a in top:
    circ = a["circulating"].get("peggedUSD") or 0
    chains = sorted(((c, (v.get("current") or {}).get("peggedUSD") or 0) for c, v in a["chainCirculating"].items()),
                    key=lambda z: -z[1])
    F["stable"]["top"].append({"symbol": a["symbol"], "name": a["name"], "usd": round(circ),
                               "share": round(100 * circ / tot, 1),
                               "chains": [[c, round(v), round(100 * v / circ, 1) if circ else 0] for c, v in chains[:6]],
                               "chain_count": sum(1 for c, v in chains if v > 1e6)})
usdt = F["stable"]["top"][0]
F["stable"]["usdt_tron_share"] = next((c[2] for c in usdt["chains"] if c[0] == "Tron"), None)
tot_hist = raw("llama_stable_total.json")["data"]
F["stable"]["hist"] = [[dt.datetime.utcfromtimestamp(int(r["date"])).strftime("%Y-%m-%d"),
                        round((r.get("totalCirculatingUSD") or {}).get("peggedUSD", 0))] for r in tot_hist[::7]]
yago = [r for r in F["stable"]["hist"] if r[0] <= (end - dt.timedelta(days=365)).isoformat()]
F["stable"]["year_growth_pct"] = round((tot / yago[-1][1] - 1) * 100, 1) if yago else None

chains_usdt = raw("llama_usdt_chains.json")["data"]
F["stable"]["usdt_chain_hist"] = {c: v for c, v in chains_usdt.items()
                                  if c in ("Tron", "Ethereum", "BSC", "Solana", "Arbitrum", "TON", "Plasma", "Avalanche", "Polygon")}

# --- 5. bitcoin fees
mp = raw("mempool_fees.json")["data"]
fees = [(dt.datetime.utcfromtimestamp(r["timestamp"]).strftime("%Y-%m-%d"), r.get("avgFee_50")) for r in mp if r.get("avgFee_50") is not None]
F["fees"] = {"points": len(fees), "from": fees[0][0], "to": fees[-1][0],
             "last": fees[-1][1], "max": max(fees, key=lambda z: z[1]),
             "median_last_year": round(st.median([v for k, v in fees if k >= (end - dt.timedelta(days=365)).isoformat()]), 1)}
hr = raw("mempool_hashrate.json")["data"]
F["fees"]["hashrate"] = hr.get("currentHashrate")
F["fees"]["difficulty"] = hr.get("currentDifficulty")
# a typical 1-input 2-output segwit spend is ~141 vbytes
F["fees"]["vb_typical"] = 141

# --- 6. the Bitkub board and the world board
tk = raw("bitkub_ticker.json")["data"]
board = []
for t in tk:
    if not t["symbol"].endswith("_THB"): continue
    # 107 pairs carry quote_volume_self: the pair's volume on Bitkub's own book, where
    # quote_volume also counts liquidity routed from elsewhere. Own book is what we rank.
    qv = float(t.get("quote_volume_self", t.get("quote_volume")) or 0)
    board.append({"sym": t["symbol"][:-4], "last": float(t["last"]), "chg": float(t.get("percent_change") or 0), "thb_vol": qv,
                  "shared": "quote_volume_self" in t})
board.sort(key=lambda b: -b["thb_vol"])
F["bitkub"] = {"pairs": len(board), "shared": sum(1 for b in board if b["shared"]), "top": board[:24], "vol_total": round(sum(b["thb_vol"] for b in board)),
               "usdt_share": round(100 * next((b["thb_vol"] for b in board if b["sym"] == "USDT"), 0) / max(1, sum(b["thb_vol"] for b in board)), 1)}
cg = raw("cg_markets.json")["data"]
F["world"] = [{"sym": c["symbol"].upper(), "name": c["name"], "thb": c["current_price"], "cap_thb": c["market_cap"],
               "chg24": c.get("price_change_percentage_24h_in_currency"), "chg1y": c.get("price_change_percentage_1y_in_currency"),
               "rank": c["market_cap_rank"]} for c in cg[:40]]
try:
    g = raw("cg_global.json")["data"]["data"]
    F["global"] = {"cap_usd": round(g["total_market_cap"]["usd"]), "btc_dom": round(g["market_cap_percentage"]["btc"], 1),
                   "eth_dom": round(g["market_cap_percentage"]["eth"], 1), "coins": g["active_cryptocurrencies"]}
except Exception:
    F["global"] = None

# --- 7. the supply schedule, from the halving rule
sup, reward, h = [], 50.0, 0
total = 0.0
for era in range(34):
    total += reward * 210000
    sup.append({"era": era, "height": (era + 1) * 210000, "reward": reward, "supply": total})
    reward = math.floor(reward * 1e8 / 2) / 1e8
F["supply"] = {"cap": round(total, 8), "eras": sup,
               "halvings": [["2012-11-28", 25], ["2016-07-09", 12.5], ["2020-05-11", 6.25], ["2024-04-20", 3.125]],
               "next_height": 1050000}

# --- chart series, thinned
def thin(series, step):
    ks = sorted(series)
    out = [[k, series[k]] for i, k in enumerate(ks) if i % step == 0]
    if out[-1][0] != ks[-1]:
        out.append([ks[-1], series[ks[-1]]])
    return out


S = {"btc_thb": thin(bk_btc, 3), "eth_thb": thin(bk_eth, 3),
     "premium": [[k, round(p, 3)] for k, p in prem],
     "usdt": [[k, u, m, b] for k, u, m, b, s in spread],
     "fees": [[k, round(v, 1)] for k, v in fees[::2]],
     "fx": [[r["period"], f(r["mid_rate"])] for r in fx_rows]}
json.dump(S, open(os.path.join(BUILD, "series.json"), "w"), separators=(",", ":"))
json.dump(F, open(os.path.join(BUILD, "facts.json"), "w"), indent=1, default=str)

# ---------------------------------------------------------------- checks
fails = []
def check(name, ok):
    if not ok: fails.append(name)

check("bitkub btc since 2018", F["btc"]["first_date"] <= "2018-06-01" and len(bk_btc) > 2800)
check("BOT fx within 20 days", (end - dt.date.fromisoformat(F["fx"]["date"])).days < 20)
check("fx in 25..45", 25 < F["fx"]["mid"] < 45)
check("premium median small", abs(F["premium"]["median"]) < 2)
check("usdt days > 2500", F["usdt"]["days"] > 2500)
check("stable total > 100B", F["stable"]["total_usd"] > 1e11)
check("usdt is top stable", F["stable"]["top"][0]["symbol"] == "USDT")
check("supply cap ~21M", abs(F["supply"]["cap"] - 20999999.9769) < 1e-3)
check("bitkub board", F["bitkub"]["pairs"] > 50)
check("fees series", F["fees"]["points"] > 500)
check("btc thb sane", 5e5 < F["btc"]["thb"] < 2e7)
if fails:
    print("CHECK FAILED:", fails); sys.exit(1)
print("facts ok — premium median %.2f%%, USDT vs bank TT %.2f%%, stable $%.0fB, %d Bitkub pairs"
      % (F["premium"]["median"], F["usdt"]["vs_tt_median"], F["stable"]["total_usd"] / 1e9, F["bitkub"]["pairs"]))
