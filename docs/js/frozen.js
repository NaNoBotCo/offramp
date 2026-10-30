/* frozen.js — the counter on /frozen/: months of spending covered by the places that still pay out,
   with coins at full and at half price. Rows are added, removed and ticked in the page. MIT. */
(function () {
  var box = document.getElementById("fz");
  if (!box) return;
  var rows = box.querySelector(".fzrows"), tpl = document.getElementById("fzrow"), month = document.getElementById("fzm");
  var outs = box.querySelectorAll(".fzo"), MAXSQ = 36;
  var W = { months: box.dataset.months, month1: box.dataset.month1, need: box.dataset.need };

  function num(el) { var v = parseFloat(String(el.value).replace(/[^\d.]/g, "")); return isFinite(v) && v > 0 ? v : 0; }
  function fmt(x) { return Math.round(x).toLocaleString("en-US"); }
  function months(m) { return m >= 10 ? fmt(m) : (Math.floor(m * 10) / 10).toFixed(1).replace(/\.0$/, ""); }

  function squares(el, m) {
    var whole = Math.min(Math.floor(m), MAXSQ), part = m < MAXSQ && m - Math.floor(m) >= 0.1, h = "";
    for (var i = 0; i < whole; i++) h += "<i></i>";
    if (part) h += '<i class="part"></i>';
    if (m > MAXSQ) h += "<b>+" + fmt(m - MAXSQ) + "</b>";
    el.innerHTML = h;
  }

  function calc() {
    var spend = num(month), sums = [0, 0, 0];
    rows.querySelectorAll(".fzrow").forEach(function (r) {
      var a = num(r.querySelector(".fza")), k = r.querySelector(".fzk").value, frozen = r.querySelector(".fzf input").checked;
      var half = k === "bank" ? a : a / 2;
      if (!frozen) { sums[0] += a; sums[1] += half; if (k !== "ex") sums[2] += half; }
    });
    outs.forEach(function (o, i) {
      var v = o.querySelector(".v"), sq = o.querySelector(".fzsq");
      if (!spend) { v.textContent = i === 0 ? W.need : "—"; sq.innerHTML = ""; return; }
      var m = sums[i] / spend;
      v.textContent = months(m) + " " + (m === 1 ? W.month1 : W.months) + " · ฿" + fmt(sums[i]);
      squares(sq, m);
    });
  }

  function tidy(e) {
    var el = e.target;
    if (el.classList && (el.classList.contains("fza") || el.id === "fzm")) {
      var v = num(el);
      el.value = v ? fmt(v) : "";
    }
  }

  box.addEventListener("input", calc);
  box.addEventListener("change", function (e) { tidy(e); calc(); });
  box.addEventListener("focusout", tidy);
  box.addEventListener("click", function (e) {
    var x = e.target.closest(".fzx");
    if (x) { x.closest(".fzrow").remove(); calc(); return; }
    if (e.target.closest(".fzadd") && tpl) {
      rows.appendChild(tpl.content.cloneNode(true));
      var added = rows.lastElementChild && rows.lastElementChild.querySelector(".fzn");
      if (added) added.focus();
      calc();
    }
  });
  calc();
})();
