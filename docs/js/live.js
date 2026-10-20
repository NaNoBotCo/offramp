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
