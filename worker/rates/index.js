// offrampt-rates — the live legs of the Offrampt rate board.
// Cron (*/15) refreshes; GET / serves the latest JSON with CORS open.
// Three legs: Bitkub public book (licensed Thai street), CoinGecko demo
// (global mid), BOT reference USD/THB (official, weekdays, fetched once/day).
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

  const out = {
    generated: new Date().toISOString(),
    note: "Reference information, not financial advice. Rates move; timestamps tell you how old each leg is.",
    sources: sources,
    routes: routes,
  };
  await env.RATES.put("rates", JSON.stringify(out));
  return out;
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
    let data = await env.RATES.get("rates", "json");
    if (!data || Date.parse(data.generated) < Date.now() - 20 * 60e3) {
      try { data = await refresh(env); } catch (e) { /* serve what we hold */ }
    }
    if (!data) return new Response(JSON.stringify({ error: "warming up" }), { status: 503, headers: cors });
    return new Response(JSON.stringify(data), { headers: cors });
  },
};
