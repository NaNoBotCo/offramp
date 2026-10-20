/* i18n.js — one switch for the page's scripts: OFR.t(english, thai). MIT. */
(function (G) {
  G.OFR = G.OFR || {};
  G.OFR.lang = (typeof document !== "undefined" && document.body && document.body.dataset.lang) || "en";
  G.OFR.t = function (en, th) { return G.OFR.lang === "th" && th ? th : en; };
})(typeof window !== "undefined" ? window : globalThis);
