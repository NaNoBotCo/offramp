/* paper.js — Paper Baht, offrampt.net/paper/. Practice trading at live Bitkub prices,
   read through the offrampt-rates worker. Built by Hongdam Studio (hongdam.net). MIT. */
(function () {
  "use strict";
  var T = window.PB_T || {}, L = document.documentElement.lang || "en";
  function t(k, v) {
    var s = T[k] || k;
    if (v) for (var n in v) s = s.split("{" + n + "}").join(v[n]);
    return s;
  }
  function $(id) { return document.getElementById(id); }
  var API = (document.body.dataset.rates || "").replace(/\/$/, "") + "/paper/";
  var START = 1e6, KEY = "paperbaht.v1";
  var COINS = {
    BTC: "#f7931a", ETH: "#8c8cff", XAUT: "#e8c15a", SOL: "#9945ff", XRP: "#c8d0d8",
    DOGE: "#c2a633", BNB: "#f3ba2f", ADA: "#3c7cff", KUB: "#2fd27f", LINK: "#2a5ada", SUI: "#4da2ff"
  };
  var ORDER = Object.keys(COINS);
  // money the account holds: baht, US dollar notes (Chiang Mai money changer), USDT and USDC (Bitkub)
  var MORDER = ["THB", "USD", "USDT", "USDC"];
  var MINS = { THB: 10, USDT: 1 };
  var RANGES = { "1D": { res: "15", days: 1 }, "1W": { res: "60", days: 7 }, "1M": { res: "240", days: 30 }, "1Y": { res: "1D", days: 365 } };
  var reduce = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  var DPR = Math.min(window.devicePixelRatio || 1, 2);

  // ---------------------------------------------------------------- the account
  function fresh() {
    return { v: 2, start: Date.now(), bal: { THB: START, USD: 0, USDT: 0, USDC: 0 }, pos: {}, orders: [], hist: [], monkey: null, medals: {}, fee: 0.25,
      sound: false, sel: "BTC", range: "1D", snaps: [], best: 0, seq: 1, pay: "THB", show: "THB" };
  }
  function migrate(s) {
    if (s.v === 1) {
      s.bal = { THB: s.cash || 0, USD: 0, USDT: 0, USDC: 0 };
      if (s.pos.USDT) { s.bal.USDT += s.pos.USDT.q; delete s.pos.USDT; }
      s.orders = s.orders.filter(function (o) {
        o.pay = "THB"; if (o.side === "buy") o.spend = o.thb;
        if (o.sym !== "USDT") return true;
        if (o.side === "buy") s.bal.THB += o.thb; else s.bal.USDT += o.q;
        return false;
      });
      delete s.cash; s.pay = "THB"; s.show = "THB"; s.v = 2;
    }
    return s;
  }
  function load() {
    try { var s = JSON.parse(localStorage.getItem(KEY)); if (s && (s.v === 1 || s.v === 2)) return migrate(s); } catch (e) {}
    return null;
  }
  var S = load() || fresh();
  function save() { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) {} }

  // ---------------------------------------------------------------- numbers
  var NF = {};
  function fmt(x, d) {
    if (!NF[d]) NF[d] = new Intl.NumberFormat(L === "th" ? "th-TH" : "en-US", { minimumFractionDigits: d, maximumFractionDigits: d });
    return NF[d].format(x);
  }
  function dp(p) { p = Math.abs(p); return p >= 1000 ? 0 : p >= 10 ? 2 : p >= 1 ? 3 : p >= 0.01 ? 4 : 6; }
  function baht(x) { var a = Math.abs(x); return (x < 0 ? "−" : "") + "฿" + fmt(a, a >= 100 ? 0 : 2); }
  function signed(x) { var a = Math.abs(x); return (x > 0.004 ? "+" : x < -0.004 ? "−" : "") + "฿" + fmt(a, a >= 100 ? 0 : 2); }
  function price(p) { return "฿" + fmt(p, dp(p)); }
  function qty(q) { return fmt(q, q >= 100 ? 2 : q >= 1 ? 4 : 6); }
  function pct(x) { return (x > 0.004 ? "+" : x < -0.004 ? "−" : "") + fmt(Math.abs(x), 2) + "%"; }
  function cls(x) { return x > 0.004 ? "up" : x < -0.004 ? "dn" : ""; }
  function parse(s) { var x = parseFloat(String(s).replace(/[^\d.]/g, "")); return isFinite(x) ? x : 0; }
  function name(sym) { return T["c_" + sym] || sym; }
  function money(m, x, d) {
    var a = Math.abs(x), s = fmt(a, d != null ? d : (m === "THB" && a >= 100 ? 0 : 2)), n = x < 0 ? "−" : "";
    return m === "THB" ? n + "฿" + s : m === "USD" ? n + "$" + s : n + s + " " + m;
  }
  function mprice(m, p) { return m === "THB" ? price(p) : money(m, p, dp(p)); }
  function shop(n) { return String(n || "").replace(/\s+—\s+/, ", "); }
  function day(ms) { return new Date(ms).toLocaleDateString(L === "th" ? "th-TH" : "en-GB", { day: "numeric", month: "short", year: "numeric" }); }
  function clock(ms) { return new Date(ms).toLocaleTimeString(L === "th" ? "th-TH" : "en-GB", { hour: "2-digit", minute: "2-digit" }); }

  function disc(sym, size) {
    var c = COINS[sym] || "#888", s = size || 28;
    if (sym === "XAUT") {
      return '<svg class="disc" viewBox="0 0 28 28" width="' + s + '" height="' + s + '" aria-hidden="true"><path d="M6 19l3-9h10l3 9z" fill="#e8c15a" stroke="#fff3c2" stroke-width="1"/><path d="M9 10h10" stroke="#fff3c2"/><text x="14" y="17.5" text-anchor="middle" font-size="5.5" font-weight="700" fill="#5a4310" font-family="system-ui">Au</text></svg>';
    }
    var g = sym === "USDT" ? "$" : sym === "BTC" ? "₿" : sym.charAt(0);
    return '<svg class="disc" viewBox="0 0 28 28" width="' + s + '" height="' + s + '" aria-hidden="true"><circle cx="14" cy="14" r="12.5" fill="' + c + '"/><circle cx="14" cy="14" r="10" fill="none" stroke="rgba(255,255,255,.35)"/><text x="14" y="18.6" text-anchor="middle" font-size="12" font-weight="800" fill="#0b0f15" font-family="system-ui">' + g + "</text></svg>";
  }

  function mpic(m, size) {
    var s = size || 28, o = '<svg class="disc" viewBox="0 0 28 28" width="' + s + '" height="' + s + '" aria-hidden="true">';
    if (m === "THB" || m === "USD") {
      var f = m === "THB" ? "#2fa66a" : "#7fa56b", g = m === "THB" ? "฿" : "$";
      return o + '<rect x="2" y="7" width="24" height="14" rx="2.5" fill="' + f + '" stroke="#e8f2eb" stroke-opacity=".6"/><circle cx="14" cy="14" r="4.6" fill="none" stroke="rgba(255,255,255,.55)"/><text x="14" y="17.4" text-anchor="middle" font-size="9" font-weight="800" fill="#0b0f15" font-family="system-ui">' + g + "</text></svg>";
    }
    var c = m === "USDT" ? "#26a17b" : "#2775ca", t2 = m === "USDT" ? "₮" : "$";
    return o + '<circle cx="14" cy="14" r="12.5" fill="' + c + '"/><circle cx="14" cy="14" r="9.5" fill="none" stroke="rgba(255,255,255,.55)" stroke-width="1.4"/><text x="14" y="18.6" text-anchor="middle" font-size="12" font-weight="800" fill="#fff" font-family="system-ui">' + t2 + "</text></svg>";
  }

  // ---------------------------------------------------------------- live prices
  var Q = {}, QU = {}, MQ = {}, MID = null, qAt = 0, polling = false;
  function getJ(url, ms) {
    var ctl = window.AbortController ? new AbortController() : null;
    var to = setTimeout(function () { if (ctl) ctl.abort(); }, ms || 9000);
    return fetch(url, { signal: ctl ? ctl.signal : undefined, cache: "no-store" })
      .then(function (r) { clearTimeout(to); if (!r.ok) throw new Error(r.status); return r.json(); });
  }
  function poll() {
    clearTimeout(poll.t);
    if (document.hidden || polling) return;
    polling = true;
    getJ(API + "ticker").then(function (d) {
      if (!d || !d.coins) return;
      d.coins.forEach(function (c) { var o = Q[c.sym]; c.prev = o ? o.last : null; Q[c.sym] = c; });
      (d.usdt || []).forEach(function (c) { QU[c.sym] = c; });
      for (var m in (d.money || {})) MQ[m] = d.money[m];
      if (d.mid && d.mid.usd_thb) MID = d.mid.usd_thb;
      qAt = Date.parse(d.at) || Date.now();
      onTick();
    }).catch(function (e) { if (window.console) console.error(e); }).then(function () { polling = false; poll.t = setTimeout(poll, 10000); });
  }
  document.addEventListener("visibilitychange", function () { if (!document.hidden) poll(); });
  function liveAge() {
    var el = $("live"), tx = $("liveTxt");
    if (!qAt) { tx.textContent = t("stale"); return; }
    var a = Math.max(0, (Date.now() - qAt) / 1000), on = a < 60;
    el.classList.toggle("on", on);
    tx.textContent = (on ? t("live") : t("stale")) + " · " + (a < 90 ? Math.round(a) + t("sec") : Math.round(a / 60) + t("min"));
  }
  setInterval(liveAge, 1000);

  // ---------------------------------------------------------------- money moves
  function feeOf(x) { return x * (S.fee || 0) / 100; }
  function held(sym) { var p = S.pos[sym]; return p ? p.q : 0; }
  // baht for one unit of money m, at the price it sells for now
  function rate(m) { if (m === "THB") return 1; var q = MQ[m]; return q ? q.bid : 0; }
  function usdtLast() { return MQ.USDT ? MQ.USDT.last : 33.6; }
  function effPay(sym) { return S.pay === "USDT" && QU[sym || S.sel] ? "USDT" : "THB"; }
  function quote(sym, pay) { return pay === "USDT" ? QU[sym] : Q[sym]; }
  function toChart(p, pay) { return pay === "USDT" ? p * usdtLast() : p; }
  function moneyTotal() { var v = 0; MORDER.forEach(function (m) { v += (S.bal[m] || 0) * rate(m); }); return v; }
  function total() {
    var v = moneyTotal();
    for (var s in S.pos) if (Q[s]) v += S.pos[s].q * Q[s].bid; else v += S.pos[s].cost;
    S.orders.forEach(function (o) { v += o.side === "buy" ? o.spend * rate(o.pay || "THB") : (Q[o.sym] ? o.q * Q[o.sym].bid : o.cost); });
    return v;
  }
  function usdMid() { return MID || (MQ.USD && MQ.USD.mid) || usdtLast(); }
  function disp(v) { if (S.show === "USD") { var d = v / usdMid(); return "$" + fmt(d, Math.abs(d) >= 100 ? 0 : 2); } return baht(v); }
  function dispSigned(v) {
    if (S.show !== "USD") return signed(v);
    var d = v / usdMid(), a = Math.abs(d);
    return (d > 0.004 ? "+" : d < -0.004 ? "−" : "") + "$" + fmt(a, a >= 100 ? 0 : 2);
  }
  function record(h) { h.id = S.seq++; h.at = Date.now(); S.hist.unshift(h); if (S.hist.length > 300) S.hist.length = 300; }

  function doBuy(sym, spend, px, pay, reserved, via) {
    if (!reserved) S.bal[pay] -= spend;
    var fee = feeOf(spend), q = (spend - fee) / px, p = S.pos[sym] || (S.pos[sym] = { q: 0, cost: 0 }), r = rate(pay) || usdtLast();
    p.q += q; p.cost += spend * r;
    record({ sym: sym, side: "buy", q: q, px: px, pay: pay, pxThb: px * r, spend: spend, fee: fee, kind: via ? via.kind : "now" });
    toast((via ? t("filled") : "") + t("bought", { q: qty(q), coin: sym, px: mprice(pay, px) }), "");
    chime(660, 880); pop(sym, px * r, "buy");
    if (via) medal("patient");
  }
  function doSell(sym, q, px, pay, reserved, via) {
    var p = S.pos[sym], cost, r = rate(pay) || usdtLast();
    if (reserved) cost = via.cost;
    else { cost = p.cost * (q / p.q); p.q -= q; p.cost -= cost; }
    if (p && p.q < 1e-12) delete S.pos[sym];
    var gross = q * px, fee = feeOf(gross), net = gross - fee, pnl = net * r - cost;
    S.bal[pay] += net;
    record({ sym: sym, side: "sell", q: q, px: px, pay: pay, pxThb: px * r, net: net, fee: fee, pnl: pnl, kind: via ? via.kind : "now" });
    toast((via ? t("filled") : "") + t("sold", { q: qty(q), coin: sym, px: mprice(pay, px), pnl: signed(pnl) }), pnl >= 0 ? "gold" : "");
    chime(880, 660); pop(sym, px * r, "sell");
    if (pnl > 0) rain(Math.min(70, 14 + Math.round(Math.log10(1 + pnl) * 10)));
    if (via) medal("patient");
  }
  function fillOrders() {
    var keep = [], hit = false;
    S.orders.forEach(function (o) {
      var q = quote(o.sym, o.pay || "THB"), px = null;
      if (q) {
        if (o.side === "buy") { if ((o.kind === "limit" && q.ask <= o.px) || (o.kind === "stop" && q.ask >= o.px)) px = q.ask; }
        else if ((o.kind === "limit" && q.bid >= o.px) || (o.kind === "stop" && q.bid <= o.px)) px = q.bid;
      }
      if (px == null) { keep.push(o); return; }
      hit = true;
      if (o.side === "buy") doBuy(o.sym, o.spend, px, o.pay || "THB", true, o);
      else {
        S.pos[o.sym] = S.pos[o.sym] || { q: 0, cost: 0 };
        doSell(o.sym, o.q, px, o.pay || "THB", true, o);
      }
    });
    S.orders = keep;
    return hit;
  }
  function cancel(id) {
    S.orders = S.orders.filter(function (o) {
      if (o.id !== id) return true;
      if (o.side === "buy") S.bal[o.pay || "THB"] += o.spend;
      else { var p = S.pos[o.sym] || (S.pos[o.sym] = { q: 0, cost: 0 }); p.q += o.q; p.cost += o.cost; }
      return false;
    });
    save(); toast(t("cancelled"), ""); paint();
  }

  // ---------------------------------------------------------------- the monkey
  function monkeyInit() {
    if (S.monkey || ORDER.some(function (s) { return !Q[s]; })) return;
    var picks = ORDER.slice().sort(function () { return Math.random() - 0.5; }).slice(0, 3 + Math.floor(Math.random() * 3));
    var w = picks.map(function () { return 0.3 + Math.random(); }), sw = w.reduce(function (a, b) { return a + b; }, 0), pos = {};
    picks.forEach(function (s, i) { var thb = START * w[i] / sw; pos[s] = (thb - feeOf(thb)) / Q[s].ask; });
    S.monkey = { at: Date.now(), pos: pos };
  }
  function monkeyValue() {
    if (!S.monkey) return null;
    var v = 0;
    for (var s in S.monkey.pos) {
      var b = Q[s] ? Q[s].bid : rate(s);
      if (!b) return null; v += S.monkey.pos[s] * b;
    }
    return v;
  }

  // ---------------------------------------------------------------- medals
  var MEDALS = [
    ["first", "#2fd27f", "1"], ["ten", "#5aa9ff", "10"], ["gold", "#e8c15a", "Au"], ["five", "#b69cff", "5"],
    ["green", "#2fd27f", "฿"], ["monkey", "#ffb13b", "🐒"], ["rewind", "#ffb13b", "⏪"], ["patient", "#26a17b", "◎"],
    ["swap", "#2775ca", "⇄"], ["four", "#85bb65", "$฿"]
  ];
  function medal(k) {
    if (S.medals[k]) return;
    S.medals[k] = Date.now(); save();
    toast(t("medal_new", { m: t("m_" + k) }), "gold"); confetti(); chime(990, 1320);
    paintMedals();
  }
  function checkMedals() {
    var n = S.hist.filter(function (x) { return x.side !== "swap"; }).length;
    if (MORDER.every(function (m) { return S.bal[m] > 1e-6; })) medal("four");
    if (n >= 1) medal("first");
    if (n >= 10) medal("ten");
    if (held("XAUT") > 0) medal("gold");
    if (Object.keys(S.pos).filter(function (s) { return S.pos[s].q > 0; }).length >= 5) medal("five");
    var v = total();
    if (Object.keys(Q).length && v > START * 1.0001 && n) medal("green");
    var m = monkeyValue();
    if (m && n && Date.now() - S.monkey.at > 864e5 && v > m) medal("monkey");
  }
  function paintMedals() {
    $("medals").innerHTML = MEDALS.map(function (m) {
      var got = !!S.medals[m[0]];
      return '<div class="medal' + (got ? " got" : "") + '"><svg viewBox="0 0 40 40" aria-hidden="true"><path d="M13 2h6l-3 12zM21 2h6l-3 12z" fill="#0e7d4e"/><circle cx="20" cy="25" r="13" fill="' + m[1] + '"/><circle cx="20" cy="25" r="10" fill="none" stroke="rgba(255,255,255,.5)"/><text x="20" y="29.5" text-anchor="middle" font-size="' + (m[2].length > 1 ? 10 : 13) + '" font-weight="800" fill="#0b0f15" font-family="system-ui">' + m[2] + '</text></svg><span>' + t("m_" + m[0]) + (got ? '<span class="sr"> ✓</span>' : "") + "</span></div>";
    }).join("");
  }

  // ---------------------------------------------------------------- the tick
  function onTick() {
    monkeyInit();
    var filled = fillOrders();
    var v = total(), last = S.snaps[S.snaps.length - 1];
    if (!last || Date.now() - last[0] > 3e5) {
      S.snaps.push([Date.now(), Math.round(v)]);
      if (S.snaps.length > 600) S.snaps = S.snaps.filter(function (x, i) { return i % 2 === 0 || i === S.snaps.length - 1; });
    }
    checkMedals();
    save();
    liveAge();
    var el = $("live"); el.classList.add("tick"); setTimeout(function () { el.classList.remove("tick"); }, 700);
    paintStrip(true); paintPay(); paint(); if (!R) draw();
    if (filled) paintTrade();
  }

  // ---------------------------------------------------------------- painting
  var shownTotal = null;
  function tween(el, from, to, f) {
    if (reduce || from == null || Math.abs(to - from) < 0.5) { el.textContent = f(to); return; }
    var t0 = performance.now(), d = 700;
    (function step(now) {
      var k = Math.min(1, (now - t0) / d), e = 1 - Math.pow(1 - k, 3);
      el.textContent = f(from + (to - from) * e);
      if (k < 1) requestAnimationFrame(step);
    })(t0);
  }
  function paint() {
    var v = total(), ch = v - START;
    tween($("total"), shownTotal, v, disp); shownTotal = v;
    var c = $("chg"); c.textContent = dispSigned(ch) + " " + pct(ch / START * 100); c.className = "num " + cls(ch);
    $("cash").textContent = disp(moneyTotal());
    $("totCur").textContent = S.show === "USD" ? "$ ⇄ ฿" : "฿ ⇄ $";
    $("tot").setAttribute("aria-label", t("total") + " " + disp(v) + ". " + t(S.show === "USD" ? "show_thb" : "show_usd"));
    var lvl = Math.max(0.06, Math.min(0.98, 0.5 + (v / START - 1) * 2.5));
    $("jarLvl").style.transform = "translateY(" + (46 - lvl * 36).toFixed(1) + "px)";
    $("jar").setAttribute("aria-label", t("total") + " " + disp(v));
    paintQuote();
    if (tab === "money") paintMoney();
    if (tab === "mine") paintMine();
    if (tab === "toys") paintToys();
    paintSum();
  }
  function paintStrip(flash) {
    var box = $("strip");
    if (!box.children.length) {
      box.innerHTML = ORDER.map(function (s) {
        return '<button class="coin" data-sym="' + s + '" aria-pressed="' + (s === S.sel) + '">' + disc(s) + '<span class="s">' + s + '</span><span class="p num"><span class="v">—</span><span class="c"></span></span></button>';
      }).join("");
      box.addEventListener("click", function (e) { var b = e.target.closest(".coin"); if (b) select(b.dataset.sym); });
    }
    Array.prototype.forEach.call(box.children, function (b) {
      var s = b.dataset.sym, q = Q[s];
      b.setAttribute("aria-pressed", s === S.sel);
      if (!q) return;
      b.querySelector(".v").textContent = price(q.last);
      var c = b.querySelector(".c"); c.textContent = pct(q.pct); c.className = "c " + cls(q.pct);
      b.setAttribute("aria-label", name(s) + ", " + price(q.last) + ", " + pct(q.pct));
      if (flash && q.prev != null && q.prev !== q.last && !reduce) {
        b.classList.remove("flash-up", "flash-dn"); void b.offsetWidth;
        b.classList.add(q.last > q.prev ? "flash-up" : "flash-dn");
      }
    });
  }
  function paintQuote() {
    var pay = effPay(), q = quote(S.sel, pay);
    $("qname").innerHTML = disc(S.sel, 18) + " " + name(S.sel) + " · " + S.sel;
    if (!q) return;
    $("qpx").textContent = R ? price(R.c[R.i]) : mprice(pay, q.last);
    var c = $("qchg");
    if (R) { var rc = (R.c[R.i] / R.c[0] - 1) * 100; c.textContent = pct(rc); c.className = "qchg num " + cls(rc); }
    else { c.textContent = pct(q.pct) + " · 24h"; c.className = "qchg num " + cls(q.pct); }
    $("qba").textContent = t("bidask", { a: mprice(pay, q.ask), b: mprice(pay, q.bid) });
  }
  function select(sym) {
    if (R || !COINS[sym]) return;
    S.sel = sym; save();
    paintStrip(false); paintQuote(); loadHist(); paintTrade();
    if (tab === "toys") paintToys();
    var b = document.querySelector('.coin[data-sym="' + sym + '"]');
    if (b && b.scrollIntoView) b.scrollIntoView({ block: "nearest", inline: "nearest", behavior: reduce ? "auto" : "smooth" });
  }

  // ---------------------------------------------------------------- trade ticket
  var side = "buy", kind = "now", limitPx = null;
  function amt() { return parse($("amt").value); }
  function setAmt(x) { $("amt").value = fmt(Math.floor(x * 100) / 100, x >= 100 ? 0 : 2); paintSum(); }
  var CHIPS = { THB: [1000, 10000, 100000], USDT: [10, 100, 1000] }, lastPay = null;
  function paintPay() {
    var pay = effPay(), ok = !!QU[S.sel];
    document.querySelectorAll(".pay button").forEach(function (b) {
      b.setAttribute("aria-pressed", b.dataset.pay === pay);
      if (b.dataset.pay === "USDT") { b.disabled = !ok; b.title = ok ? "" : t("no_usdt", { coin: S.sel }); }
    });
    $("payL").textContent = t(side === "buy" ? "pay_in" : "get_in");
    $("amtCur").textContent = pay === "THB" ? "฿" : "₮";
    $("amt").setAttribute("aria-label", t("amount_in", { m: pay === "THB" ? t("m_THB") : "USDT" }));
    if ($("chips").dataset.pay !== pay || !$("chips").children.length) $("chips").innerHTML = CHIPS[pay].map(function (v) { return '<button data-a="' + v + '">' + money(pay, v, 0) + "</button>"; }).join("") +
      '<button data-a="half">' + t("half") + '</button><button data-a="all">' + t("all") + "</button>";
    $("chips").dataset.pay = pay;
    if (lastPay && lastPay !== pay) { limitPx = null; setAmt(pay === "THB" ? 10000 : 300); }
    lastPay = pay;
  }
  function paintTrade() {
    paintPay();
    document.querySelectorAll(".side button").forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.side === side); });
    document.querySelectorAll(".kind button").forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.k === kind); });
    $("def").textContent = t("def_" + kind + "_" + side);
    $("pxrow").hidden = kind === "now";
    var g = $("go");
    g.className = "go" + (side === "sell" ? " sell" : "");
    g.textContent = kind === "now" ? t(side) + " " + S.sel : t("place");
    var qq = quote(S.sel, effPay());
    if (kind !== "now" && limitPx == null && qq) {
      var p = side === "buy" ? qq.ask : qq.bid, up = (kind === "limit") === (side === "sell");
      limitPx = +(p * (up ? 1.02 : 0.98)).toFixed(dp(p));
      $("px").value = fmt(limitPx, dp(limitPx));
    }
    var mine = S.orders.filter(function (o) { return o.sym === S.sel; });
    $("ordH").hidden = !mine.length;
    $("ordHere").innerHTML = mine.map(orderRow).join("");
    paintSum(); draw();
  }
  function orderRow(o) {
    var m = o.pay || "THB";
    return '<li>' + disc(o.sym, 22) + '<span class="grow">' + t(o.side) + " " + o.sym + " · " + t(o.kind) + '<br><span class="mute num">' + mprice(m, o.px) + " · " + (o.side === "buy" ? money(m, o.spend) : qty(o.q) + " " + o.sym) + '</span></span><button class="x" data-cancel="' + o.id + '">' + t("cancel") + "</button></li>";
  }
  function paintSum() {
    var pay = effPay(), q = quote(S.sel, pay), a = amt(), el = $("sum");
    if (!q) { el.textContent = t("e_noprice"); return; }
    var px = kind === "now" ? (side === "buy" ? q.ask : q.bid) : (limitPx || q.last);
    if (side === "buy") {
      var fee = feeOf(a);
      el.innerHTML = t("youget") + " <b>" + qty(Math.max(0, a - fee) / px) + " " + S.sel + "</b> · " + t("fee") + " " + money(pay, fee) +
        "<br>" + t("youhave") + " " + money(pay, S.bal[pay] || 0);
    } else {
      var h = held(S.sel), sq = Math.min(h, a / px), gross = sq * px;
      el.innerHTML = t("youget") + " <b>" + money(pay, gross - feeOf(gross)) + "</b> · " + t("fee") + " " + money(pay, feeOf(gross)) + "<br>" + t("youhave") + " " + qty(h) + " " + S.sel + " (" + money(pay, h * q.bid) + ")";
    }
  }
  function go() {
    var pay = effPay(), q = quote(S.sel, pay), a = amt();
    if (!q) return toast(t("e_noprice"), "no");
    if (a < MINS[pay]) return toast(t("e_min", { min: money(pay, MINS[pay], 0) }), "no");
    if (kind !== "now" && !(limitPx > 0)) return toast(t("e_price"), "no");
    if (side === "buy") {
      if (a > (S.bal[pay] || 0) + 0.005) return toast(t("e_bal", { m: pay === "THB" ? t("m_THB") : pay }), "no");
      a = Math.min(a, S.bal[pay]);
      if (kind === "now") doBuy(S.sel, a, q.ask, pay);
      else { S.bal[pay] -= a; S.orders.push({ id: S.seq++, sym: S.sel, side: "buy", kind: kind, pay: pay, px: limitPx, spend: a, at: Date.now() }); placed(); }
    } else {
      var h = held(S.sel);
      if (!(h > 0)) return toast(t("e_none", { coin: S.sel }), "no");
      var px = kind === "now" ? q.bid : limitPx, sq = Math.min(h, a / px);
      if (h - sq < h * 1e-6) sq = h;
      if (kind === "now") doSell(S.sel, sq, q.bid, pay);
      else {
        var p = S.pos[S.sel], cost = p.cost * (sq / p.q);
        p.q -= sq; p.cost -= cost; if (p.q < 1e-12) delete S.pos[S.sel];
        S.orders.push({ id: S.seq++, sym: S.sel, side: "sell", kind: kind, pay: pay, px: limitPx, q: sq, cost: cost, at: Date.now() }); placed();
      }
    }
    fillOrders(); checkMedals(); save(); paint(); paintTrade();
  }
  function placed() {
    var o = S.orders[S.orders.length - 1];
    toast(t("placed", { side: t(o.side), coin: o.sym, px: mprice(o.pay, o.px) }), "");
    chime(520, 620);
  }
  $("go").addEventListener("click", go);
  $("amt").addEventListener("input", paintSum);
  $("amt").addEventListener("keydown", function (e) { if (e.key === "Enter") go(); });
  $("amt").addEventListener("blur", function () { setAmt(amt()); });
  $("px").addEventListener("input", function () { limitPx = parse($("px").value) || null; paintSum(); draw(); });
  document.querySelector(".side").addEventListener("click", function (e) {
    var b = e.target.closest("button"); if (!b) return; side = b.dataset.side; limitPx = null; paintTrade();
  });
  document.querySelector(".pay").addEventListener("click", function (e) {
    var b = e.target.closest("button"); if (!b || b.disabled) return; S.pay = b.dataset.pay; save(); paintTrade(); paintQuote();
  });
  document.querySelector(".kind").addEventListener("click", function (e) {
    var b = e.target.closest("button"); if (!b) return; kind = b.dataset.k; limitPx = null; paintTrade();
  });
  $("chips").addEventListener("click", function (e) {
    var b = e.target.closest("button"); if (!b) return;
    var a = b.dataset.a, pay = effPay(), q = quote(S.sel, pay);
    if (a === "half" || a === "all") {
      var f = a === "half" ? 0.5 : 1;
      if (side === "buy") setAmt((S.bal[pay] || 0) * f);
      else if (q) setAmt(held(S.sel) * (kind === "now" ? q.bid : (limitPx || q.bid)) * f);
    } else setAmt(+a);
  });
  document.addEventListener("click", function (e) {
    var c = e.target.closest("[data-cancel]"); if (c) cancel(+c.dataset.cancel);
    var r = e.target.closest("[data-pick]"); if (r) { select(r.dataset.pick); showTab("trade"); }
  });

  // ---------------------------------------------------------------- the chart
  var cv = $("chart"), cx = cv.getContext("2d"), box = $("chartbox"), H = null, HC = {}, W = 0, HH = 0, hover = null, dragging = false, tm = null;
  function size() {
    var r = box.getBoundingClientRect();
    W = Math.max(10, r.width); HH = Math.max(10, r.height);
    cv.width = Math.round(W * DPR); cv.height = Math.round(HH * DPR);
    draw();
  }
  if (window.ResizeObserver) new ResizeObserver(size).observe(box); else addEventListener("resize", size);
  function hist(sym, range) {
    var key = sym + "/" + range, h = HC[key];
    if (h && Date.now() - h.got < 12e4) return Promise.resolve(h);
    var r = RANGES[range];
    return getJ(API + "history?sym=" + sym + "&res=" + r.res + "&days=" + r.days, 12000).then(function (d) {
      var o = { key: key, sym: sym, range: range, t: (d.t || []).map(function (x) { return x * 1000; }), c: d.c || [], got: Date.now() };
      HC[key] = o; return o;
    });
  }
  function loadHist() {
    var sym = S.sel, range = S.range, m = $("cmsg");
    document.querySelectorAll(".ranges button").forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.r === range); });
    if (!HC[sym + "/" + range]) { m.textContent = t("loading"); m.hidden = false; }
    hist(sym, range).then(function (h) {
      if (sym !== S.sel || range !== S.range) return;
      H = h; m.hidden = h.c.length > 1; if (h.c.length < 2) m.textContent = t("e_chart");
      draw();
    }).catch(function (e) { if (window.console) console.error(e); if (sym === S.sel) { m.textContent = t("e_chart"); m.hidden = false; } });
  }
  document.querySelector(".ranges").addEventListener("click", function (e) {
    var b = e.target.closest("button"); if (!b || R) return; S.range = b.dataset.r; save(); tm = null; loadHist();
  });
  function series() {
    if (R) return { t: R.t.slice(0, R.i + 1), c: R.c.slice(0, R.i + 1), full: R.t.length };
    if (!H || H.sym !== S.sel) return null;
    var ts = H.t.slice(), cs = H.c.slice(), q = Q[S.sel];
    if (q && ts.length && Date.now() > ts[ts.length - 1]) { ts.push(Math.max(Date.now(), ts[ts.length - 1] + 1)); cs.push(q.last); }
    return { t: ts, c: cs, full: ts.length };
  }
  var geo = null;
  function draw() {
    if (!W) return;
    var sr = series();
    cx.setTransform(DPR, 0, 0, DPR, 0, 0);
    cx.clearRect(0, 0, W, HH);
    if (!sr || sr.c.length < 2) { geo = null; return; }
    var ts = sr.t, cs = sr.c, n = sr.full;
    var lo = Math.min.apply(null, cs), hi = Math.max.apply(null, cs);
    if (R) { lo = Math.min(lo, Math.min.apply(null, R.c)); hi = Math.max(hi, Math.max.apply(null, R.c)); }
    var pay = effPay(), line = (!R && tab === "trade" && kind !== "now" && limitPx > 0) ? toChart(limitPx, pay) : null;
    if (line && line > lo * 0.6 && line < hi * 1.4) { lo = Math.min(lo, line); hi = Math.max(hi, line); }
    var pad = (hi - lo) * 0.12 || hi * 0.01; lo -= pad; hi += pad;
    cx.font = "11px " + getComputedStyle(document.body).fontFamily;
    var lineTxt = line ? mprice(pay, limitPx) : "";
    var R0 = 12 + Math.max(cx.measureText(price(hi)).width, cx.measureText(price(lo)).width, line ? cx.measureText(lineTxt).width + 6 : 0);
    var T0 = HH < 160 ? 12 : 30, B0 = HH < 160 ? 8 : 18, L0 = 6, w = W - L0 - R0, h = HH - T0 - B0;
    var t0 = ts[0], t1 = R ? R.t[R.t.length - 1] : ts[ts.length - 1];
    function X(x) { return L0 + (t1 > t0 ? (x - t0) / (t1 - t0) : 0) * w; }
    function Y(y) { return T0 + (1 - (y - lo) / (hi - lo)) * h; }
    geo = { X: X, Y: Y, lo: lo, hi: hi, T0: T0, h: h, L0: L0, w: w, t0: t0, t1: t1, ts: ts, cs: cs };
    // grid
    cx.textAlign = "left"; cx.textBaseline = "middle";
    var ng = h < 110 ? 1 : 3;
    for (var g = 0; g <= ng; g++) {
      var gy = lo + (hi - lo) * (0.1 + g * 0.8 / ng), yy = Y(gy);
      cx.strokeStyle = "rgba(255,255,255,.06)"; cx.lineWidth = 1;
      cx.beginPath(); cx.moveTo(L0, yy); cx.lineTo(L0 + w, yy); cx.stroke();
      cx.fillStyle = "#6f7b82"; cx.fillText(price(gy), L0 + w + 6, yy);
    }
    var upc = cs[cs.length - 1] >= cs[0], col = upc ? "#2fd27f" : "#ff6b6f";
    // time machine shading
    if (tm != null && !R && S.range === "1Y" && cs[tm] != null) {
      var tx = X(ts[tm]);
      cx.fillStyle = "rgba(255,177,59,.08)"; cx.fillRect(tx, T0, L0 + w - tx, h);
      cx.strokeStyle = "rgba(255,177,59,.9)"; cx.setLineDash([3, 3]); cx.beginPath(); cx.moveTo(tx, T0); cx.lineTo(tx, T0 + h); cx.stroke(); cx.setLineDash([]);
    }
    // area + line
    var grad = cx.createLinearGradient(0, T0, 0, T0 + h);
    grad.addColorStop(0, upc ? "rgba(47,210,127,.28)" : "rgba(255,107,111,.26)"); grad.addColorStop(1, "rgba(0,0,0,0)");
    cx.beginPath();
    for (var i = 0; i < cs.length; i++) { var px = X(ts[i]), py = Y(cs[i]); if (i) cx.lineTo(px, py); else cx.moveTo(px, py); }
    cx.lineWidth = 2; cx.strokeStyle = col; cx.lineJoin = "round"; cx.stroke();
    cx.lineTo(X(ts[cs.length - 1]), T0 + h); cx.lineTo(X(ts[0]), T0 + h); cx.closePath(); cx.fillStyle = grad; cx.fill();
    // trades on this coin
    var trades = R ? R.trades : S.hist.filter(function (x) { return x.sym === S.sel && x.at >= t0; });
    trades.forEach(function (x) {
      var mx = X(Math.min(x.at, t1)), my = Y(x.pxThb || x.px), b = x.side === "buy";
      cx.beginPath(); cx.arc(mx, my, 7, 0, 7); cx.fillStyle = b ? "#2fd27f" : "#ffb13b"; cx.fill();
      cx.lineWidth = 2; cx.strokeStyle = "#05070c"; cx.stroke();
      cx.fillStyle = "#05070c"; cx.textAlign = "center"; cx.font = "bold 9px system-ui";
      cx.fillText(b ? "B" : "S", mx, my + 0.5); cx.textAlign = "left";
    });
    // waiting orders
    if (!R) S.orders.filter(function (o) { return o.sym === S.sel; }).forEach(function (o) {
      var oy = Y(toChart(o.px, o.pay)); if (oy < T0 || oy > T0 + h) return;
      cx.strokeStyle = o.side === "buy" ? "rgba(47,210,127,.6)" : "rgba(255,177,59,.6)"; cx.setLineDash([2, 4]);
      cx.beginPath(); cx.moveTo(L0, oy); cx.lineTo(L0 + w, oy); cx.stroke(); cx.setLineDash([]);
    });
    // the line you drag
    if (line) {
      var ly = Y(line);
      cx.strokeStyle = "#ffb13b"; cx.lineWidth = 1.5; cx.setLineDash([6, 4]);
      cx.beginPath(); cx.moveTo(L0, ly); cx.lineTo(L0 + w, ly); cx.stroke(); cx.setLineDash([]);
      cx.fillStyle = "#ffb13b"; roundRect(L0 + w + 1, ly - 10, R0 - 3, 20, 6); cx.fill();
      cx.fillStyle = "#05070c"; cx.font = "bold 11px system-ui"; cx.fillText(lineTxt, L0 + w + 3, ly);
      cx.beginPath(); for (var k = -1; k <= 1; k++) { cx.moveTo(L0 + w / 2 - 10, ly + k * 3 - 12); cx.lineTo(L0 + w / 2 + 10, ly + k * 3 - 12); }
      cx.strokeStyle = "rgba(255,177,59,.7)"; cx.lineWidth = 1; cx.stroke();
    }
    // the last price
    var lx = X(ts[cs.length - 1]), ly2 = Y(cs[cs.length - 1]);
    cx.beginPath(); cx.arc(lx, ly2, 4, 0, 7); cx.fillStyle = col; cx.fill();
    cx.beginPath(); cx.arc(lx, ly2, 9, 0, 7); cx.strokeStyle = upc ? "rgba(47,210,127,.35)" : "rgba(255,107,111,.35)"; cx.lineWidth = 2; cx.stroke();
    // hover
    var tip = $("tip");
    if (hover != null && !dragging) {
      var hi2 = nearest(hover), hx = X(ts[hi2]), hy = Y(cs[hi2]);
      cx.strokeStyle = "rgba(255,255,255,.25)"; cx.lineWidth = 1;
      cx.beginPath(); cx.moveTo(hx, T0); cx.lineTo(hx, T0 + h); cx.stroke();
      cx.beginPath(); cx.arc(hx, hy, 4, 0, 7); cx.fillStyle = "#eef2ef"; cx.fill();
      tip.hidden = false;
      tip.textContent = price(cs[hi2]) + " · " + (S.range === "1D" || R ? clock(ts[hi2]) : day(ts[hi2]));
    } else tip.hidden = true;
    var rangeName = R ? t("rw_on") : t("r" + S.range);
    cv.setAttribute("aria-label", t("chart_aria", { coin: name(S.sel), range: rangeName, a: price(cs[0]), b: price(cs[cs.length - 1]), h: price(Math.max.apply(null, cs)), l: price(Math.min.apply(null, cs)) }));
  }
  function roundRect(x, y, w, h, r) { cx.beginPath(); cx.moveTo(x + r, y); cx.arcTo(x + w, y, x + w, y + h, r); cx.arcTo(x + w, y + h, x, y + h, r); cx.arcTo(x, y + h, x, y, r); cx.arcTo(x, y, x + w, y, r); cx.closePath(); }
  function nearest(px) {
    var g = geo, tt = g.t0 + (px - g.L0) / g.w * (g.t1 - g.t0), best = 0, bd = Infinity;
    for (var i = 0; i < g.ts.length; i++) { var d = Math.abs(g.ts[i] - tt); if (d < bd) { bd = d; best = i; } }
    return best;
  }
  function yToPrice(y) { var g = geo; return g.lo + (1 - (y - g.T0) / g.h) * (g.hi - g.lo); }
  function local(e) { var r = cv.getBoundingClientRect(); return { x: e.clientX - r.left, y: e.clientY - r.top }; }
  cv.addEventListener("pointerdown", function (e) {
    if (!geo || R) return;
    var p = local(e);
    if (kind !== "now" && tab === "trade") {
      dragging = true; cv.setPointerCapture(e.pointerId);
      setLimit(yToPrice(p.y));
    } else { hover = p.x; draw(); }
  });
  cv.addEventListener("pointermove", function (e) {
    if (!geo) return;
    var p = local(e);
    if (dragging) setLimit(yToPrice(p.y));
    else if (e.pointerType === "mouse" || e.buttons) { hover = p.x; draw(); }
  });
  function endDrag() { if (dragging) { dragging = false; paintSum(); } }
  cv.addEventListener("pointerup", endDrag); cv.addEventListener("pointercancel", endDrag);
  cv.addEventListener("pointerleave", function () { hover = null; draw(); });
  function setLimit(p) {
    if (!(p > 0)) return;
    if (effPay() === "USDT") p = p / usdtLast();
    limitPx = +p.toFixed(dp(p)); $("px").value = fmt(limitPx, dp(limitPx)); paintSum(); draw();
  }

  // ---------------------------------------------------------------- mine
  var eq = $("eq"), ex = eq.getContext("2d");
  function paintMine() {
    var rows = Object.keys(S.pos).filter(function (s) { return S.pos[s].q > 0; }).map(function (s) {
      var p = S.pos[s], q = Q[s], v = q ? p.q * q.bid : p.cost, g = v - p.cost;
      return '<li class="sel" data-pick="' + s + '">' + disc(s, 22) + '<span class="grow">' + name(s) + '<br><span class="mute num">' + qty(p.q) + " " + s + '</span></span><span class="r">' + baht(v) + '<br><span class="' + cls(g) + '">' + signed(g) + " " + pct(p.cost ? g / p.cost * 100 : 0) + "</span></span></li>";
    });
    $("hold").innerHTML = rows.join("") || '<li class="empty">' + t("nothing") + "</li>";
    $("ords").innerHTML = S.orders.map(orderRow).join("") || '<li class="empty">' + t("nothing") + "</li>";
    $("hist").innerHTML = S.hist.slice(0, 30).map(function (x) {
      var when = '<br><span class="mute">' + day(x.at) + " " + clock(x.at) + "</span>";
      if (x.side === "swap") return "<li>" + mpic(x.from, 22) + '<span class="grow">' + t("swap") + " " + money(x.from, x.x) + when + '</span><span class="r">' + money(x.to, x.y) + "</span></li>";
      return "<li>" + disc(x.sym, 22) + '<span class="grow">' + t(x.side) + " " + qty(x.q) + " " + x.sym + when + '</span><span class="r">' + mprice(x.pay || "THB", x.px) + (x.pnl != null ? '<br><span class="' + cls(x.pnl) + '">' + signed(x.pnl) + "</span>" : "") + "</span></li>";
    }).join("") || '<li class="empty">' + t("nothing") + "</li>";
    // equity line
    var r = eq.getBoundingClientRect(), w = r.width, h = r.height;
    if (!w) return;
    eq.width = Math.round(w * DPR); eq.height = Math.round(h * DPR); ex.setTransform(DPR, 0, 0, DPR, 0, 0); ex.clearRect(0, 0, w, h);
    var pts = S.snaps.concat([[Date.now(), total()]]);
    if (pts.length < 2) pts.unshift([S.start, START]);
    var vs = pts.map(function (p) { return p[1]; }).concat([START]), lo = Math.min.apply(null, vs), hi = Math.max.apply(null, vs);
    if (hi - lo < START * 0.002) { lo -= START * 0.001; hi += START * 0.001; }
    var a = pts[0][0], b = pts[pts.length - 1][0];
    function X(x) { return 4 + (b > a ? (x - a) / (b - a) : 1) * (w - 8); }
    function Y(y) { return 6 + (1 - (y - lo) / (hi - lo)) * (h - 12); }
    ex.strokeStyle = "rgba(255,255,255,.18)"; ex.setLineDash([3, 3]); ex.beginPath(); ex.moveTo(0, Y(START)); ex.lineTo(w, Y(START)); ex.stroke(); ex.setLineDash([]);
    ex.beginPath(); pts.forEach(function (p, i) { if (i) ex.lineTo(X(p[0]), Y(p[1])); else ex.moveTo(X(p[0]), Y(p[1])); });
    ex.strokeStyle = total() >= START ? "#2fd27f" : "#ff6b6f"; ex.lineWidth = 2; ex.stroke();
    eq.setAttribute("aria-label", t("equity") + ": " + disp(pts[0][1]) + " → " + disp(total()));
  }

  // ---------------------------------------------------------------- money: the wallet and swaps, every swap through baht
  var swF = "THB", swT = "USDT";
  function swapQuote(f, to, x) {
    var legs = [], thb = x, y, change = 0;
    if (!(x > 0)) return null;
    if (f !== "THB") {
      var q = MQ[f]; if (!q) return null;
      if (f === "USD") { thb = x * q.bid; legs.push(t("leg_sell_cash", { x: money(f, x), shop: shop(q.bid_shop), r: price(q.bid), y: baht(thb) })); }
      else { var g = x * q.bid, fe = feeOf(g); thb = g - fe; legs.push(t("leg_sell_coin", { x: money(f, x), r: price(q.bid), y: baht(thb), f: baht(fe) })); }
    }
    y = thb;
    if (to !== "THB") {
      var q2 = MQ[to]; if (!q2) return null;
      if (to === "USD") {
        y = Math.floor(thb / q2.ask + 1e-9); change = thb - y * q2.ask;
        legs.push(t("leg_buy_cash", { y: money(to, y, 0), shop: shop(q2.ask_shop), r: price(q2.ask) }) + (change > 0.005 ? " · " + t("change", { c: baht(change) }) : ""));
      } else { var fe2 = feeOf(thb); y = (thb - fe2) / q2.ask; legs.push(t("leg_buy_coin", { y: money(to, y), r: price(q2.ask), f: baht(fe2) })); }
    }
    return { y: y, legs: legs, change: change };
  }
  function paintMoney() {
    $("wallet").innerHTML = MORDER.map(function (m) {
      var b = S.bal[m] || 0, q = MQ[m], line = "";
      if (m !== "THB") line = q ? t("bidask", { a: price(q.ask), b: price(q.bid) }) + " · " + (m === "USD" ? shop(q.bid_shop) : "Bitkub") : t("e_noprice");
      return "<li>" + mpic(m, 26) + '<span class="grow">' + t("m_" + m) + (line ? '<br><span class="mute small num">' + line + "</span>" : "") +
        '</span><span class="r">' + money(m, b) + (m !== "THB" && q ? '<br><span class="mute">' + baht(b * rate(m)) + "</span>" : "") + "</span></li>";
    }).join("");
    [["swF", swF], ["swT", swT]].forEach(function (g) {
      $(g[0]).querySelectorAll("button").forEach(function (b) { b.setAttribute("aria-pressed", b.dataset.m === g[1]); b.disabled = b.dataset.m !== "THB" && !MQ[b.dataset.m]; });
    });
    $("swCur").textContent = { THB: "฿", USD: "$", USDT: "₮", USDC: "$" }[swF];
    $("swAmt").setAttribute("aria-label", t("amount_in", { m: t("ms_" + swF) }));
    paintSwapSum(); paintRound();
  }
  function paintSwapSum() {
    var x = parse($("swAmt").value), el = $("swSum"), g = $("swGo");
    if (swF === swT) { el.textContent = t("same"); g.disabled = true; g.textContent = t("swap"); return; }
    var q = swapQuote(swF, swT, x);
    g.disabled = !q;
    g.textContent = t("swap_go", { a: money(swF, x || 0), m: t("ms_" + swT) });
    el.innerHTML = q ? q.legs.map(function (l) { return "<span>" + l + "</span>"; }).join("") + "<b>" + t("youget") + " " + money(swT, q.y, swT === "USD" ? 0 : null) + "</b>" : t("e_noprice");
  }
  function doSwap() {
    var x = parse($("swAmt").value);
    if (swF === swT) return toast(t("same"), "no");
    if (!(x > 0)) return toast(t("e_min", { min: money(swF, 1, 0) }), "no");
    if (x > (S.bal[swF] || 0) + 1e-6) return toast(t("e_bal", { m: t("ms_" + swF) }), "no");
    var q = swapQuote(swF, swT, Math.min(x, S.bal[swF]));
    if (!q) return toast(t("e_noprice"), "no");
    if (swT === "USD" && q.y < 1) return toast(t("e_min", { min: money("USD", 1, 0) }), "no");
    x = Math.min(x, S.bal[swF]);
    S.bal[swF] -= x; S.bal[swT] = (S.bal[swT] || 0) + q.y; S.bal.THB += q.change;
    record({ sym: "SWAP", side: "swap", from: swF, to: swT, x: x, y: q.y });
    toast(t("swapped", { a: money(swF, x), b: money(swT, q.y) }), "gold");
    chime(700, 940); medal("swap"); checkMedals(); save(); paint(); paintMoney();
  }
  function paintRound() {
    $("round").innerHTML = ["USD", "USDT", "USDC"].map(function (m) {
      var a = swapQuote("THB", m, 10000); if (!a) return "";
      var b = swapQuote(m, "THB", a.y); if (!b) return "";
      var back = b.y + a.change, loss = back - 10000;
      return "<li>" + mpic(m, 22) + '<span class="grow">฿10,000 → ' + money(m, a.y, m === "USD" ? 0 : null) + ' → ฿</span><span class="r">' + baht(back) + '<br><span class="' + cls(loss) + '">' + signed(loss) + "</span></span></li>";
    }).join("");
  }
  $("swF").addEventListener("click", function (e) { var b = e.target.closest("button"); if (!b || b.disabled) return; swF = b.dataset.m; if (swF === swT) swT = swF === "THB" ? "USDT" : "THB"; $("swAmt").value = fmt(Math.floor((S.bal[swF] || 0) * 0.1 * 100) / 100, 2); paintMoney(); });
  $("swT").addEventListener("click", function (e) { var b = e.target.closest("button"); if (!b || b.disabled) return; swT = b.dataset.m; if (swF === swT) swF = swT === "THB" ? "USDT" : "THB"; paintMoney(); });
  $("swFlip").addEventListener("click", function () { var a = swF; swF = swT; swT = a; paintMoney(); });
  $("swAmt").addEventListener("input", paintSwapSum);
  $("swAmt").addEventListener("keydown", function (e) { if (e.key === "Enter") doSwap(); });
  $("swChips").addEventListener("click", function (e) {
    var b = e.target.closest("button"); if (!b) return;
    var f = b.dataset.f === "all" ? 1 : b.dataset.f === "half" ? 0.5 : 0.1;
    $("swAmt").value = fmt(Math.floor((S.bal[swF] || 0) * f * 100) / 100, 2); paintSwapSum();
  });
  $("swGo").addEventListener("click", doSwap);
  $("tot").addEventListener("click", function () { S.show = S.show === "USD" ? "THB" : "USD"; save(); shownTotal = null; paint(); if (tab === "mine") paintMine(); });
  $("cashBtn").addEventListener("click", function () { showTab("money"); });

  // ---------------------------------------------------------------- toys
  var tmAmt = 10000;
  function paintToys() {
    $("rwP").textContent = t("rw_p", { coin: name(S.sel) });
    $("rwBest").textContent = S.best ? t("rw_best") + ": " + baht(S.best) : "";
    // monkey race
    var you = total(), mon = monkeyValue();
    if (mon != null) {
      var ry = (you / START - 1) * 100, rm = (mon / START - 1) * 100, span = Math.max(1, Math.abs(ry), Math.abs(rm)) * 1.25;
      function at(x) { return (50 + x / span * 38).toFixed(1) + "%"; }
      $("raceZero").style.left = "50%";
      $("runYou").style.left = at(ry); $("runMon").style.left = at(rm);
      $("runYouV").textContent = pct(ry); $("runYouV").className = cls(ry);
      $("runMonV").textContent = pct(rm); $("runMonV").className = cls(rm);
      $("race").setAttribute("aria-label", t("you") + " " + pct(ry) + ", " + t("monkey") + " " + pct(rm));
      $("monHas").textContent = t("monkey_has") + ": " + Object.keys(S.monkey.pos).map(function (s) { return name(s); }).join(", ") + " · " + day(S.monkey.at);
    }
    tmPaint();
  }
  function tmPaint() {
    var h = HC[S.sel + "/1Y"], out = $("tmOut"), q = Q[S.sel];
    if (!h) { hist(S.sel, "1Y").then(function () { if (tab === "toys") tmPaint(); }).catch(function () {}); out.textContent = t("loading"); return; }
    var sl = $("tm"); sl.max = Math.max(0, h.c.length - 1);
    if (tm == null) tm = 0;
    tm = Math.min(tm, h.c.length - 1); sl.value = tm;
    var nowPx = q ? q.bid : h.c[h.c.length - 1], v = tmAmt / h.c[tm] * nowPx, g = (v / tmAmt - 1) * 100;
    out.innerHTML = t("tm_p", { amt: baht(tmAmt), coin: name(S.sel), date: day(h.t[tm]), now: '<b class="' + cls(g) + '">' + baht(v) + " (" + pct(g) + ")</b>" });
  }
  $("tm").addEventListener("input", function () {
    tm = +this.value;
    if (S.range !== "1Y") { S.range = "1Y"; save(); loadHist(); }
    tmPaint(); draw();
  });
  $("tmAmt").addEventListener("click", function (e) {
    var b = e.target.closest("button"); if (!b) return; tmAmt = +b.dataset.a;
    this.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", x === b); }); tmPaint();
  });
  $("reset").addEventListener("click", function () {
    if (!confirm(t("reset_q"))) return;
    var keep = { fee: S.fee, sound: S.sound, sel: S.sel, range: S.range, best: S.best, pay: S.pay, show: S.show };
    S = fresh(); for (var k in keep) S[k] = keep[k];
    monkeyInit(); save(); shownTotal = null; paint(); paintMedals(); paintTrade();
  });

  // rewind: the last day of the selected coin, one 15-minute bar every 0.6 s
  var R = null;
  $("rwGo").addEventListener("click", function () {
    var sym = S.sel;
    hist(sym, "1D").then(function (h) {
      if (h.c.length < 20) return toast(t("e_chart"), "no");
      R = { sym: sym, t: h.t.slice(), c: h.c.slice(), i: 4, cash: 100000, q: 0, trades: [] };
      $("rwIdle").hidden = true; $("rwEnd").hidden = true; $("rwPlay").hidden = false;
      $("rwbadge").hidden = false; $("rwbar").hidden = false; $("cmsg").hidden = true;
      document.body.classList.add("rewinding");
      rwStep(); R.timer = setInterval(rwStep, 600);
    }).catch(function () { toast(t("e_chart"), "no"); });
  });
  function rwVal() { return R.cash + R.q * R.c[R.i]; }
  function rwStep() {
    if (!R) return;
    R.i++;
    if (R.i >= R.c.length - 1) { R.i = R.c.length - 1; return rwEnd(); }
    $("rwScore").textContent = baht(rwVal()) + "  " + pct((rwVal() / 100000 - 1) * 100);
    $("rwScore").className = "big num " + cls(rwVal() - 100000);
    $("rwbar").style.width = (R.i / (R.c.length - 1) * 100).toFixed(1) + "%";
    paintQuote(); draw();
  }
  function rwTrade(buy) {
    if (!R) return;
    var px = R.c[R.i];
    if (buy && R.cash > 1) { var f = feeOf(R.cash); R.q += (R.cash - f) / px; R.cash = 0; R.trades.push({ side: "buy", px: px, at: R.t[R.i] }); chime(660, 880); }
    else if (!buy && R.q > 0) { var g = R.q * px; R.cash += g - feeOf(g); R.q = 0; R.trades.push({ side: "sell", px: px, at: R.t[R.i] }); chime(880, 660); }
    draw();
  }
  function rwEnd() {
    clearInterval(R.timer);
    var you = rwVal(), hold = 100000 * (1 - S.fee / 100) * R.c[R.c.length - 1] / R.c[4] * (1 - S.fee / 100);
    $("rwEnd").innerHTML = t("rw_end", { you: '<b class="' + cls(you - 100000) + '">' + baht(you) + "</b>", hold: baht(hold) });
    $("rwEnd").hidden = false; $("rwPlay").hidden = true; $("rwIdle").hidden = false;
    $("rwbadge").hidden = true; $("rwbar").hidden = true; document.body.classList.remove("rewinding");
    if (you > S.best) S.best = Math.round(you);
    if (you > hold) rain(40);
    R = null; medal("rewind"); save(); paintQuote(); paintToys(); loadHist();
  }
  $("rwBuy").addEventListener("click", function () { rwTrade(true); });
  $("rwSell").addEventListener("click", function () { rwTrade(false); });
  $("rwStop").addEventListener("click", function () { if (R) { R.i = R.c.length - 1; rwEnd(); } });

  // ---------------------------------------------------------------- about
  $("fee").value = S.fee;
  $("fee").addEventListener("change", function () { var f = Math.max(0, Math.min(2, parseFloat(this.value) || 0)); this.value = f; S.fee = f; save(); paintSum(); });
  $("sound").checked = !!S.sound;
  $("sound").addEventListener("change", function () { S.sound = this.checked; save(); if (S.sound) chime(660, 990); });

  // ---------------------------------------------------------------- tabs
  var tab = "trade";
  function showTab(k) {
    tab = k;
    document.querySelectorAll(".tabs button").forEach(function (b) {
      var on = b.dataset.tab === k; b.setAttribute("aria-selected", on); b.tabIndex = on ? 0 : -1;
      $("p-" + b.dataset.tab).hidden = !on;
    });
    if (k !== "toys" && tm != null && !R) { tm = null; draw(); }
    if (k === "money") paintMoney();
    if (k === "mine") paintMine();
    if (k === "toys") paintToys();
    draw();
  }
  document.querySelector(".tabs").addEventListener("click", function (e) { var b = e.target.closest("button"); if (b) showTab(b.dataset.tab); });
  document.querySelector(".tabs").addEventListener("keydown", function (e) {
    if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
    var bs = Array.prototype.slice.call(this.querySelectorAll("button")), i = bs.findIndex(function (b) { return b.dataset.tab === tab; });
    var n = bs[(i + (e.key === "ArrowRight" ? 1 : bs.length - 1)) % bs.length]; showTab(n.dataset.tab); n.focus();
  });
  $("jar").addEventListener("click", function () { showTab("mine"); });

  // ---------------------------------------------------------------- toasts, sound, coins in the air
  function toast(msg, kind2) {
    var box = $("toasts"), el = document.createElement("div");
    el.className = "toast " + (kind2 || ""); el.textContent = msg; box.appendChild(el);
    while (box.children.length > 3) box.removeChild(box.firstChild);
    setTimeout(function () { if (el.parentNode) el.parentNode.removeChild(el); }, 4200);
  }
  var AC = null;
  function chime(a, b) {
    if (!S.sound) return;
    try {
      AC = AC || new (window.AudioContext || window.webkitAudioContext)();
      var o = AC.createOscillator(), g = AC.createGain(), n = AC.currentTime;
      o.type = "triangle"; o.frequency.setValueAtTime(a, n); o.frequency.exponentialRampToValueAtTime(b, n + 0.12);
      g.gain.setValueAtTime(0.0001, n); g.gain.exponentialRampToValueAtTime(0.12, n + 0.02); g.gain.exponentialRampToValueAtTime(0.0001, n + 0.32);
      o.connect(g); g.connect(AC.destination); o.start(n); o.stop(n + 0.35);
    } catch (e) {}
  }
  var fx = $("fx"), fc = fx.getContext("2d"), parts = [], fxOn = false;
  function fxSize() { fx.width = innerWidth * DPR; fx.height = innerHeight * DPR; }
  addEventListener("resize", fxSize); fxSize();
  function rain(n) {
    if (reduce) return;
    for (var i = 0; i < n; i++) parts.push({ x: Math.random() * innerWidth, y: -20 - Math.random() * innerHeight * 0.5, vx: (Math.random() - 0.5) * 1.5, vy: 2 + Math.random() * 3, r: 7 + Math.random() * 6, a: Math.random() * 6, va: (Math.random() - 0.5) * 0.3, coin: true, life: 1 });
    fxRun();
  }
  function confetti() {
    if (reduce) return;
    var cols = ["#2fd27f", "#ffb13b", "#5aa9ff", "#e8c15a", "#b69cff", "#ff6b6f"];
    for (var i = 0; i < 90; i++) {
      var ang = -Math.PI / 2 + (Math.random() - 0.5) * 1.6, sp = 6 + Math.random() * 7;
      parts.push({ x: innerWidth / 2, y: innerHeight * 0.55, vx: Math.cos(ang) * sp, vy: Math.sin(ang) * sp, r: 4 + Math.random() * 4, a: Math.random() * 6, va: (Math.random() - 0.5) * 0.5, col: cols[i % cols.length], life: 1 });
    }
    fxRun();
  }
  function pop(sym, px, s) {
    if (reduce || !geo || sym !== S.sel) return;
    var r = cv.getBoundingClientRect(), x = r.left + geo.X(Math.min(Date.now(), geo.t1)), y = r.top + geo.Y(px);
    for (var i = 0; i < 16; i++) { var a = i / 16 * Math.PI * 2; parts.push({ x: x, y: y, vx: Math.cos(a) * 3, vy: Math.sin(a) * 3, r: 3, a: 0, va: 0, col: s === "buy" ? "#2fd27f" : "#ffb13b", life: 1, fade: 0.04 }); }
    fxRun();
  }
  function fxRun() {
    if (fxOn) return; fxOn = true;
    (function frame() {
      fc.setTransform(DPR, 0, 0, DPR, 0, 0); fc.clearRect(0, 0, innerWidth, innerHeight);
      parts = parts.filter(function (p) {
        p.x += p.vx; p.y += p.vy; p.a += p.va;
        if (p.coin) p.vy += 0.12; else { p.vy += 0.18; p.vx *= 0.985; }
        p.life -= p.fade || 0.006;
        if (p.y > innerHeight + 30 || p.life <= 0) return false;
        fc.save(); fc.globalAlpha = Math.max(0, Math.min(1, p.life * 1.4)); fc.translate(p.x, p.y); fc.rotate(p.a);
        if (p.coin) {
          var sx = Math.abs(Math.cos(p.a * 1.7)) * 0.85 + 0.15;
          fc.scale(sx, 1); fc.beginPath(); fc.arc(0, 0, p.r, 0, 7); fc.fillStyle = "#e8c15a"; fc.fill();
          fc.lineWidth = 1.5; fc.strokeStyle = "#fff3c2"; fc.stroke();
          fc.fillStyle = "#7a5a10"; fc.font = "bold " + Math.round(p.r * 1.2) + "px system-ui"; fc.textAlign = "center"; fc.textBaseline = "middle"; fc.fillText("฿", 0, 1);
        } else { fc.fillStyle = p.col; fc.fillRect(-p.r / 2, -p.r / 4, p.r, p.r / 2); }
        fc.restore();
        return true;
      });
      if (parts.length) requestAnimationFrame(frame); else { fxOn = false; fc.clearRect(0, 0, innerWidth, innerHeight); }
    })();
  }

  // ---------------------------------------------------------------- start
  if (!COINS[S.sel]) S.sel = "BTC";
  if (!RANGES[S.range]) S.range = "1D";
  if (!S.bal) S = fresh();
  if (S.pay !== "USDT") S.pay = "THB";
  setAmt(S.pay === "USDT" ? 300 : 10000);
  $("swAmt").value = "10,000";
  paintStrip(false); paintMedals(); paintTrade(); paint(); size(); loadHist(); poll(); liveAge();
  var f = document.fonts && document.fonts.ready; if (f) f.then(draw);
})();
