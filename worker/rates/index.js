// offrampt-rates — the live legs of the Offrampt rate board.
// Cron (*/15) refreshes; GET / serves the latest JSON with CORS open.
// Four legs: Bitkub public book (licensed Thai street), CoinGecko demo
// (global mid), BOT reference USD/THB (official, weekdays, fetched once/day),
// USD cash at Thai money changers (baht-rates worker over the BAHT service
// binding; data thairate.com, CC BY 4.0).
// Failure policy is the live_shell one: a leg that fails keeps its previous
// value and its previous fetched_at — staleness is visible, never invented.

const BITKUB = "https://api.bitkub.com/api/v3/market/ticker?sym=";
const COINGECKO = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,tether&vs_currencies=usd";
const BOT_FX = "https://gateway.api.bot.or.th/Stat-ExchangeRate/v2/DAILY_AVG_EXG_RATE/";

function bangkokDate(d) {
  return (d || new Date()).toLocaleDateString("en-CA", { timeZone: "Asia/Bangkok" });
}

async function getJSON(url, headers) {
  const r = await fetch(url, { headers: headers || {}, signal: AbortSignal.timeout(10000) });
  if (!r.ok) throw new Error("HTTP " + r.status + " from " + new URL(url).host);
  return r.json();
}

async function bitkubLeg(sym) {
  const arr = await getJSON(BITKUB + sym);
  const t = arr[0];
  return {
    bid: parseFloat(t.highest_bid),
    ask: parseFloat(t.lowest_ask),
    last: parseFloat(t.last),
    fetched_at: new Date().toISOString(),
    source: "Bitkub public market API (SEC-licensed Thai exchange)",
  };
}

// Best USD cash buy (what the shop pays for a US$100 note band), stale boards left out.
async function cashLeg(env) {
  const get = (q) => env.BAHT.fetch("https://baht-rates/feed/best.json?cur=USD&limit=1" + q).then((r) => {
    if (!r.ok) throw new Error("baht-rates HTTP " + r.status);
    return r.json();
  });
  const [all, cm, cr] = await Promise.all([get(""), get("&city=chiangmai"), get("&city=chiangrai")]);
  const top = (d) => {
    const r = (d.results || []).find((x) => !x.stale);
    return r ? { rate: r.rate, shop: r.name, city: r.city, area: r.area, denom: r.denom, url: r.url } : null;
  };
  const best = top(all);
  if (!best || !all.mid) throw new Error("no cash rate");
  return {
    best: best,
    chiangmai: top(cm),
    chiangrai: top(cr),
    mid: all.mid,
    source_at: all.source_at,
    fetched_at: new Date().toISOString(),
    source: "Exchange rates: thairate.com (CC BY 4.0)",
    source_url: "https://thairate.com/",
  };
}

async function refresh(env) {
  const prev = (await env.RATES.get("rates", "json")) || { sources: {} };
  const sources = Object.assign({}, prev.sources);
  const today = bangkokDate();

  // BOT reference — one fetch per Bangkok day is plenty for a daily series.
  if (!sources.bot || sources.bot.checked_on !== today) {
    try {
      const since = bangkokDate(new Date(Date.now() - 7 * 864e5));
      const url = BOT_FX + "?start_period=" + since + "&end_period=" + today + "&currency=USD";
      const d = await getJSON(url, { Authorization: env.BOT_TOKEN });
      const row = d.result.data.data_detail[0];
      sources.bot = {
        usd_thb_mid: parseFloat(row.mid_rate),
        period: row.period,
        checked_on: today,
        fetched_at: new Date().toISOString(),
        source: "Bank of Thailand reference rate (weighted-average interbank)",
      };
    } catch (e) { /* keep previous BOT leg, its period stays visible */ }
  }

  try { sources.bitkub_usdt = await bitkubLeg("usdt_thb"); } catch (e) {}
  try { sources.bitkub_btc = await bitkubLeg("btc_thb"); } catch (e) {}

  try {
    const cg = await getJSON(COINGECKO, { "x-cg-demo-api-key": env.COINGECKO_KEY });
    sources.coingecko = {
      btc_usd: cg.bitcoin.usd,
      usdt_usd: cg.tether.usd,
      fetched_at: new Date().toISOString(),
      source: "CoinGecko global mid",
    };
  } catch (e) {}

  try { sources.cash = await cashLeg(env); delete sources.cash_error; } catch (e) { sources.cash_error = String(e && e.message || e); }

  const routes = [];
  const bot = sources.bot, cg = sources.coingecko;
  if (bot && cg && sources.bitkub_usdt) {
    const fair = bot.usd_thb_mid * cg.usdt_usd;
    routes.push({
      id: "usdt_bitkub",
      label: "USDT → THB · sell on Bitkub",
      thb_out_per_unit: sources.bitkub_usdt.bid,
      global_fair_thb: +fair.toFixed(4),
      premium_pct: +((sources.bitkub_usdt.bid / fair - 1) * 100).toFixed(2),
    });
  }
  if (bot && cg && sources.bitkub_btc) {
    const fair = bot.usd_thb_mid * cg.btc_usd;
    routes.push({
      id: "btc_bitkub",
      label: "BTC → THB · sell on Bitkub",
      thb_out_per_unit: sources.bitkub_btc.bid,
      global_fair_thb: +fair.toFixed(0),
      premium_pct: +((sources.bitkub_btc.bid / fair - 1) * 100).toFixed(2),
    });
  }

  if (sources.cash && sources.cash.best) {
    const c = sources.cash;
    routes.push({
      id: "usd_cash_changer",
      label: "USD cash → THB · best money changer",
      thb_out_per_unit: c.best.rate,
      global_fair_thb: c.mid,
      premium_pct: +((c.best.rate / c.mid - 1) * 100).toFixed(2),
    });
  }

  const out = {
    generated: new Date().toISOString(),
    note: "Rates move; each leg carries its timestamp.",
    sources: sources,
    routes: routes,
  };
  await env.RATES.put("rates", JSON.stringify(out));
  return out;
}

// ---- Paper Baht (offrampt.net/paper/): the coins it trades, live from Bitkub through here,
// so the reader's browser talks to this worker and not to the exchange.
const PAPER = ["BTC", "ETH", "XAUT", "USDT", "USDC", "SOL", "XRP", "DOGE", "BNB", "ADA", "KUB", "LINK", "SUI"];
const RES = { "15": 15 * 60, "60": 3600, "240": 4 * 3600, "1D": 86400 };

async function cached(ctx, key, ttl, make) {
  const cache = caches.default, req = new Request("https://offrampt-rates.cache/" + key);
  const hit = await cache.match(req);
  if (hit) return hit.json();
  const body = await make();
  ctx.waitUntil(cache.put(req, new Response(JSON.stringify(body), { headers: { "Cache-Control": "public, max-age=" + ttl } })));
  return body;
}

// Money the app holds besides baht: USDT and USDC on Bitkub, US dollar notes at the best
// Chiang Mai money changer (baht-rates over the BAHT binding; data thairate.com, CC BY 4.0).
const MONEY_COINS = ["USDT", "USDC"];

async function cashUSD(env) {
  const get = (side) => env.BAHT.fetch("https://baht-rates/feed/best.json?cur=USD&limit=1&city=chiangmai&side=" + side).then((r) => {
    if (!r.ok) throw new Error("baht-rates HTTP " + r.status);
    return r.json();
  });
  const [b, a] = await Promise.all([get("buy"), get("sell")]);
  const rb = (b.results || []).find((x) => !x.stale), ra = (a.results || []).find((x) => !x.stale);
  if (!rb || !ra) return null;
  return { bid: rb.rate, ask: ra.rate, bid_shop: rb.name, ask_shop: ra.name, denom: rb.denom, city: "chiangmai",
    mid: b.mid, source_at: b.source_at, source: "Exchange rates: thairate.com (CC BY 4.0)", source_url: "https://thairate.com/" };
}

async function paperTicker(env) {
  const all = await getJSON("https://api.bitkub.com/api/v3/market/ticker");
  const by = {};
  for (const t of all) by[t.symbol] = t;
  const coins = [], usdt = [], money = {};
  for (const s of PAPER) {
    const t = by[s + "_THB"];
    if (t) coins.push({
      sym: s, bid: +t.highest_bid, ask: +t.lowest_ask, last: +t.last, pct: +t.percent_change,
      high: +t.high_24_hr, low: +t.low_24_hr, vol_thb: +t.quote_volume,
    });
    const u = by[s + "_USDT"];
    if (u && +u.highest_bid > 0 && +u.lowest_ask > 0) usdt.push({ sym: s, bid: +u.highest_bid, ask: +u.lowest_ask, last: +u.last, pct: +u.percent_change });
  }
  for (const m of MONEY_COINS) {
    const t = by[m + "_THB"];
    if (t) money[m] = { bid: +t.highest_bid, ask: +t.lowest_ask, last: +t.last, pct: +t.percent_change, source: "Bitkub" };
  }
  try { const c = await cashUSD(env); if (c) money.USD = c; } catch (e) {}
  let mid = null;
  try { const r = await env.RATES.get("rates", "json"); if (r && r.sources && r.sources.bot) mid = { usd_thb: r.sources.bot.usd_thb_mid, period: r.sources.bot.period, source: "Bank of Thailand reference rate" }; } catch (e) {}
  return { at: new Date().toISOString(), source: "Bitkub public market API, v3 ticker", coins: coins, usdt: usdt, money: money, mid: mid };
}

async function paperHistory(sym, res, days) {
  const to = Math.floor(Date.now() / 1000), from = to - days * 86400;
  const d = await getJSON("https://api.bitkub.com/tradingview/history?symbol=" + sym + "_THB&resolution=" + res + "&from=" + from + "&to=" + to);
  if (d.s !== "ok") return { sym: sym, res: res, t: [], c: [] };
  return { sym: sym, res: res, at: new Date().toISOString(), source: "Bitkub public API, tradingview history", t: d.t, c: d.c };
}

async function paper(url, env, ctx, cors) {
  const p = url.pathname.replace(/\/+$/, "");
  try {
    if (p === "/paper/ticker") {
      return new Response(JSON.stringify(await cached(ctx, "ticker2", 10, () => paperTicker(env))), { headers: Object.assign({}, cors, { "Cache-Control": "public, max-age=5" }) });
    }
    if (p === "/paper/history") {
      const sym = (url.searchParams.get("sym") || "").toUpperCase(), res = url.searchParams.get("res") || "60";
      const days = Math.min(400, Math.max(1, parseInt(url.searchParams.get("days") || "7", 10) || 7));
      if (!PAPER.includes(sym) || !RES[res]) return new Response(JSON.stringify({ error: "sym or res" }), { status: 400, headers: cors });
      const ttl = res === "1D" ? 3600 : 120;
      const body = await cached(ctx, "h/" + sym + "/" + res + "/" + days, ttl, () => paperHistory(sym, res, days));
      return new Response(JSON.stringify(body), { headers: Object.assign({}, cors, { "Cache-Control": "public, max-age=" + Math.min(ttl, 300) }) });
    }
  } catch (e) {
    return new Response(JSON.stringify({ error: "upstream" }), { status: 502, headers: cors });
  }
  return new Response(JSON.stringify({ error: "not found" }), { status: 404, headers: cors });
}

export default {
  async scheduled(event, env, ctx) {
    ctx.waitUntil(refresh(env));
  },
  async fetch(request, env, ctx) {
    const cors = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET",
      "Content-Type": "application/json; charset=utf-8",
      "Cache-Control": "public, max-age=60",
    };
    if (request.method !== "GET") return new Response(null, { status: 405, headers: cors });
    const url = new URL(request.url);
    if (url.pathname.startsWith("/paper/")) return paper(url, env, ctx, cors);
    let data = await env.RATES.get("rates", "json");
    if (!data || Date.parse(data.generated) < Date.now() - 20 * 60e3) {
      try { data = await refresh(env); } catch (e) { /* serve what we hold */ }
    }
    if (!data) return new Response(JSON.stringify({ error: "warming up" }), { status: 503, headers: cors });
    return new Response(JSON.stringify(data), { headers: cors });
  },
};
