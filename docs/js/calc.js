/* calc.js — the baht converter and the off-ramp calculator. Routes and default fees come from the
   page's #routes JSON; every fee is an editable field. MIT. */
(function () {
  var R = window.OFR = window.OFR || {}, t = R.t || function (e) { return e; }, TH = R.lang === "th";
  var rj = document.getElementById("routes"), routes = rj ? JSON.parse(rj.textContent) : null;
  var base = rj ? JSON.parse(document.getElementById("ratebase").textContent) : null;
  var rate = base ? { usdt_bid: base.usdt_bid, mid: base.mid, tt: base.tt, btc_bid: base.btc_bid, when: base.date + t(" (build)", " (ตอนสร้างหน้า)") } : null;
  function f(x, d) { return Number(x).toLocaleString("en-US", { minimumFractionDigits: d, maximumFractionDigits: d }); }
  function num(el) { var v = parseFloat(String(el.value).replace(/,/g, "")); return isFinite(v) ? v : 0; }

  // converter
  var ca = document.getElementById("cvamt"), cs = document.getElementById("cvasset"), co = document.getElementById("cvout");
  function conv() {
    if (!ca || !rate) return;
    var a = num(ca), k = cs.value, out;
    if (k === "usdt") out = "฿" + f(a * rate.usdt_bid, 2) + t(" at the Bitkub bid (", " ที่ราคารับซื้อ Bitkub (") + f(rate.usdt_bid, 2) + ")\n฿" + f(a * rate.mid, 2) + t(" at the Bank of Thailand mid (", " ที่อัตรากลาง ธปท. (") + f(rate.mid, 2) + ")";
    else if (k === "btc") out = "฿" + f(a * rate.btc_bid, 0) + t(" at the Bitkub bid (฿", " ที่ราคารับซื้อ Bitkub (฿") + f(rate.btc_bid, 0) + t(" per BTC)", " ต่อ BTC)") + "\n" + f(a * 1e8, 0) + " sats";
    else out = "฿" + f(a * rate.mid, 2) + t(" at the Bank of Thailand mid", " ที่อัตรากลาง ธปท.") + "\n฿" + f(a * rate.tt, 2) + t(" at the banks' average buying rate for a transfer", " ที่อัตรารับซื้อเงินโอนเฉลี่ยของธนาคาร");
    co.textContent = out + t("\nRates: ", "\nอัตรา: ") + rate.when;
  }
  if (ca) { ca.addEventListener("input", conv); cs.addEventListener("change", conv); }

  // calculator
  var box = document.getElementById("croutes"), bars = document.getElementById("cbars"), amt = document.getElementById("camt");
  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function build() {
    if (!box || !routes) return;
    box.innerHTML = routes.map(function (r, i) {
      var fields = Object.keys(r.fees).map(function (k) {
        var fd = r.fees[k];
        return '<div class="field" style="flex:1 1 9rem;margin:.3rem 0"><input data-r="' + i + '" data-k="' + k + '" inputmode="decimal" placeholder=" " value="' + fd.v + '" id="f' + i + k + '"><label for="f' + i + k + '">' + esc(TH && fd.label_th ? fd.label_th : fd.label) + "</label></div>";
      }).join("");
      return '<details class="cardx" style="margin:.6rem 0"' + (i < 2 ? " open" : "") + '><summary style="cursor:pointer"><b>' + esc(TH && r.label_th ? r.label_th : r.label) + '</b> <span class="small mute">' + esc(TH && r.needs_th ? r.needs_th : r.needs) + "</span></summary>" +
        '<div class="row">' + fields + '</div><p class="small mute" style="margin:.3rem 0 0">' + esc(TH && r.note_th ? r.note_th : r.note) + "</p></details>";
    }).join("");
    box.querySelectorAll("input").forEach(function (el) { el.addEventListener("input", calc); });
  }
  function val(i, k) { var el = document.getElementById("f" + i + k); return el ? num(el) : 0; }
  function calc() {
    if (!box || !routes || !rate) return;
    var a = num(amt), res = [];
    routes.forEach(function (r, i) {
      var q = 0, net = Math.max(0, a - val(i, "network_usdt"));
      if (r.kind === "exchange") q = net * rate.usdt_bid * (1 - val(i, "trade_pct") / 100) - val(i, "withdraw_thb");
      else if (r.kind === "card") {
        var g = net * (1 - val(i, "topup_pct") / 100) * rate.mid * (1 - val(i, "fx_pct") / 100);
        var per = val(i, "atm_max_thb") || 20000, n = Math.ceil(g / per);
        q = g - n * (val(i, "atm_thb") + val(i, "issuer_atm_thb")) - g * val(i, "issuer_atm_pct") / 100;
      } else if (r.kind === "wire") q = (net * (1 - val(i, "trade_pct") / 100) - val(i, "wire_usd")) * rate.tt - val(i, "receive_thb");
      else if (r.kind === "p2p") q = net * rate.usdt_bid * (1 + val(i, "spread_pct") / 100);
      res.push({ r: r, q: Math.max(0, q) });
    });
    var mx = Math.max.apply(null, res.map(function (x) { return x.q; }).concat([1])), ref = a * rate.mid;
    bars.innerHTML = res.map(function (x) {
      var w = (x.q / mx * 100).toFixed(1), d = ref ? (x.q / ref - 1) * 100 : 0;
      var col = x.r.kind === "p2p" ? "var(--red)" : x.r.kind === "card" ? "var(--blue)" : "var(--go)";
      return '<div style="margin:.45rem 0"><div class="row" style="justify-content:space-between"><span>' + esc(TH && x.r.label_th ? x.r.label_th : x.r.label) + '</span><b class="num">฿' + f(x.q, 0) +
        ' <span class="small mute">' + (d >= 0 ? "+" : "") + f(d, 2) + t('% vs mid', '% เทียบอัตรากลาง') + '</span></b></div><div style="height:.7rem;border-radius:6px;background:#121925"><div style="height:100%;width:' + w + '%;border-radius:6px;background:' + col + '"></div></div></div>';
    }).join("") + '<p class="small mute">' + t("Rates: ", "อัตรา: ") + esc(rate.when) + t(". A route's bar is the baht in hand after the fees in its fields.", " แท่งของแต่ละเส้นทางคือเงินบาทที่ได้รับหลังหักค่าธรรมเนียมในช่องของเส้นทางนั้น") + "</p>";
  }
  if (amt) amt.addEventListener("input", calc);
  document.addEventListener("ofr-rates", function (e) {
    var s = e.detail && e.detail.sources; if (!s || !rate) return;
    if (s.bitkub_usdt) rate.usdt_bid = s.bitkub_usdt.bid;
    if (s.bitkub_btc) rate.btc_bid = s.bitkub_btc.bid;
    if (s.bot) rate.mid = s.bot.usd_thb_mid;
    rate.when = t("live, ", "สด ") + new Date(s.bitkub_usdt ? s.bitkub_usdt.fetched_at : Date.now()).toLocaleString();
    conv(); calc();
  });
  build(); conv(); calc();
})();
