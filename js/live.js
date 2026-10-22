/* live.js — the board: reads the offrampt-rates worker and replaces the baked figures. MIT. */
(function () {
  var url = document.body.dataset.rates;
  window.OFR = window.OFR || {};
  if (!url || !window.fetch) return;
  OFR.rates = fetch(url, { cache: "no-store" }).then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; });
  function f(x, d) { return Number(x).toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d }); }
  var t = OFR.t || function (e) { return e; };
  OFR.rates.then(function (d) {
    if (!d || !d.sources) return;
    var s = d.sources, v = {};
    if (s.bitkub_usdt) v.usdt_bid = s.bitkub_usdt.bid;
    if (s.bot) v.bot_mid = s.bot.usd_thb_mid;
    if (s.bitkub_btc) v.btc_bid = s.bitkub_btc.bid;
    if (v.usdt_bid && v.bot_mid) v.usdt_prem = (v.usdt_bid / v.bot_mid - 1) * 100;
    var fmt = {
      usdt_bid: function (x) { return f(x, 2); }, bot_mid: function (x) { return f(x, 2); },
      usdt_prem: function (x) { return (x >= 0 ? "+" : "") + f(x, 2) + "%"; }, btc_bid: function (x) { return "฿" + f(x, 0); }
    };
    // USD cash at a money changer (sources.cash from baht-rates; data thairate.com, CC BY 4.0).
    var c = s.cash && s.cash.best, tick = document.querySelector(".tick");
    if (c) v.cash_usd = c.rate;
    fmt.cash_usd = function (x) { return f(x, 2); };
    if (c && tick && !tick.querySelector('[data-live="cash_usd"]')) {
      var sp2 = document.createElement("span"), b = document.createElement("b"), sm = document.createElement("small"), a = document.createElement("a");
      sp2.className = "cash";
      sp2.appendChild(document.createTextNode(t("USD cash at a money changer ฿", "เงินสด USD ที่ร้านแลกเงิน ฿")));
      b.setAttribute("data-live", "cash_usd"); sp2.appendChild(b);
      a.href = s.cash.source_url || "https://thairate.com/"; a.textContent = "thairate.com"; a.rel = "noopener";
      sm.appendChild(document.createTextNode(" " + c.shop + " · "));
      sm.appendChild(a); sm.appendChild(document.createTextNode(" (CC BY 4.0)"));
      sp2.appendChild(sm); tick.appendChild(sp2);
    }
    document.querySelectorAll("[data-live]").forEach(function (el) {
      var k = el.getAttribute("data-live");
      if (v[k] != null && fmt[k]) el.textContent = fmt[k](v[k]);
    });
    var st = document.getElementById("livestate"), sp = document.getElementById("livestamp");
    var ts = s.bitkub_usdt && new Date(s.bitkub_usdt.fetched_at), age = ts ? (Date.now() - ts) / 60000 : 1e9;
    if (st) { st.textContent = age < 60 ? t("live", "สด") : t("stale", "ค้าง"); st.classList.toggle("stale", age >= 60); }
    if (sp && ts) sp.textContent = t("Bitkub bid at ", "ราคารับซื้อ Bitkub เวลา ") + ts.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) +
      t(" (" + Math.round(age) + " min ago); Bank of Thailand rate for ", " (" + Math.round(age) + " นาทีที่แล้ว) อัตรา ธปท. ของวันที่ ") + (s.bot ? s.bot.period : "—") + t(". Refreshed every fifteen minutes.", " อัปเดตทุกสิบห้านาที");
    document.dispatchEvent(new CustomEvent("ofr-rates", { detail: d }));
  });
})();
