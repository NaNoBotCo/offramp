#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""intel.py — Offrampt's intel: dated notes, trends computed from the data at each build, and
the services of Hongdam, Chiang Mai Visa Desk and Mot Dang.

    data/intel/notes/<date>-<slug>.json   one note, English and Thai (format in data/intel/brief.md)
    data/ours.json                        sister services; Hongdam prices read live from its API

site.py calls prepare(S) before the pages, build(S) after them (when every page that a note can
link to exists), and home blocks from home(). S is the site module: T, U, E, page, sign, LANG.

Writes /intel/, /intel/<slug>/, /intel/feed.xml, /intel/notes.json and the Thai pages under /th/.
Notes already published on the live site are read back from its notes.json and kept, so a build
from an older checkout keeps them (INTEL_OFFLINE=1 skips that).
"""
from __future__ import annotations

import json
import math
import os
import re
import statistics as st
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTES = ROOT / "data" / "intel" / "notes"
OURS = ROOT / "data" / "ours.json"
RAW = ROOT / "data" / "raw"
BUILD = ROOT / "build"
HONGDAM_API = "https://hongdam.net/api/services"

KINDS = {  # kind: English, Thai, colour class
    "hack": ("Hack", "การแฮ็ก", "red"),
    "long": ("Long view", "มองยาว", "violet"),
    "market": ("Market", "ตลาด", "blue"),
    "rule": ("Rules", "กฎ", "amber"),
    "bank": ("Banks", "ธนาคาร", "go"),
    "scam": ("Scams", "กลโกง", "red"),  # stylecheck: allow — topic label
}
SHAPES = {  # shape: English, Thai
    "rising": ("Rising", "ขาขึ้น"),
    "falling": ("Falling", "ขาลง"),
    "flat": ("Flat", "ทรงตัว"),
    "peak": ("Past its peak", "ผ่านจุดสูงสุดแล้ว"),
    "trough": ("Past its low", "ผ่านจุดต่ำสุดแล้ว"),
    "step-down": ("Sudden drop", "ร่วงฉับพลัน"),
    "step-up": ("Sudden jump", "พุ่งฉับพลัน"),
    "s-curve": ("Slow, then sudden", "ช้า แล้วจู่ๆ ก็เร็ว"),
    "steps": ("Step by step", "ทีละขั้น"),
}
SPEEDS = {"hours": ("hours", "ชั่วโมง"), "days": ("days", "วัน"), "weeks": ("weeks", "สัปดาห์"),
          "months": ("months", "เดือน"), "years": ("years", "ปี"), "decades": ("decades", "ทศวรรษ")}

STATE = {"notes": [], "signals": [], "ours": []}


# ------------------------------------------------------------------ reading a trend
def _iso(d):
    """'2013-07' or '2013' read as the first day"""
    d = str(d)[:10]
    return date.fromisoformat(d + "-01-01"[len(d) - 4:] if len(d) < 10 else d)


def _days(a, b):
    return (_iso(b) - _iso(a)).days


def trend(points, log=True):
    """points: [(iso date, value)], oldest first. The shape of the run, and its speed as a
    doubling or halving time (log=True) or a change per month in points (log=False)."""
    pts = [(d, v) for d, v in points if v is not None and (v > 0 or not log)]
    if len(pts) < 6:
        return None
    f = (lambda v: math.log(v)) if log else (lambda v: v)
    n = len(pts)
    thirds = [pts[: n // 3 + 1], pts[n // 3: 2 * n // 3 + 1], pts[2 * n // 3:]]

    def slope(seg):  # per day, least squares
        xs = [_days(pts[0][0], d) for d, _ in seg]
        ys = [f(v) for _, v in seg]
        mx, my = st.mean(xs), st.mean(ys)
        den = sum((x - mx) ** 2 for x in xs) or 1
        return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den

    s = [slope(t) for t in thirds]
    whole = slope(pts)
    span = max(_days(pts[0][0], pts[-1][0]), 1)
    total = f(pts[-1][1]) - f(pts[0][1])
    ys = [f(v) for _, v in pts]
    hi, lo = max(ys), min(ys)
    rng = (hi - lo) or 1e-9
    i_hi, i_lo = ys.index(hi), ys.index(lo)
    jumps = [abs(ys[i + 1] - ys[i]) for i in range(n - 1)]
    flat_cut = 0.03 if log else 0.25 * (st.pstdev(ys) or 1)
    if abs(total) < flat_cut and rng < 2.5 * flat_cut:
        shape = "flat"
    elif max(jumps) > 0.6 * rng and abs(total) > 0.5 * rng:
        shape = "step-up" if total > 0 else "step-down"
    elif s[0] > 0 and s[2] < 0 and 0.15 * n < i_hi < 0.9 * n and (hi - ys[-1]) > 0.25 * rng:
        shape = "peak"
    elif s[0] < 0 and s[2] > 0 and 0.15 * n < i_lo < 0.9 * n and (ys[-1] - lo) > 0.25 * rng:
        shape = "trough"
    else:
        shape = "rising" if whole > 0 else "falling"
    recent = s[2] if shape in ("peak", "trough") else whole
    out = {"shape": shape, "from": pts[0][0], "to": pts[-1][0], "first": pts[0][1], "last": pts[-1][1],
           "change": (pts[-1][1] / pts[0][1] - 1) * 100 if log and pts[0][1] else pts[-1][1] - pts[0][1],
           "days": span, "pts": pts}
    if log and recent:
        months = math.log(2) / abs(recent) / 30.44
        out["double_months"] = months
        out["per_month"] = (math.exp(recent * 30.44) - 1) * 100
        out["speed"] = "weeks" if months < 2 else "months" if months < 18 else "years" if months < 120 else "decades"
    else:
        out["per_month"] = recent * 30.44
        out["speed"] = "months"
    return out


def spark(pts, w=132, h=34, cls="spark"):
    """a small line of the data itself (no arrowhead; a falling line is the data)"""
    if not pts or len(pts) < 2:
        return ""
    xs = [_days(pts[0][0], d) for d, _ in pts]
    ys = [v for _, v in pts]
    x0, x1, y0, y1 = min(xs), max(xs) or 1, min(ys), max(ys)
    sy = (y1 - y0) or 1
    p = " ".join(f"{2 + (x - x0) / ((x1 - x0) or 1) * (w - 6):.1f},{h - 3 - (y - y0) / sy * (h - 6):.1f}" for x, y in zip(xs, ys))
    lx, ly = p.split(" ")[-1].split(",")
    return (f'<svg class="{cls}" viewBox="0 0 {w} {h}" width="{w}" height="{h}" aria-hidden="true" focusable="false">'
            f'<polyline points="{p}" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>'
            f'<circle cx="{lx}" cy="{ly}" r="3" fill="currentColor"/></svg>')


GLYPH = {  # an idealised run for a note with no series of its own
    "rising": "4,28 40,20 76,13 112,6", "falling": "4,6 40,13 76,20 112,28", "flat": "4,17 40,16 76,18 112,17",
    "peak": "4,28 36,12 58,6 80,12 112,22", "trough": "4,6 36,22 58,28 80,22 112,12",
    "step-down": "4,8 54,8 60,27 112,27", "step-up": "4,27 54,27 60,8 112,8",
    "s-curve": "4,29 40,28 64,25 80,16 94,7 112,5", "steps": "4,28 28,28 28,21 56,21 56,14 84,14 84,7 112,7",
}


def glyph(shape, w=116, h=34):
    pts = GLYPH.get(shape)
    if not pts:
        return ""
    return (f'<svg class="spark" viewBox="0 0 116 34" width="{w}" height="{h}" aria-hidden="true" focusable="false">'
            f'<polyline points="{pts}" fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="1 0" stroke-linejoin="round" stroke-linecap="round"/></svg>')


# ------------------------------------------------------------------ the computed trends
def _raw(name):
    p = RAW / name
    return json.loads(p.read_text(encoding="utf-8"))["data"] if p.exists() else None


def signals(F, SER, rules):
    """five trends computed from the build's data: (id, en, th, value, note_en, note_th, trend, href, src)"""
    out = []
    today = F["usdt"]["last"]["date"]
    # 1. bitcoin in baht, 90 days
    b = [(d, v) for d, v in SER.get("btc_thb", []) if _days(d, today) <= 90]
    t = trend(b)
    if t:
        out.append(dict(id="btc", en="Bitcoin in baht, 90 days", th="บิตคอยน์เป็นบาท 90 วัน", t=t, href="markets/", src="bitkub",
                        value=f'฿{t["last"]:,.0f}', note_en=f'{t["change"]:+.1f}% since {t["from"]}', note_th=f'{t["change"]:+.1f}% ตั้งแต่ {t["from"]}'))
    # 2. USDT sold on Bitkub against the banks' dollar-transfer rate, 90 days
    u = [(d, (bk / tt - 1) * 100) for d, bk, mid, tt in SER.get("usdt", []) if tt and _days(d, today) <= 90]
    t = trend(u, log=False)
    if t:
        med = F["usdt"]["vs_tt_median"]
        last30 = st.median([v for d, v in u if _days(d, today) <= 30]) if u else 0
        out.append(dict(id="usdt", en="USDT against a bank wire", th="USDT เทียบเงินโอนผ่านธนาคาร", t=t, href="markets/", src="bitkub",
                        value=f"{last30:+.2f}%", note_en=f"median of the last 30 days; {med:+.2f}% median since {F['usdt']['from'][:4]}",
                        note_th=f"ค่ามัธยฐาน 30 วันล่าสุด ค่ามัธยฐานตั้งแต่ {F['usdt']['from'][:4]} คือ {med:+.2f}%"))
    # 3. dollar stablecoins in circulation worldwide, 1 year
    s = _raw("llama_stable_total.json") or []
    sp = []
    for r in s:
        d = datetime.fromtimestamp(int(r["date"]), timezone.utc).date().isoformat()
        v = (r.get("totalCirculatingUSD") or {}).get("peggedUSD")
        if v and _days(d, today) <= 365:
            sp.append((d, v))
    top = max(sp, key=lambda x: x[1]) if sp else None
    sp = sp[::7] + ([sp[-1]] if sp and sp[::7][-1] != sp[-1] else [])
    t = trend(sp)
    if t:
        out.append(dict(id="stable", en="Dollar stablecoins, 1 year", th="สเตเบิลคอยน์ดอลลาร์ 1 ปี", t=t, href="networks/", src="llama",
                        value=f'${t["last"] / 1e9:,.0f}B', note_en=f'${t["first"] / 1e9:,.1f}B a year ago; high ${top[1] / 1e9:,.1f}B on {top[0]}',
                        note_th=f'${t["first"] / 1e9:,.1f}B เมื่อปีก่อน สูงสุด ${top[1] / 1e9:,.1f}B เมื่อ {top[0]}'))
    # 4. bitcoin's hashrate, 3 years: guesses a second at the SHA-256 puzzle
    h = _raw("mempool_hashrate_3y.json")
    if h:
        hp = [(datetime.fromtimestamp(x["timestamp"], timezone.utc).date().isoformat(), x["avgHashrate"]) for x in h.get("hashrates", [])]
        hp = hp[::14] + ([hp[-1]] if hp and hp[::14][-1] != hp[-1] else [])
        t = trend(hp)
        if t:
            out.append(dict(id="hash", en="Bitcoin's guesses a second, 3 years", th="จำนวนการเดาต่อวินาทีของบิตคอยน์ 3 ปี", t=t, href="how/", src="mempool",
                            value=f'{t["last"] / 1e18:,.0f} EH/s',
                            note_en=f'{t["last"] / 1e18:,.0f} quintillion SHA-256 guesses a second; {t["first"] / 1e18:,.0f} on {t["from"]}',
                            note_th=f'เดา SHA-256 {t["last"] / 1e18:,.0f} ล้านล้านล้านครั้งต่อวินาที เทียบกับ {t["first"] / 1e18:,.0f} เมื่อ {t["from"]}'))
    # 5. Thai crypto rule changes: how often a new one lands
    tl = sorted(e["date"] for e in (rules.get("timeline") or []) if e.get("date") and e["date"] <= today)
    year = [d for d in tl if _days(d, today) <= 365]
    if len(year) >= 3:
        cum = []
        start = date.fromisoformat(today) - timedelta(days=365)
        for i in range(13):
            m = (start + timedelta(days=30.4 * i)).isoformat()
            cum.append((m, sum(1 for d in year if d <= m)))
        every = 365 / len(year) / 7
        t = {"shape": "steps", "speed": "weeks", "pts": cum, "last": len(year)}
        out.append(dict(id="rules", en="Thai crypto rule changes, 12 months", th="กฎคริปโตของไทยที่เปลี่ยน 12 เดือน", t=t, href="rules/", src="rules",
                        value=f"{len(year)}", note_en=f"one about every {every:.0f} weeks; latest {year[-1]}",
                        note_th=f"ราวทุก {every:.0f} สัปดาห์ ล่าสุด {year[-1]}"))
    return out


def speed_text(S, t):
    """a run under about a year: '% a month' (points a month for a spread); longer: 'doubles in about 2.6 years'"""
    if t["shape"] == "flat":
        return S.T("no clear direction", "ยังไม่มีทิศทางชัด")
    if t["shape"] == "steps":
        return S.T(*SPEEDS.get(t.get("speed", "months"), ("months", "เดือน")))
    pm = t.get("per_month", 0)
    if "double_months" not in t:
        return S.T(f"{pm:+.2f} points a month", f"{pm:+.2f} จุดต่อเดือน")
    if t.get("days", 0) < 400:
        return S.T(f"{'up' if pm > 0 else 'down'} about {abs(pm):.0f}% a month", f"{'ขึ้น' if pm > 0 else 'ลง'}ราว {abs(pm):.0f}% ต่อเดือน")
    m = t["double_months"]
    grow = pm > 0
    n = f"{m:.0f} months" if m < 24 else f"{m / 12:.1f} years"
    nt = f"{m:.0f} เดือน" if m < 24 else f"{m / 12:.1f} ปี"
    return S.T(f"{'doubles' if grow else 'halves'} in about {n}", f"{'เพิ่มเป็นสองเท่า' if grow else 'ลดลงครึ่งหนึ่ง'}ในราว {nt}")


def shape_word(S, shape):
    return S.T(*SHAPES.get(shape, (shape, shape)))


# ------------------------------------------------------------------ notes
def _read_local():
    out = []
    for p in sorted(NOTES.glob("*.json")):
        n = json.loads(p.read_text(encoding="utf-8"))
        n.setdefault("id", p.stem)
        out.append(n)
    return out


def _read_live(site_url):
    if os.environ.get("INTEL_OFFLINE") == "1":
        return []
    try:
        req = urllib.request.Request(site_url.rstrip("/") + "/intel/notes.json", headers={"User-Agent": "offrampt-build"})
        with urllib.request.urlopen(req, timeout=8) as r:
            return json.loads(r.read().decode("utf-8")).get("notes", [])
    except Exception:
        return []


def _read_ours():
    ours = json.loads(OURS.read_text(encoding="utf-8")).get("items", []) if OURS.exists() else []
    live = {}
    if os.environ.get("INTEL_OFFLINE") != "1":
        try:
            req = urllib.request.Request(HONGDAM_API, headers={"User-Agent": "offrampt-build"})
            with urllib.request.urlopen(req, timeout=8) as r:
                live = {k["id"]: k for k in json.loads(r.read().decode("utf-8")).get("kinds", [])}
        except Exception:
            live = {}
    for o in ours:
        k = live.get(o.get("hongdam_id") or "")
        if k and k.get("price"):
            o["price"] = k["price"]
    return ours


def _url_ok(u):
    if os.environ.get("INTEL_OFFLINE") == "1":
        return False
    try:
        req = urllib.request.Request(u, method="HEAD", headers={"User-Agent": "offrampt-build"})
        with urllib.request.urlopen(req, timeout=8) as r:
            return r.status == 200
    except Exception:
        return False


def prepare(S):
    """read the notes, compute the trends, price the services; before any page is written"""
    local = _read_local()
    have = {n["id"] for n in local}
    live = [n for n in _read_live(S.SITE_URL) if n.get("id") not in have]
    notes = [n for n in local + live if not n.get("retired") and n.get("date", "9999") <= S.TODAY]
    notes.sort(key=lambda n: (n["date"], n.get("order", 0)), reverse=True)
    STATE["notes"] = notes
    STATE["live_kept"] = [n["id"] for n in live]
    STATE["signals"] = signals(S.F, json.loads((BUILD / "series.json").read_text(encoding="utf-8")), S.R["rules"])
    ours = _read_ours()
    STATE["ours"] = [o for o in ours if not o.get("check") or _url_ok(o["href_en"])]


def _f(S, n, k):
    return (n.get(k + "_th") if S.LANG == "th" else None) or n.get(k + "_en") or ""


def slug(n):
    return re.sub(r"^\d{4}-\d{2}-\d{2}-", "", n["id"])


def _exists(S, href):
    """an internal page this build wrote; outside links pass"""
    if href.startswith(("http://", "https://")):
        return True
    p = S.SITE / ("th" if S.LANG == "th" else "") / href.split("#")[0]
    return (p / "index.html").exists() or p.is_file()


def _href(S, href):
    return href if href.startswith(("http://", "https://")) else S.U(href)


def _link_href(S, lk):
    return (lk.get("href_th") if S.LANG == "th" else None) or lk.get("href") or lk.get("href_en", "")


def kind_pill(S, n):
    en, th, c = KINDS.get(n.get("kind", ""), ("Intel", "ข่าวกรอง", ""))
    return f'<span class="pill {c}">{S.E(S.T(en, th))}</span>'


def _trend_line(S, n):
    if not n.get("shape"):
        return ""
    sp = SPEEDS.get(n.get("speed", ""), None)
    sw = S.T(*sp) if sp else ""
    g = _sig(n)
    pic = spark(g["t"]["pts"], 84, 26) if g else glyph(n["shape"], 84, 26)
    return (f'<span class="shp">{pic}<span><b>{S.E(shape_word(S, n["shape"]))}</b>'
            + (f' · {S.E(sw)}' if sw else "") + "</span></span>")


def _sig(n):
    return next((g for g in STATE["signals"] if g["id"] == n.get("signal")), None)


def note_card(S, n, lead=False):
    return (f'<a class="ncard{" lead" if lead else ""}" href="{S.U("intel/" + slug(n) + "/")}">'
            f'<span class="nmeta">{kind_pill(S, n)}<time datetime="{n["date"]}">{n["date"]}</time></span>'
            f'<b>{S.E(_f(S, n, "title"))}</b><span class="ndek">{S.E(_f(S, n, "dek"))}</span>'
            f'{_trend_line(S, n)}</a>')


def signal_row(S, g):
    t = g["t"]
    return (f'<a class="sig" href="{S.U(g["href"])}"><span class="sk">{S.E(S.T(g["en"], g["th"]))}</span>'
            f'<span class="sv">{S.E(g["value"])}</span>{spark(t["pts"])}'
            f'<span class="ss"><b>{S.E(shape_word(S, t["shape"]))}</b> · {S.E(speed_text(S, t))}</span>'
            f'<span class="sn">{S.E(S.T(g["note_en"], g["note_th"]))}</span></a>')


def signals_block(S, full=False):
    rows = "".join(signal_row(S, g) for g in STATE["signals"])
    if not rows:
        return ""
    when = S.F["usdt"]["last"]["date"]
    return (f'<div class="sigs{" full" if full else ""}">{rows}</div><p class="stamp">'
            + S.T(f"Computed from the data on {when}, at each build. Shape and speed read from the run itself; the line is the data.",
                  f"คำนวณจากข้อมูลวันที่ {when} ทุกครั้งที่สร้างหน้า รูปทรงและความเร็วอ่านจากข้อมูลชุดนั้นเอง เส้นคือข้อมูลจริง")
            + "</p>")


def lead_strip(S):
    """the newest note marked lead, while its date holds"""
    for n in STATE["notes"]:
        lu = n.get("lead_until")
        if lu and lu >= S.TODAY:
            lk = next((lk for lk in n.get("links", []) if lk.get("lead") and _exists(S, _link_href(S, lk))), None)
            href = _href(S, _link_href(S, lk)) if lk else S.U("intel/" + slug(n) + "/")
            label = S.T(lk["en"], lk["th"]) if lk else S.T("Read", "อ่าน")
            return (f'<a class="leadstrip" href="{href}"><span class="live">{S.E(S.T("now", "ตอนนี้"))}</span>'
                    f'<span>{S.E(_f(S, n, "title"))}</span><b>{S.E(label)}{S.ARROW}</b></a>')
    return ""


def latest(S, k=4):
    return "".join(note_card(S, n, lead=(i == 0)) for i, n in enumerate(STATE["notes"][:k]))


def ours_cards(S, k=6):
    out = []
    for o in STATE["ours"][:k]:
        href = o["href_th"] if S.LANG == "th" else o["href_en"]
        price = (f'฿{o["price"]:,}' if o.get("price") else S.T(o.get("price_en", ""), o.get("price_th", "")))
        out.append(f'<a class="our" href="{S.E(href)}" rel="noopener"><span class="otop"><span class="osite">{S.E(o["site"])}</span>'
                   f'<span class="oprice">{S.E(price)}{S.ARROW}</span></span>'
                   f'<b>{S.E(S.T(o["en"], o["th"]))}</b><span class="oline">{S.E(S.T(o["line_en"], o["line_th"]))}</span></a>')
    return "".join(out)


# ------------------------------------------------------------------ pages
def _sources(S, n):
    items = []
    for s in n.get("sources", []):
        bits = [S.E(s.get("title", "")), S.E(s.get("publisher", "")), S.E(s.get("date", ""))]
        t = " · ".join(b for b in bits if b)
        items.append(f'<li><a href="{S.E(s["url"])}" rel="noopener">{t}</a></li>' if s.get("url") else f"<li>{t}</li>")
    return (f'<h2>{S.T("Sources", "แหล่งที่มา")}</h2><ol class="srcs">{"".join(items)}</ol>') if items else ""


def _links(S, n):
    lk = [x for x in n.get("links", []) if _exists(S, _link_href(S, x))]
    if not lk:
        return ""
    a = "".join(f'<a class="nl{" ext" if _link_href(S, x).startswith("http") else ""}" href="{S.E(_href(S, _link_href(S, x)))}">'
                f'{S.E(S.T(x["en"], x["th"]))}{S.ARROW}</a>' for x in lk)
    return f'<h2>{S.T("Where to next", "ไปต่อที่ไหน")}</h2><div class="nlinks">{a}</div>'


def follow(S, compact=False):
    feed = S.U("intel/feed.xml")
    pat = S.SUPPORT.get("patreon")
    btns = (f'<a class="btn" href="{feed}" type="application/atom+xml">{S.T("Feed (RSS)", "ฟีด (RSS)")}</a>'
            + (f'<a class="btn" href="{S.E(pat)}" rel="noopener" target="_blank">{S.T("Patreon", "Patreon")}</a>' if pat else "")
            + f'<button class="btn share" type="button" data-share>{S.T("Share", "แชร์")}</button>')
    return (f'<section class="follow panel" id="follow"><h3>{S.T("Follow the intel", "ติดตามข่าวกรอง")}</h3>'
            f'{S.subscribe_form("offrampt-intel")}<div class="row fbtns">{btns}</div></section>')


SHARE_JS = """<script>(function(){document.querySelectorAll('[data-share]').forEach(function(b){b.addEventListener('click',function(){
var u=b.getAttribute('data-url')||location.href,t=document.title;if(navigator.share){navigator.share({title:t,url:u}).catch(function(){});return}
if(navigator.clipboard){navigator.clipboard.writeText(u).then(function(){b.textContent=b.getAttribute('data-done')||'✓'})}})})})();</script>"""


def note_page(S, n):
    paras = n.get("body_th") if S.LANG == "th" and n.get("body_th") else n.get("body_en", [])
    body_p = "".join(f"<p>{S.E(p)}</p>" for p in paras)
    quote = ""
    if n.get("quote_en"):
        quote = (f'<blockquote class="nq"><p>{S.E(_f(S, n, "quote"))}</p>'
                 f'<cite>{S.E(_f(S, n, "quote_by"))}</cite></blockquote>')
    read = _f(S, n, "read")
    trend_box = ""
    if n.get("shape"):
        sp = SPEEDS.get(n.get("speed", ""))
        g = _sig(n)
        pic = spark(g["t"]["pts"], 160, 46) if g else glyph(n["shape"], 160, 46)
        trend_box = (f'<div class="nread panel"><div class="shp big">{pic}<span>'
                     f'<b>{S.E(S.T("Shape", "รูปทรง"))}: {S.E(shape_word(S, n["shape"]))}</b>'
                     + (f'<br><b>{S.E(S.T("Speed", "ความเร็ว"))}: {S.E(S.T(*sp))}</b>' if sp else "") + "</span></div>"
                     + (f'<p>{S.E(read)}</p>' if read else "") + "</div>")
    head = (S.sign(None, "Intel", "ข่าวกรอง", n["date"], n["date"], cls="sm", tab="", alt_en="", alt_th="")
            + f'<h1 class="nh">{S.E(_f(S, n, "title"))}</h1><p class="lede">{S.E(_f(S, n, "dek"))}</p>'
            + f'<p class="nmeta">{kind_pill(S, n)}<time datetime="{n["date"]}">{n["date"]}</time></p>')
    body = S.band("hero.jpg", head, "top") + S.section(
        f'<article class="nbody">{quote}{body_p}{trend_box}</article>'
        + _links(S, n) + _sources(S, n)
        + f'<p><a href="{S.U("intel/")}">{S.T("All intel", "ข่าวกรองทั้งหมด")}</a></p>'
        + follow(S))
    ld = {"@context": "https://schema.org", "@type": "NewsArticle", "headline": _f(S, n, "title"), "datePublished": n["date"],
          "dateModified": n.get("updated", n["date"]), "inLanguage": S.LANG, "description": _f(S, n, "dek"),
          "author": {"@type": "Person", "name": "Nan"}, "publisher": {"@type": "Organization", "name": "Offrampt", "url": S.SITE_URL + "/"},
          "isAccessibleForFree": True, "license": "https://creativecommons.org/licenses/by/4.0/"}
    S.page(_f(S, n, "title"), body + SHARE_JS, "intel/" + slug(n) + "/", _f(S, n, "dek"), jsonld=ld)


def index_page(S):
    head = (S.sign(None, "Intel", "ข่าวกรอง", "What is moving, its shape and its speed", "อะไรกำลังเปลี่ยน รูปทรงและความเร็วของมัน", cls="sm", tab="", alt_en="", alt_th="")
            + f'<h1 class="q">{S.T("Intel", "ข่าวกรอง")}</h1>'
            + f'<p class="lede">{S.T("Crypto in Thailand, read for the long haul: dated notes with their sources, and trends computed from the data at every build.", "คริปโตในไทย อ่านแบบมองยาว: บันทึกลงวันที่พร้อมแหล่งที่มา และแนวโน้มที่คำนวณจากข้อมูลทุกครั้งที่สร้างหน้า")}</p>')
    cards = "".join(note_card(S, n, lead=(i == 0)) for i, n in enumerate(STATE["notes"]))
    body = S.band("hero.jpg", head, "top") + S.section(
        f'<h2>{S.T("Trends", "แนวโน้ม")}</h2>{signals_block(S, full=True)}'
        f'<h2>{S.T("Notes", "บันทึก")} <small>{len(STATE["notes"])}</small></h2><div class="ncards">{cards}</div>'
        + follow(S))
    S.page(S.T("Intel", "ข่าวกรอง"), body + SHARE_JS, "intel/",
           S.T("Crypto intel for Thailand: hacks, rules, banks, markets and the long view, each with its trend's shape and speed.",
               "ข่าวกรองคริปโตสำหรับประเทศไทย: การแฮ็ก กฎ ธนาคาร ตลาด และมุมมองระยะยาว พร้อมรูปทรงและความเร็วของแนวโน้ม"))


def _atom(S):
    base = S.SITE_URL + ("/th" if S.LANG == "th" else "")
    from html import escape as esc
    entries = []
    for n in STATE["notes"][:40]:
        url = f"{base}/intel/{slug(n)}/"
        paras = n.get("body_th") if S.LANG == "th" and n.get("body_th") else n.get("body_en", [])
        content = "".join(f"<p>{esc(p)}</p>" for p in paras)
        entries.append(f"<entry><id>{url}</id><title>{esc(_f(S, n, 'title'))}</title><link href=\"{url}\"/>"
                       f"<updated>{n.get('updated', n['date'])}T00:00:00+07:00</updated><summary>{esc(_f(S, n, 'dek'))}</summary>"
                       f"<content type=\"html\">{esc(content)}</content></entry>")
    upd = STATE["notes"][0]["date"] if STATE["notes"] else S.TODAY
    title = S.T("Offrampt intel", "ข่าวกรอง Offrampt")
    return (f'<?xml version="1.0" encoding="utf-8"?><feed xmlns="http://www.w3.org/2005/Atom" xml:lang="{S.LANG}">'
            f"<id>{base}/intel/</id><title>{esc(title)}</title><link href=\"{base}/intel/\"/>"
            f"<link rel=\"self\" href=\"{base}/intel/feed.xml\"/><updated>{upd}T00:00:00+07:00</updated>"
            f"<author><name>Nan</name></author><rights>CC BY 4.0</rights>{''.join(entries)}</feed>")


def build(S):
    """the intel pages and feeds for the current language; after every other page exists"""
    index_page(S)
    for n in STATE["notes"]:
        note_page(S, n)
    d = S.SITE / ("th" if S.LANG == "th" else "") / "intel"
    S.write(d / "feed.xml", _atom(S))
    if S.LANG == "en":
        keep = [{k: v for k, v in n.items()} for n in STATE["notes"]]
        S.write(d / "notes.json", json.dumps({"built": S.TODAY, "notes": keep}, ensure_ascii=False))


def paths():
    return ["intel/"] + [f"intel/{slug(n)}/" for n in STATE["notes"]]


def llms_lines(site_url):
    out = [f"- {site_url}/intel/ · {site_url}/th/intel/ — Intel / ข่าวกรอง: dated notes and computed trends; Atom feeds {site_url}/intel/feed.xml and {site_url}/th/intel/feed.xml; all notes as JSON {site_url}/intel/notes.json"]
    for n in STATE["notes"][:20]:
        out.append(f"  - {n['date']} {site_url}/intel/{slug(n)}/ — {n.get('title_en', '')}")
    return "\n".join(out) + "\n"
