# -*- coding: utf-8 -*-
"""figures.py — the charts, as inline SVG strings, from build/series.json and facts.json.

Each function returns an <svg> that site.py drops into the page, so the text in a chart
is text, the colours are the stylesheet's, and nothing is fetched.
"""
import datetime as dt, html, json, math, os, statistics as st

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILD = os.path.join(ROOT, "build")
E = html.escape
LANG = "en"


def L(en, th):
    return th if LANG == "th" else en

GO, AMBER, RED, BLUE, VIOLET, INK, MUTE, LINE = "#2fd27f", "#ffb13b", "#ff5a5f", "#5aa9ff", "#b69cff", "#eef2ef", "#98a3a9", "#1c2531"
CHAIN = {"Tron": "#ff5a5f", "Ethereum": "#8ea2ff", "BSC": "#f3ba2f", "Solana": "#19fb9b", "Base": "#2f6bff",
         "Arbitrum": "#28a0f0", "TON": "#34a6ff", "Plasma": "#c9a0ff", "Avalanche": "#e84142", "Polygon": "#8247e5",
         "Hyperliquid L1": "#97fce4"}


def load():
    return (json.load(open(os.path.join(BUILD, "series.json"))), json.load(open(os.path.join(BUILD, "facts.json"))))


def d2n(s):
    return dt.date.fromisoformat(s[:10]).toordinal()


def fmt_thb(v):
    if v >= 1e9: return "฿%.1fB" % (v / 1e9)
    if v >= 1e6: return "฿%.1fM" % (v / 1e6)
    if v >= 1e3: return "฿%.0fk" % (v / 1e3)
    if v >= 1: return "฿%.0f" % v
    return "฿%.2f" % v


class Chart:
    def __init__(self, w=1000, h=420, pad=(30, 150, 44, 16), title="", desc=""):
        self.w, self.h = w, h
        self.t, self.r, self.b, self.l = pad[0], pad[1], pad[2], pad[3] + 66
        self.parts = []
        self.title, self.desc = title, desc

    def frame(self, x0, x1, y0, y1, logy=False):
        self.x0, self.x1, self.y0, self.y1, self.logy = x0, x1, y0, y1, logy

    def X(self, x):
        return self.l + (x - self.x0) / (self.x1 - self.x0) * (self.w - self.l - self.r)

    def Y(self, y):
        if self.logy:
            y, a, b = math.log10(max(y, 1e-12)), math.log10(self.y0), math.log10(self.y1)
        else:
            a, b = self.y0, self.y1
        return self.h - self.b - (y - a) / (b - a) * (self.h - self.t - self.b)

    def add(self, s):
        self.parts.append(s)

    def ygrid(self, ticks, fmt):
        for v in ticks:
            y = self.Y(v)
            self.add('<line x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f" stroke="%s"/>' % (self.l, self.w - self.r, y, y, LINE))
            self.add('<text x="%.1f" y="%.1f" text-anchor="end" fill="%s" font-size="17">%s</text>' % (self.l - 8, y + 4, MUTE, E(fmt(v))))

    def xyears(self, y0, y1, step=1):
        for yr in range(y0, y1 + 1, step):
            x = self.X(dt.date(yr, 1, 1).toordinal())
            if self.l <= x <= self.w - self.r:
                self.add('<line x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f" stroke="%s" stroke-dasharray="2 4"/>' % (x, x, self.t, self.h - self.b, LINE))
                self.add('<text x="%.1f" y="%.1f" fill="%s" font-size="17">%d</text>' % (x + 4, self.h - self.b + 20, MUTE, yr))

    def line(self, pts, color, width=2, opacity=1, dash=""):
        if not pts: return
        d = "M" + " L".join("%.1f %.1f" % (self.X(x), self.Y(y)) for x, y in pts)
        da = ' stroke-dasharray="%s"' % dash if dash else ""
        self.add('<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-opacity="%s" stroke-linejoin="round"%s/>' % (d, color, width, opacity, da))

    def area(self, pts, color, opacity=.18, base=None):
        if not pts: return
        yb = self.Y(base if base is not None else self.y0)
        d = "M%.1f %.1f " % (self.X(pts[0][0]), yb) + " ".join("L%.1f %.1f" % (self.X(x), self.Y(y)) for x, y in pts) + " L%.1f %.1f Z" % (self.X(pts[-1][0]), yb)
        self.add('<path d="%s" fill="%s" fill-opacity="%s"/>' % (d, color, opacity))

    def band(self, lo, hi, color, opacity=.1):
        pts = [(x, y) for x, y in hi] + [(x, y) for x, y in reversed(lo)]
        d = "M" + " L".join("%.1f %.1f" % (self.X(x), self.Y(y)) for x, y in pts) + " Z"
        self.add('<path d="%s" fill="%s" fill-opacity="%s"/>' % (d, color, opacity))

    def mark(self, x, y, label, color=AMBER, dx=8, dy=-8, anchor="start"):
        self.add('<circle cx="%.1f" cy="%.1f" r="5" fill="%s" stroke="#05070c" stroke-width="2"/>' % (self.X(x), self.Y(y), color))
        self.add('<text x="%.1f" y="%.1f" fill="%s" font-size="18" text-anchor="%s" font-weight="600">%s</text>' % (self.X(x) + dx, self.Y(y) + dy, color, anchor, E(label)))

    def vline(self, x, label, color=GO):
        X = self.X(x)
        self.add('<line x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f" stroke="%s" stroke-width="1.5" stroke-dasharray="4 4"/>' % (X, X, self.t, self.h - self.b, color))
        self.add('<text x="%.1f" y="%.1f" fill="%s" font-size="16" transform="rotate(-90 %.1f %.1f)" text-anchor="end">%s</text>' % (X - 5, self.t + 4, color, X - 5, self.t + 4, E(label)))

    def hline(self, y, label, color=MUTE, dash="5 5"):
        Y = self.Y(y)
        self.add('<line x1="%.1f" x2="%.1f" y1="%.1f" y2="%.1f" stroke="%s" stroke-width="1.5" stroke-dasharray="%s"/>' % (self.l, self.w - self.r, Y, Y, color, dash))
        self.add('<text x="%.1f" y="%.1f" fill="%s" font-size="17">%s</text>' % (self.w - self.r + 6, Y + 4, color, E(label)))

    def legend(self, items, x=None, y=None):
        x = self.l + 10 if x is None else x
        y = self.t + 12 if y is None else y
        for i, (label, color) in enumerate(items):
            yy = y + i * 25
            self.add('<rect x="%.1f" y="%.1f" width="16" height="5" rx="2" fill="%s"/>' % (x, yy - 5, color))
            self.add('<text x="%.1f" y="%.1f" fill="%s" font-size="17" paint-order="stroke" stroke="#0f141e" stroke-width="4">%s</text>' % (x + 22, yy + 1, INK, E(label)))

    def svg(self):
        return ('<svg viewBox="0 0 %d %d" role="img" aria-labelledby="t d" font-family="DIN Alternate, Avenir Next, Sukhumvit Set, Thonburi, system-ui, sans-serif">'
                '<title>%s</title><desc>%s</desc>%s</svg>' % (self.w, self.h, E(self.title), E(self.desc), "".join(self.parts)))


def roll_median(pts, k=30):
    out = []
    for i in range(len(pts)):
        w = [p[1] for p in pts[max(0, i - k + 1):i + 1]]
        out.append((pts[i][0], st.median(w)))
    return out


# ------------------------------------------------------------------ charts
def btc_thb(S, F):
    pts = [(d2n(d), v) for d, v in S["btc_thb"]]
    c = Chart(title=L("Bitcoin in baht on Bitkub, daily close, since May 2018", "บิตคอยน์ในสกุลบาทบน Bitkub ราคาปิดรายวัน ตั้งแต่ พ.ค. 2018"),
              desc=L("A log-scale line from %s in May 2018 to %s today, peaking at %s on %s.", "เส้นสเกลลอการิทึมจาก %s เมื่อ พ.ค. 2018 ถึง %s วันนี้ สูงสุด %s เมื่อ %s") % (
                  fmt_thb(F["btc"]["first_thb"]), fmt_thb(F["btc"]["thb"]), fmt_thb(F["btc"]["ath_thb"]), F["btc"]["ath_date"]))
    c.frame(pts[0][0], pts[-1][0] + 20, 80000, 6e6, logy=True)
    c.ygrid([1e5, 2e5, 5e5, 1e6, 2e6, 5e6], fmt_thb)
    c.xyears(2019, dt.date.today().year)
    for d, n in F["supply"]["halvings"]:
        if d2n(d) > pts[0][0]:
            c.vline(d2n(d), L("halving", "halving"), GO)
    c.area(pts, AMBER, .10)
    c.line(pts, AMBER, 2.2)
    c.mark(d2n(F["btc"]["ath_date"]), F["btc"]["ath_thb"], L("high %s · %s", "สูงสุด %s · %s") % (fmt_thb(F["btc"]["ath_thb"]), F["btc"]["ath_date"]), AMBER, -10, -10, "end")
    c.mark(pts[-1][0], F["btc"]["thb"], fmt_thb(F["btc"]["thb"]), INK, 8, 18)
    return c.svg()


def premium(S, F):
    pts = [(d2n(d), max(-6, min(8, v))) for d, v in S["premium"]]
    med = roll_median([(d2n(d), v) for d, v in S["premium"]], 30)
    P = F["premium"]
    c = Chart(h=380, title=L("Bitcoin's price on Bitkub against the world price, in percent", "ราคาบิตคอยน์บน Bitkub เทียบราคาโลก เป็นเปอร์เซ็นต์"),
              desc=L("Daily difference between Bitkub's BTC/THB close and Binance's BTC/USDT close converted at the Bank of Thailand mid rate. Median %.2f%%; 80%% of days between %.2f%% and %.2f%%.",
                     "ส่วนต่างรายวันระหว่างราคาปิด BTC/THB บน Bitkub กับราคาปิด BTC/USDT บน Binance ที่แปลงด้วยอัตรากลางของ ธปท. มัธยฐาน %.2f%% และ 80%% ของวันอยู่ระหว่าง %.2f%% ถึง %.2f%%") % (P["median"], P["p10"], P["p90"]))
    c.frame(pts[0][0], pts[-1][0] + 20, -6, 8)
    c.ygrid([-6, -4, -2, 0, 2, 4, 6, 8], lambda v: "%+d%%" % v if v else "0")
    c.xyears(2019, dt.date.today().year)
    c.band([(pts[0][0], P["p10"]), (pts[-1][0], P["p10"])], [(pts[0][0], P["p90"]), (pts[-1][0], P["p90"])], GO, .07)
    c.line(pts, MUTE, 1, .45)
    c.line(med, AMBER, 2.4)
    c.hline(0, L("world price", "ราคาโลก"), INK, "0")
    c.legend([(L("each day", "รายวัน"), MUTE), (L("30-day median", "มัธยฐาน 30 วัน"), AMBER), (L("80% of days fall in the green band", "80% ของวันอยู่ในแถบสีเขียว"), GO)])
    return c.svg()


def usdt(S, F):
    raw = [(d2n(d), (u / b - 1) * 100) for d, u, m, b in S["usdt"]]
    mid = [(d2n(d), (m / b - 1) * 100) for d, u, m, b in S["usdt"]]
    pts = [(x, max(-3, min(6, y))) for x, y in raw]
    med = roll_median(raw, 30)
    U = F["usdt"]
    c = Chart(h=400, title=L("One USDT sold on Bitkub against one dollar bought by a Thai bank", "ขาย 1 USDT บน Bitkub เทียบธนาคารไทยรับซื้อ 1 ดอลลาร์"),
              desc=L("Percent more (or less) baht from selling USDT on Bitkub at the daily close than from the Thai banks' average buying rate for a dollar transfer. Median %+.2f%%; above the bank rate on %.1f%% of days.",
                     "เงินบาทที่ได้มากกว่า (หรือน้อยกว่า) เป็นเปอร์เซ็นต์ เมื่อขาย USDT บน Bitkub ที่ราคาปิด เทียบอัตรารับซื้อเงินโอนดอลลาร์เฉลี่ยของธนาคารไทย มัธยฐาน %+.2f%% สูงกว่าอัตราธนาคารใน %.1f%% ของวัน") % (U["vs_tt_median"], U["beat_tt_share"]))
    c.frame(pts[0][0], pts[-1][0] + 20, -3, 6)
    c.ygrid([-3, -2, -1, 0, 1, 2, 3, 4, 5, 6], lambda v: "%+d%%" % v if v else "0")
    c.xyears(2019, dt.date.today().year)
    c.line(pts, MUTE, 1, .4)
    c.line(mid, BLUE, 1.6, .9, "6 4")
    c.line(med, GO, 2.6)
    c.hline(0, L("bank buying rate", "อัตรารับซื้อธนาคาร"), INK, "0")
    c.legend([(L("USDT on Bitkub, each day", "USDT บน Bitkub รายวัน"), MUTE), (L("30-day median", "มัธยฐาน 30 วัน"), GO), (L("the interbank mid rate", "อัตรากลางระหว่างธนาคาร"), BLUE)])
    return c.svg()


def stable_total(S, F):
    pts = [(d2n(d), v / 1e9) for d, v in F["stable"]["hist"] if v > 0]
    pts = [p for p in pts if p[0] >= d2n("2017-01-01")]
    c = Chart(h=360, title=L("All stablecoins in circulation, US dollars", "สเตเบิลคอยน์ที่หมุนเวียนทั้งหมด ดอลลาร์สหรัฐ"),
              desc=L("Total supply of dollar-pegged stablecoins tracked by DefiLlama, from 2017 to %s: $%.0f billion today.", "ปริมาณสเตเบิลคอยน์ที่ผูกกับดอลลาร์ตามข้อมูล DefiLlama ตั้งแต่ 2017 ถึง %s: วันนี้ %.0f พันล้านดอลลาร์") % (F["fetched"]["llama_stable_total"]["at"][:10], F["stable"]["total_usd"] / 1e9))
    top = max(p[1] for p in pts) * 1.12
    c.frame(pts[0][0], pts[-1][0] + 20, 0, top)
    step = 50 if top > 200 else 25
    c.ygrid(list(range(0, int(top) + 1, step)), lambda v: "$%dB" % v)
    c.xyears(2018, dt.date.today().year)
    c.area(pts, GO, .16)
    c.line(pts, GO, 2.4)
    c.mark(pts[-1][0], pts[-1][1], "$%.0fB" % pts[-1][1], INK, -8, -12, "end")
    return c.svg()


def usdt_chains(S, F):
    H = F["stable"]["usdt_chain_hist"]
    chains = [c for c in ("Tron", "Ethereum", "BSC", "Solana", "TON", "Arbitrum", "Plasma", "Avalanche", "Polygon") if c in H]
    series = {c: {d2n(dt.datetime.utcfromtimestamp(int(t)).strftime("%Y-%m-%d")) // 7: v / 1e9 for t, v in H[c]} for c in chains}
    weeks = sorted(set().union(*[set(s) for s in series.values()]))
    weeks = [w for w in weeks if w * 7 >= d2n("2019-01-01")]
    c = Chart(h=400, title=L("Where USDT lives: supply by network", "USDT อยู่ที่ไหน: ปริมาณแยกตามเครือข่าย"),
              desc=L("USDT in circulation on each blockchain, weekly, from DefiLlama. Tron holds %.1f%% today.", "USDT ที่หมุนเวียนบนแต่ละบล็อกเชน รายสัปดาห์ จาก DefiLlama วันนี้ Tron ถือ %.1f%%") % F["stable"]["usdt_tron_share"])
    tops = [sum(series[ch].get(w, 0) for ch in chains) for w in weeks]
    top = max(tops) * 1.1
    c.frame(weeks[0] * 7, weeks[-1] * 7 + 20, 0, top)
    c.ygrid(list(range(0, int(top) + 1, 25)), lambda v: "$%dB" % v)
    c.xyears(2019, dt.date.today().year)
    base = [0.0] * len(weeks)
    layers = []
    for ch in chains:
        vals = [series[ch].get(w, 0) for w in weeks]
        top_ = [b + v for b, v in zip(base, vals)]
        layers.append((ch, list(base), top_))
        base = top_
    for ch, lo, hi in layers:
        c.band([(w * 7, y) for w, y in zip(weeks, lo)], [(w * 7, y) for w, y in zip(weeks, hi)], CHAIN.get(ch, MUTE), .75)
    c.legend([(ch, CHAIN.get(ch, MUTE)) for ch in chains])
    return c.svg()


def fees(S, F):
    bk = dict((d, v) for d, v in S["btc_thb"])
    ks = sorted(bk)
    pts = []
    import bisect
    for d, v in S["fees"]:
        if d < "2018-06-01": continue
        i = bisect.bisect_left(ks, d)
        if i >= len(ks): i = len(ks) - 1
        thb = v * F["fees"]["vb_typical"] * bk[ks[i]] / 1e8
        pts.append((d2n(d), max(thb, 0.05)))
    wk = roll_median(pts, 15)
    c = Chart(h=380, title=L("What a typical bitcoin payment paid in fees, in baht", "ค่าธรรมเนียมของการโอนบิตคอยน์ทั่วไป เป็นเงินบาท"),
              desc=L("Median fee rate per block (mempool.space) times a 141-vbyte payment, priced at the day's Bitkub close. Recent year median fee rate: %.1f sat/vB.", "อัตราค่าธรรมเนียมมัธยฐานต่อบล็อก (mempool.space) คูณการโอนขนาด 141 vbyte คิดที่ราคาปิด Bitkub วันนั้น มัธยฐานปีล่าสุด: %.1f sat/vB") % F["fees"]["median_last_year"])
    c.frame(pts[0][0], pts[-1][0] + 20, 0.3, 3000, logy=True)
    c.ygrid([1, 3, 10, 30, 100, 300, 1000, 3000], lambda v: "฿%d" % v)
    c.xyears(2019, dt.date.today().year)
    c.line(pts, MUTE, 1, .35)
    c.line(wk, AMBER, 2.4)
    last = wk[-1]
    c.mark(last[0], last[1], L("฿%.1f now", "฿%.1f ตอนนี้") % last[1], INK, -8, -14, "end")
    return c.svg()


def bars(rows, title, desc, color=AMBER, fmt=fmt_thb, w=1000, bh=30, label_w=150):
    h = 20 + len(rows) * (bh + 8)
    mx = max(v for _, v, *_ in rows)
    out = []
    for i, r in enumerate(rows):
        name, v = r[0], r[1]
        col = r[2] if len(r) > 2 else color
        y = 10 + i * (bh + 8)
        bw = (w - label_w - 150) * v / mx
        out.append('<text x="%d" y="%.1f" text-anchor="end" fill="%s" font-size="19">%s</text>' % (label_w - 10, y + bh * .7, INK, E(name)))
        out.append('<rect x="%d" y="%d" width="%.1f" height="%d" rx="6" fill="%s" fill-opacity=".85"/>' % (label_w, y, max(bw, 2), bh, col))
        out.append('<text x="%.1f" y="%.1f" fill="%s" font-size="18">%s</text>' % (label_w + bw + 8, y + bh * .7, MUTE, E(fmt(v))))
    return ('<svg viewBox="0 0 %d %d" role="img" aria-labelledby="t d" font-family="DIN Alternate, Avenir Next, Sukhumvit Set, Thonburi, system-ui, sans-serif"><title>%s</title><desc>%s</desc>%s</svg>'
            % (w, h, E(title), E(desc), "".join(out)))


def bitkub_board(S, F):
    rows = [(b["sym"], b["thb_vol"], GO if b["sym"] in ("USDT", "USDC", "RLUSD", "USD1") else AMBER) for b in F["bitkub"]["top"][:15]]
    return bars(rows, L("Bitkub: the most-traded pairs against baht, last 24 hours", "Bitkub: คู่ที่ซื้อขายกับเงินบาทมากที่สุด 24 ชั่วโมงล่าสุด"),
                L("Baht volume on Bitkub's own order book. USDT is %.1f%% of all baht volume.", "มูลค่าเป็นบาทในสมุดคำสั่งของ Bitkub เอง USDT คิดเป็น %.1f%% ของมูลค่าทั้งหมด") % F["bitkub"]["usdt_share"])


def world_caps(S, F):
    rows = [("%s" % c["sym"], c["cap_thb"], GO if c["sym"] in ("USDT", "USDC", "USDE", "DAI", "USDS", "USD1") else BLUE) for c in F["world"][:15]]
    return bars(rows, L("The largest coins by market value, in baht", "เหรียญที่มูลค่าตลาดสูงสุด ในสกุลบาท"),
                L("CoinGecko market capitalisation, priced in baht. Green bars are dollar stablecoins.", "มูลค่าตลาดจาก CoinGecko ในสกุลบาท แท่งสีเขียวคือสเตเบิลคอยน์ดอลลาร์"), fmt=lambda v: "฿%.2fT" % (v / 1e12) if v >= 1e12 else "฿%.0fB" % (v / 1e9))


def supply(S, F):
    # blocks every ten minutes on average; the dates past 2024 are that average, not a promise
    g = dt.date(2009, 1, 3).toordinal()
    pts = [(g, 0)]
    tot = 0
    for e in F["supply"]["eras"][:10]:
        start_h = e["era"] * 210000
        # use the real dates for the halvings that have happened
        real = {1: "2012-11-28", 2: "2016-07-09", 3: "2020-05-11", 4: "2024-04-20"}
        d_end = d2n(real[e["era"] + 1]) if (e["era"] + 1) in real else pts[-1][0] + int(210000 * 10 / 1440)
        tot = e["supply"]
        pts.append((d_end, tot / 1e6))
    c = Chart(h=360, title=L("Bitcoin's supply schedule: how many coins exist, and when", "ตารางอุปทานบิตคอยน์: มีกี่เหรียญ เมื่อไร"),
              desc=L("Coins mined, in millions, rising toward the cap of %s. Each era halves the reward; the dates after April 2024 assume ten-minute blocks.", "จำนวนเหรียญที่ขุดแล้ว หน่วยล้าน เพิ่มขึ้นสู่เพดาน %s แต่ละช่วงรางวัลลดครึ่ง วันที่หลังเมษายน 2024 สมมติบล็อกละสิบนาที") % "{:,.8f}".format(F["supply"]["cap"]))
    c.frame(g, dt.date(2045, 1, 1).toordinal(), 0, 22)
    c.ygrid([0, 5, 10, 15, 20, 21], lambda v: "%dM" % v)
    c.xyears(2010, 2044, 5)
    c.hline(21, L("21 million cap", "เพดาน 21 ล้าน"), GO)
    c.area(pts, AMBER, .12, 0)
    c.line(pts, AMBER, 2.4)
    today = dt.date.today().toordinal()
    c.vline(today, L("today", "วันนี้"), INK)
    return c.svg()


def fx(S, F):
    pts = [(d2n(d), v) for d, v in S["fx"] if v]
    c = Chart(h=320, title=L("US dollar in baht, Bank of Thailand reference rate", "ดอลลาร์สหรัฐในสกุลบาท อัตราอ้างอิงธนาคารแห่งประเทศไทย"),
              desc=L("Daily weighted-average interbank mid rate since August 2017. Low %.2f on %s, high %.2f on %s.", "อัตรากลางถัวเฉลี่ยระหว่างธนาคารรายวันตั้งแต่ ส.ค. 2017 ต่ำสุด %.2f เมื่อ %s สูงสุด %.2f เมื่อ %s") % (F["fx"]["min"][0], F["fx"]["min"][1], F["fx"]["max"][0], F["fx"]["max"][1]))
    c.frame(pts[0][0], pts[-1][0] + 20, 29, 39)
    c.ygrid([29, 31, 33, 35, 37, 39], lambda v: "฿%d" % v)
    c.xyears(2018, dt.date.today().year)
    c.line(pts, BLUE, 2)
    c.mark(pts[-1][0], pts[-1][1], "฿%.2f" % pts[-1][1], INK, -8, -12, "end")
    return c.svg()


def build():
    global LANG
    S, F = load()
    out = {}
    for LANG in ("en", "th"):
        out[LANG] = {fn.__name__: fn(S, F) for fn in (btc_thb, premium, usdt, stable_total, usdt_chains, fees, bitkub_board, world_caps, supply, fx)}
    LANG = "en"
    json.dump(out, open(os.path.join(BUILD, "figs.json"), "w"), ensure_ascii=False)
    return out


if __name__ == "__main__":
    o = build()
    print("  figures:", ", ".join("%s %dk" % (k, len(v) // 1000) for k, v in o["en"].items()))
