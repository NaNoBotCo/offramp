#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""site.py — the pages, in English at / and Thai at /th/, from build/facts.json, build/figs.json,
data/research/*.json, data/ramp.json, data/routes.json and data/money.json.

    SITE_URL=https://offrampt.net python3 tools/site.py
"""
from __future__ import annotations

import html
import json
import os
import re
import shutil
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fleet                                   # noqa: E402
from css import CSS                            # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
BUILD = ROOT / "build"
SITE = BUILD / "site"
IMG = BUILD / "img"
OG = ROOT / "og"  # one 1200x630 link card per page: <lang>-<page>.jpg, alt text in tools/og_alts.py
DATA = ROOT / "data"
SITE_URL = os.environ.get("SITE_URL", "https://offrampt.net").rstrip("/")
tail = SITE_URL.split("//", 1)[-1]
BASE = "/" + tail.split("/", 1)[1] + "/" if "/" in tail else "/"
SELF = "offramp"
NAME = "Offrampt"
CREDIT = "Nan · hongdam.net · CC BY 4.0"
TODAY = date.today().isoformat()
E = html.escape
RATES = "https://offrampt-rates.nanobotco.workers.dev/"
LIST = "https://nanobot-list.nanobotco.workers.dev/subscribe"

F = json.loads((BUILD / "facts.json").read_text(encoding="utf-8"))
FIGS = json.loads((BUILD / "figs.json").read_text(encoding="utf-8"))
FLEET = fleet.load(DATA / "fleet.json")


def load(p):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


R = {k: load(DATA / "research" / f"{k}.json") for k in ("rules", "products", "history", "scams", "words")}  # stylecheck: allow — code: data file names
MONEY = load(DATA / "money.json")
RAMP = load(DATA / "ramp.json")
ROUTES = load(DATA / "routes.json").get("routes", [])

# ------------------------------------------------------------------ language
LANG = "en"


def T(en, th):
    return th if LANG == "th" else en


def U(h=""):
    """a link to page h in the current language"""
    return BASE + ("th/" if LANG == "th" else "") + h


def fld(o, k):
    if not o:
        return ""
    if LANG == "th" and o.get(k + "_th"):
        return o[k + "_th"]
    return o.get(k, "") or ""


def two(o, k):
    """ramp.json style: k_en / k_th"""
    return (o.get(k + "_th") if LANG == "th" else None) or o.get(k + "_en") or o.get(k, "")


TAG_EN = "Crypto in Thailand: the routes out to baht, the Thai rules, the cards, the scams, and the market in baht, with the numbers computed."  # stylecheck: allow — topic noun in the tagline, not a warning
TAG_TH = "คริปโตในประเทศไทย: เส้นทางแลกเป็นเงินบาท กฎของไทย บัตร กลโกง และตลาดในสกุลบาท พร้อมตัวเลขที่คำนวณจากข้อมูล"

# href, English, Thai, English sub, Thai sub, picture
EXITS = [
    ("ramp/", "Ramp", "แลกบาท", "Crypto to baht", "จากคริปโตเป็นเงินบาท", "band-ramp.jpg"),
    ("rules/", "Rules", "กฎ", "Thai law, tax, banks", "กฎหมาย ภาษี ธนาคาร", "band-rules.jpg"),
    ("cards/", "Cards", "บัตร", "Cards, exchanges, rails", "บัตร ศูนย์ซื้อขาย ช่องทางโอน", "band-cards.jpg"),
    ("networks/", "Networks", "เครือข่าย", "Chains and addresses", "เชนและที่อยู่กระเป๋า", "band-networks.jpg"),
    ("markets/", "Markets", "ตลาด", "The market in baht", "ตลาดในสกุลบาท", "band-markets.jpg"),
    ("scams/", "Scams", "กลโกง", "Frauds, freezes, signs", "การหลอกลวง การอายัด สัญญาณเตือน", "band-scams.jpg"),  # stylecheck: allow — nav label naming the Scams page
    ("how/", "How", "กลไก", "How crypto works", "คริปโตทำงานอย่างไร", "band-how.jpg"),
    ("history/", "History", "ประวัติ", "1976 to now", "ตั้งแต่ 1976 ถึงวันนี้", "band-history.jpg"),
    ("words/", "Words", "ศัพท์", "English and Thai", "อังกฤษและไทย", "band-words.jpg"),
    ("tools/", "Tools", "เครื่องมือ", "Checker, calculator", "ตรวจที่อยู่ คำนวณ", "band-tools.jpg"),
]
EXIT_NO = {e[0]: i + 1 for i, e in enumerate(EXITS)}
EX = {e[0]: e for e in EXITS}

ARROW = ('<svg class="arrow" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 19 L18 6" stroke="currentColor" '
         'stroke-width="3.2" stroke-linecap="round"/><path d="M9 5 H19 V15" fill="none" stroke="currentColor" '
         'stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/></svg>')
PLATE = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 19 L17 7" stroke="#f3faf5" stroke-width="3.4" '
         'stroke-linecap="round"/><path d="M9 6 H18 V15" fill="none" stroke="#f3faf5" stroke-width="3.4" '
         'stroke-linecap="round" stroke-linejoin="round"/></svg>')

# ------------------------------------------------------------------ sources
SRC: dict[str, int] = {}
SRC_LIST: list[dict] = []
FIXED = {
    "bitkub": {"title": "Bitkub public API: tradingview history and v3 market ticker", "url": "https://api.bitkub.com/", "publisher": "Bitkub Online", "date": TODAY},
    "binance": {"title": "Binance public market data API, daily klines", "url": "https://data-api.binance.vision/", "publisher": "Binance", "date": TODAY},
    "bot": {"title": "Bank of Thailand API, Stat-ExchangeRate v2, daily average exchange rate", "url": "https://portal.api.bot.or.th/", "publisher": "Bank of Thailand", "date": TODAY},
    "llama": {"title": "DefiLlama stablecoins API", "url": "https://stablecoins.llama.fi/stablecoins", "publisher": "DefiLlama", "date": TODAY},
    "mempool": {"title": "mempool.space block fee rates and hashrate", "url": "https://mempool.space/docs/api/rest", "publisher": "mempool.space", "date": TODAY},
    "coingecko": {"title": "CoinGecko API, coins/markets and global", "url": "https://www.coingecko.com/en/api", "publisher": "CoinGecko", "date": TODAY},
    "whitepaper": {"title": "Bitcoin: A Peer-to-Peer Electronic Cash System", "url": "https://bitcoin.org/bitcoin.pdf", "publisher": "Satoshi Nakamoto", "date": "2008-10-31"},
    "fips180": {"title": "FIPS 180-4, Secure Hash Standard", "url": "https://csrc.nist.gov/pubs/fips/180-4/upd1/final", "publisher": "NIST", "date": "2015-08-04"},
    "eip55": {"title": "EIP-55: Mixed-case checksum address encoding", "url": "https://eips.ethereum.org/EIPS/eip-55", "publisher": "Ethereum Improvement Proposals", "date": "2016-01-14"},
    "bip173": {"title": "BIP 173: Base32 address format for native v0-16 witness outputs", "url": "https://github.com/bitcoin/bips/blob/master/bip-0173.mediawiki", "publisher": "Bitcoin Improvement Proposals", "date": "2017-03-20"},
    "bip350": {"title": "BIP 350: Bech32m format for v1+ witness addresses", "url": "https://github.com/bitcoin/bips/blob/master/bip-0350.mediawiki", "publisher": "Bitcoin Improvement Proposals", "date": "2020-12-16"},
}


def cite(*items) -> str:
    out, flat = [], []
    for it in items:
        flat.extend(it if isinstance(it, list) else [it])
    for s in list(flat):
        if isinstance(s, str) and ":" in s:
            flat.extend(lookup(s))
    for s in flat:
        if isinstance(s, str):
            if ":" in s:
                continue
            s = FIXED[s]
        if not s or not s.get("url"):
            continue
        u = s["url"].strip()
        if u not in SRC:
            SRC_LIST.append(s)
            SRC[u] = len(SRC_LIST)
        k = SRC[u]
        out.append(f'<a class="cite" href="{U("sources/")}#s{k}" title="{E(s.get("title") or s.get("publisher") or u)}">[{k}]</a>')
    return "".join(out)


def lookup(ref):
    """'rule:<id>' or 'prod:<section>:<id>' → that research item's sources"""
    kind, _, rest = ref.partition(":")
    if kind == "rule":
        for sec in ("rules", "tax", "banking"):
            for r in R["rules"].get(sec) or []:
                if r.get("id") == rest:
                    return src_of(r)
    if kind == "prod":
        sec, _, pid = rest.partition(":")
        for r in R["products"].get(sec) or []:
            if r.get("id") == pid:
                return src_of(r)
    return []


def src_of(item):
    if not item:
        return []
    if item.get("sources"):
        return item["sources"]
    if isinstance(item.get("source"), dict):
        return [item["source"]]
    if item.get("source_url"):
        return [{"url": item["source_url"], "title": item.get("title") or item.get("event") or item.get("en") or item["source_url"]}]
    return []


# ------------------------------------------------------------------ helpers
def n(x, d=0):
    return f"{x:,.{d}f}"


def thb(x, d=0):
    return "฿" + n(x, d)


def pct(x, d=2, sign=True):
    return (f"{x:+.{d}f}" if sign else f"{x:.{d}f}") + "%"


CONF_TH = {"reported": "รายงานข่าว", "unconfirmed": "ยังไม่ยืนยัน"}


def conf(c):
    if not c or c == "confirmed":
        return ""
    return f' <span class="pill amber" title="{E(c)}">{E(T(c, CONF_TH.get(c, c)))}</span>'


STATUS_TH = {"in force": "มีผลบังคับ", "announced": "ประกาศแล้ว", "proposed": "ร่าง/รับฟังความเห็น", "expired": "หมดอายุ", "replaced": "ถูกแทนที่",
             "licensed": "ได้รับอนุญาต", "suspended": "ถูกระงับ", "revoked": "ถูกเพิกถอน", "surrendered": "คืนใบอนุญาต",
             "available": "ใช้ได้ในไทย", "not available": "ใช้ในไทยไม่ได้", "unclear": "ไม่ชัดเจน"}


def st_label(s):
    return T(s, STATUS_TH.get(s, s))


def sign(no, en, th, sub_en="", sub_th="", cls="", tab=None, alt_en=None, alt_th=None):
    t = tab if tab is not None else (T(f"EXIT {no}", f"ทางออก {no}") if no else "")
    tb = f'<span class="tab">{E(t)}</span>' if t else ""
    big, alt = (th, en) if LANG == "th" else (en, th)
    if alt_en is not None:
        alt = alt_en if LANG == "th" else alt_th
    sub = T(sub_en, sub_th)
    bl = ' lang="en"' if big.isascii() else ""
    return (f'<div class="sign {cls}">{tb}<span class="big"{bl}>{E(big)}{ARROW}</span>'
            + (f'<span class="alt" lang="{T("th", "en")}">{E(alt)}</span>' if alt else "")
            + (f'<span class="sub">{E(sub)}</span>' if sub else "") + "</div>")


def band(img, inner, cls=""):
    return (f'<section class="band {cls}" style="background-image:url({BASE}img/{img})">'
            f'<div class="in">{inner}</div></section>')


def shot(href, img, kicker, title, text):
    return (f'<a class="shot" href="{U(href)}"><span class="bg" style="background-image:url({BASE}img/{img})"></span>'
            f'<span class="scrim"></span><span class="sp"></span>'
            f'<span class="tx"><em>{E(kicker)}</em><b>{E(title)}</b><span>{E(text)}</span></span></a>')


def door(h):
    e = EX[h]
    return shot(h, e[5], T(f"EXIT {EXIT_NO[h]}", f"ทางออก {EXIT_NO[h]}"), T(e[1], e[2]), T(e[3], e[4]))


def tile(k, v, note="", cls="", attrs=""):
    return (f'<div class="tile {cls}"><span class="k">{E(k)}</span><span class="v"{attrs}>{v}</span>'
            + (f'<span class="n">{note}</span>' if note else "") + "</div>")


def figure(key, caption):
    return (f'<figure class="fig"><div class="sv" tabindex="0" aria-label="{E(T("chart", "แผนภูมิ"))}">{FIGS[LANG][key]}</div>'
            f'<figcaption>{caption}</figcaption></figure>')


def table(head, rows, attrs=""):
    th_ = "".join(f'<th{" class=r" if h.endswith(" ›") else ""}>{E(h.rstrip(" ›"))}</th>' for h in head)
    return f'<div class="tw"><table{attrs}><thead><tr>{th_}</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'


def aff(pid, text=None):
    url = (MONEY.get("referral") or {}).get(pid)
    if not url:
        return ""
    return f' <a class="btn sponsored" href="{E(url)}" rel="sponsored noopener" target="_blank">{E(text or T("Sign up", "สมัคร"))}</a>'


def disclose():
    return T('<p class="disclose">Links marked ↗ are referral links: an account opened through one pays this site a commission from the provider, '
             'at no charge to the reader. Nothing here is advice about money.</p>',
             '<p class="disclose">ลิงก์ที่มีเครื่องหมาย ↗ เป็นลิงก์แนะนำ: บัญชีที่เปิดผ่านลิงก์นั้นทำให้เว็บนี้ได้ค่าคอมมิชชันจากผู้ให้บริการ '
             'โดยผู้อ่านไม่เสียค่าใช้จ่ายเพิ่ม เนื้อหาในเว็บนี้ไม่ใช่คำแนะนำทางการเงิน</p>')


JS_NAV = """<script>(function(){var y=scrollY,b=document.body;addEventListener('scroll',function(){var n=scrollY;
b.classList.toggle('nav-away',n>y&&n>240);y=n},{passive:true})})();</script>"""


def subscribe():
    h, p, lab, bt = (T("Rule changes, by email", "แจ้งเมื่อกฎเปลี่ยน ทางอีเมล"),
                     T("Thai limits, fees and paperwork move. The list carries notices when a rule on these pages changes.",
                       "วงเงิน ค่าธรรมเนียม และเอกสารของไทยเปลี่ยนได้ รายชื่อนี้ใช้แจ้งเมื่อกฎในหน้าเหล่านี้เปลี่ยน"),
                     T("Email address", "อีเมล"), T("Send", "ส่ง"))
    ok, bad, inc = T("On the list.", "ลงชื่อแล้ว"), T("That did not go through. Try again in a moment.", "ส่งไม่สำเร็จ ลองอีกครั้งในอีกสักครู่"), T("That address looks incomplete.", "อีเมลดูไม่ครบ")
    return f"""<section class="panel" id="subx"><h3 style="margin-top:0">{h}</h3><p class="small mute">{p}</p>
<form class="row" novalidate><label class="hp" aria-hidden="true" style="position:absolute;left:-9999px">Website<input type="text" name="website" tabindex="-1" autocomplete="off"></label>
<div class="field" style="flex:1 1 16rem;margin:0"><input type="email" name="email" id="subem" placeholder=" " autocomplete="email" required><label for="subem">{lab}</label></div>
<button class="go" type="submit">{bt}</button></form><p class="said small" hidden></p></section>
<script>(function(){{var r=document.getElementById('subx');if(!r)return;var f=r.querySelector('form'),s=r.querySelector('.said'),t0=Date.now();
f.addEventListener('submit',function(e){{e.preventDefault();var em=f.email.value.trim();
if(!/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(em)){{s.hidden=false;s.textContent='{inc}';return}}
var b=f.querySelector('button');b.disabled=true;fetch('{LIST}',{{method:'POST',headers:{{'Content-Type':'application/json'}},
body:JSON.stringify({{email:em,website:f.website.value,t0:t0,source:'offrampt',lang:'{LANG}'}})}})
.then(function(x){{return x.json()}}).then(function(d){{b.disabled=false;s.hidden=false;s.textContent=d&&d.ok?'{ok}':'{bad}';if(d&&d.ok)f.reset()}})
.catch(function(){{b.disabled=false;s.hidden=false;s.textContent='{bad}'}})}})}})();</script>"""


def write(p: Path, text: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def og_tags(path):
    """the page's own card when og/ has one, else the site card"""
    key = ("th-" if LANG == "th" else "en-") + (path.strip("/") or "home")
    from og_alts import ALTS as alts
    if (OG / f"{key}.jpg").exists() and key in alts:
        img, alt = f"{SITE_URL}/img/og/{key}.jpg", alts[key]
    else:
        img, alt = f"{SITE_URL}/img/{T('card.jpg', 'card-th.jpg')}", T("Card: Offrampt, light trails to an EXIT sign on a night road", "การ์ด: Offrampt, ทางแสงไปยังป้าย EXIT บนถนนตอนกลางคืน")
    a = E(alt, quote=True)
    return (f'<meta property="og:image" content="{img}"><meta property="og:image:width" content="1200">'
            f'<meta property="og:image:height" content="630"><meta property="og:image:alt" content="{a}">'
            f'<meta name="twitter:image" content="{img}"><meta name="twitter:image:alt" content="{a}">')


def page(title, body, path, desc="", scripts=(), jsonld=None):
    nav = "".join(f'<a href="{U(h)}"{" aria-current=page" if path == h else ""}><i>{EXIT_NO[h]}</i>{E(T(en, th))}</a>'
                  for h, en, th, *_r in EXITS)
    js = "".join(f'<script src="{BASE}js/{s}" defer></script>' for s in scripts)
    url_en, url_th = SITE_URL + "/" + path, SITE_URL + "/th/" + path
    canon = url_th if LANG == "th" else url_en
    lds = [{"@context": "https://schema.org", "@type": "WebPage", "name": title, "url": canon, "inLanguage": LANG,
            "isPartOf": {"@type": "WebSite", "name": NAME, "url": SITE_URL + "/"},
            "license": "https://creativecommons.org/licenses/by/4.0/", "dateModified": TODAY,
            "publisher": fleet.publisher_ld(FLEET)}]
    if jsonld:
        lds.append(jsonld)
    ld = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in lds)
    tag = T(TAG_EN, TAG_TH)
    head_title = f"{title} — {NAME}" if path else T(f"{NAME} — crypto in Thailand, and the ways out to baht", f"{NAME} — คริปโตในไทย และทางออกสู่เงินบาท")
    exits = "".join(f'<a href="{U(h)}"><i>{EXIT_NO[h]}</i>{E(T(en, th))}</a>' for h, en, th, *_r in EXITS)
    opath = "" if path == "404/" else path
    other = (BASE + opath) if LANG == "th" else (BASE + "th/" + opath)
    toggle = f'<a class="lang" href="{other}" hreflang="{T("th", "en")}" lang="{T("th", "en")}">{T("ไทย", "EN")}</a>'
    foot = T(f"""Text, figures and data {E(CREDIT)}. Code MIT. Built {TODAY}. Prices from Bitkub, Binance, CoinGecko and the Bank of Thailand,
fetched at build and live from <a href="{RATES}">the rates service</a>; each figure names its source on <a href="{U('sources/')}">the sources page</a>.
Nothing here is advice about money, tax or law.""",
             f"""ข้อความ ภาพ และข้อมูล {E(CREDIT)} โค้ด MIT สร้างเมื่อ {TODAY} ราคาจาก Bitkub, Binance, CoinGecko และธนาคารแห่งประเทศไทย
ดึงตอนสร้างหน้าและดึงสดจาก<a href="{RATES}">บริการอัตรา</a> ตัวเลขแต่ละตัวระบุแหล่งที่มาไว้ใน<a href="{U('sources/')}">หน้าแหล่งที่มา</a>
เนื้อหาในเว็บนี้ไม่ใช่คำแนะนำด้านการเงิน ภาษี หรือกฎหมาย""")
    out = f"""<!doctype html><html lang="{LANG}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(head_title)}</title>
<meta name="description" content="{E(desc or tag)}">
<link rel="canonical" href="{E(canon)}">
<link rel="alternate" hreflang="en" href="{E(url_en)}"><link rel="alternate" hreflang="th" href="{E(url_th)}"><link rel="alternate" hreflang="x-default" href="{E(url_en)}">
<meta property="og:title" content="{E(head_title)}">
<meta property="og:description" content="{E(desc or tag)}">
{og_tags(path)}
<meta property="og:type" content="website"><meta property="og:site_name" content="{NAME}">
<meta property="og:locale" content="{T('en_US', 'th_TH')}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#05070c">
<link rel="icon" href="{BASE}icon.svg" type="image/svg+xml">
<style>{CSS}</style>{ld}
</head>
<body data-base="{BASE}" data-rates="{RATES}" data-lang="{LANG}">
<a class="sr" href="#main">{T("Skip to the page", "ข้ามไปที่เนื้อหา")}</a>
<header class="top"><div class="in">
<a class="brand" href="{U()}" aria-label="{NAME}"><span class="plate">{PLATE}</span><b>OFFRAMPT</b></a>
<nav aria-label="{T('Exits', 'ทางออก')}">{nav}</nav>{toggle}</div></header>
<main id="main" class="wide">{body}</main>
<footer class="bot"><div class="in">
<div class="exits">{exits}<a href="{U('support/')}"><i>฿</i>{T("Support", "สนับสนุน")}</a></div>
<p><b>{NAME}</b> — {E(tag)}</p>
<p>{foot}
<a href="{U('data/')}">{T("Data", "ข้อมูล")}</a> · <a href="{U('for-agents/')}">{T("For agents", "สำหรับเอเจนต์")}</a> · <a href="{U('support/')}">{T("Support", "สนับสนุน")}</a> · <a href="{U('sources/')}">{T("Sources", "แหล่งที่มา")}</a> · {toggle}</p>
{fleet.row_html(SELF, label=T("Also ours", "เว็บอื่นของเรา"), roster=FLEET)}
{fleet.support_html(roster=FLEET, contact=False, self_id=SELF)}
{fleet.maker_html(roster=FLEET, lang=LANG)}
</div></footer>{js}{JS_NAV}
</body></html>"""
    dest = SITE / ("th" if LANG == "th" else "") / path
    write(dest / "index.html", out)
    return out


def head(no, en, th, sub_en, sub_th, img, lede="", cls="", bcls=""):
    return band(img, sign(no, en, th, sub_en, sub_th, cls) + (f'<p class="lede" style="margin-top:1.6rem">{lede}</p>' if lede else ""), bcls)


def exit_head(h, lede="", cls=""):
    e = EX[h]
    return head(EXIT_NO[h], e[1], e[2], e[3], e[4], e[5], lede, cls)


def section(inner):
    return f'<div class="in">{inner}</div>'


# ------------------------------------------------------------------ the live board
def live_board():
    Uu, X, B = F["usdt"], F["fx"], F["btc"]
    stamp = T(f"Baked {Uu['last']['date']}; live figures replace these when the page reaches the rates service.",
              f"ค่าตอนสร้างหน้า {Uu['last']['date']} ตัวเลขสดจะแทนที่เมื่อหน้าเชื่อมต่อบริการอัตราได้")
    tiles = "".join([
        tile(T("USDT → baht · Bitkub bid", "USDT → บาท · ราคารับซื้อ Bitkub"), f'{Uu["last"]["bitkub"]:.2f}', T("baht for one USDT", "บาทต่อ 1 USDT"), "go", ' data-live="usdt_bid"'),
        tile(T("US dollar · BOT mid", "ดอลลาร์ · อัตรากลาง ธปท."), f'{X["mid"]:.2f}', T(f'Bank of Thailand reference, {X["date"]}', f'อัตราอ้างอิงธนาคารแห่งประเทศไทย {X["date"]}'), "blue", ' data-live="bot_mid"'),
        tile(T("USDT vs the dollar", "USDT เทียบดอลลาร์"), pct((Uu["last"]["bitkub"] / X["mid"] - 1) * 100), T("Bitkub USDT against the BOT mid", "USDT บน Bitkub เทียบอัตรากลาง ธปท."), "", ' data-live="usdt_prem"'),
        tile(T("Bitcoin in baht · Bitkub", "บิตคอยน์เป็นบาท · Bitkub"), thb(B["thb"]),
             T(f'{pct(B["from_ath_pct"], 1)} from the {B["ath_date"][:7]} high', f'{pct(B["from_ath_pct"], 1)} จากจุดสูงสุดเมื่อ {B["ath_date"][:7]}'), "", ' data-live="btc_bid"'),
    ])
    return f"""<div class="board" id="board"><div class="row" style="justify-content:space-between">
<h3 style="margin:0">{T("The board", "กระดานราคา")}</h3><span class="live stale" id="livestate">{T("baked", "ค่าตอนสร้าง")}</span></div>
<div class="tiles" style="margin:.8rem 0 .4rem">{tiles}</div>
<p class="stamp" id="livestamp">{stamp}</p></div>"""


# ------------------------------------------------------------------ home
def home():
    Uu, P, S, K = F["usdt"], F["premium"], F["stable"], F["bitkub"]
    doors = "".join(door(h) for h, *_r in EXITS)
    intro = band("hero.jpg", sign(None, "Offrampt", "Offrampt", "Crypto in Thailand · the ways out to baht", "คริปโตในไทย · ทางออกสู่เงินบาท", tab=T("EXITS 1–10", "ทางออก 1–10"),
                                  alt_en="Crypto in Thailand · the ways out to baht", alt_th="คริปโตในไทย · ทางออกสู่เงินบาท")
                 + '<p class="lede" style="margin-top:1.8rem">' + T(
                     "Holding crypto in Thailand is easy. Turning it into baht you can spend, without a Thai bank account, is the hard part. "
                     "Ten exits: the routes, the rules, the cards, the networks, the market in baht, the scams, how it works, where it came from, the words, and the tools.",
                     "ถือคริปโตในไทยนั้นง่าย ส่วนที่ยากคือการแลกเป็นเงินบาทที่ใช้จ่ายได้ โดยไม่มีบัญชีธนาคารไทย "
                     "สิบทางออก: เส้นทางแลกเงิน กฎ บัตร เครือข่าย ตลาดในสกุลบาท กลโกง กลไก ความเป็นมา คำศัพท์ และเครื่องมือ") + "</p>", "hero")
    finds = "".join([
        tile(T("USDT vs a wired dollar", "USDT เทียบเงินโอนดอลลาร์"), pct(Uu["vs_tt_median"]),
             T(f'median baht from one USDT sold on Bitkub, against the Thai banks\' buying rate for a dollar transfer, {n(Uu["days"])} days since {Uu["from"][:4]}',
               f'ค่ามัธยฐานของเงินบาทที่ได้จากการขาย 1 USDT บน Bitkub เทียบอัตรารับซื้อเงินโอนดอลลาร์ของธนาคารไทย {n(Uu["days"])} วัน ตั้งแต่ปี {Uu["from"][:4]}')
             + cite("bitkub", "bot"), "go"),
        tile(T("Days within 1% of world", "วันที่ห่างราคาโลกไม่เกิน 1%"), f'{P["within_1pct"]:.0f}%',
             T(f"Bitkub's bitcoin close against Binance × the BOT rate, {n(P['days'])} days", f"ราคาปิดบิตคอยน์บน Bitkub เทียบ Binance × อัตรา ธปท. {n(P['days'])} วัน") + cite("binance")),
        tile(T("USDT share of Bitkub", "สัดส่วน USDT บน Bitkub"), f'{K["usdt_share"]:.0f}%',
             T("of all baht volume on Bitkub's own book, last 24 hours", "ของมูลค่าซื้อขายเป็นเงินบาททั้งหมดในสมุดคำสั่งของ Bitkub เอง 24 ชั่วโมงล่าสุด"), "blue"),
        tile(T("Stablecoins", "สเตเบิลคอยน์"), f'${S["total_usd"] / 1e9:.0f}B',
             T(f'in circulation; USDT is {S["top"][0]["share"]:.0f}% of them', f'หมุนเวียนอยู่ในตลาด USDT คิดเป็น {S["top"][0]["share"]:.0f}%') + cite("llama")),
        tile(T("USDT on Tron", "USDT บน Tron"), f'{S["usdt_tron_share"]:.0f}%', T("of all USDT sits on the Tron network", "ของ USDT ทั้งหมดอยู่บนเครือข่าย Tron"), "red"),
        tile(T("Bitcoin in baht", "บิตคอยน์เป็นบาท"), f'{F["btc"]["multiple_since_first"]}×',
             T(f'since May 2018 on Bitkub; {pct(F["btc"]["from_ath_pct"], 1)} from the {F["btc"]["ath_date"][:7]} high',
               f'ตั้งแต่ พ.ค. 2018 บน Bitkub; {pct(F["btc"]["from_ath_pct"], 1)} จากจุดสูงสุด {F["btc"]["ath_date"][:7]}')),
        tile(T("Bank margin", "ส่วนต่างของธนาคาร"), pct(Uu["bank_margin_median"], sign=False),
             T("median gap between the interbank mid and what Thai banks pay for a dollar transfer", "ค่ามัธยฐานของส่วนต่างระหว่างอัตรากลางกับอัตราที่ธนาคารไทยรับซื้อเงินโอนดอลลาร์"), "blue"),
        tile(T("Hottest year", "ปีที่ร้อนแรงที่สุด"), str(P["hot_year"]["year"]),
             T(f'bitcoin on Bitkub ran a median {pct(P["hot_year"]["median"])} over the world price', f'บิตคอยน์บน Bitkub สูงกว่าราคาโลก ค่ามัธยฐาน {pct(P["hot_year"]["median"])}'), "go"),
    ])
    who = "".join(
        f'<a class="cardx" href="{U("ramp/")}#{sid}" style="text-decoration:none;color:inherit"><span class="pill {pc}">{E(T(pe, pt))}</span>'
        f'<h3>{E(T(te, tt))}</h3><p class="small">{E(T(de, dt_))}</p></a>'
        for sid, pc, pe, pt, te, tt, de, dt_ in [
            ("visiting", "amber", "no Thai bank", "ไม่มีบัญชีธนาคารไทย", "Visiting", "มาเยือน",
             "A short stay. Cards, cash, and the TouristDigiPay sandbox the SEC has set up.", "พักระยะสั้น บัตร เงินสด และแซนด์บ็อกซ์ TouristDigiPay ที่ ก.ล.ต. ตั้งไว้"),
            ("living", "blue", "long stay", "พำนักระยะยาว", "Living here, unbanked", "อยู่ที่นี่ ยังไม่มีบัญชีธนาคาร",
             "DTV, remote work, between visas. The routes that work before a bank says yes.", "DTV ทำงานทางไกล ระหว่างรอวีซ่า เส้นทางที่ใช้ได้ก่อนธนาคารอนุมัติ"),
            ("banked", "go", "Thai bank", "มีบัญชีธนาคารไทย", "Banked here", "มีบัญชีธนาคารที่นี่",
             "Work permit, retirement, family. A licensed Thai exchange to your own account.", "ใบอนุญาตทำงาน วีซ่าเกษียณ ครอบครัว ศูนย์ซื้อขายไทยที่ได้รับอนุญาต สู่บัญชีของคุณเอง")])
    body = intro + section(f"""
{live_board()}
<h2>{T("Findings", "สิ่งที่พบ")} <small>{T(f"computed from {n(P['days'])} days of prices", f"คำนวณจากราคา {n(P['days'])} วัน")}</small></h2>
<div class="tiles">{finds}</div>
<h2>{T("Where you stand", "คุณอยู่ตรงไหน")}</h2><div class="grid3">{who}</div>
<h2>{T("The exits", "ทางออก")}</h2>
<div class="doors">{doors}</div>
{recent_block()}
{subscribe()}
""")
    ld = {"@context": "https://schema.org", "@type": "WebSite", "name": NAME, "url": SITE_URL + "/", "description": T(TAG_EN, TAG_TH),
          "inLanguage": ["en", "th"], "license": "https://creativecommons.org/licenses/by/4.0/"}
    page(NAME, body, "", scripts=("i18n.js", "live.js"), jsonld=ld)


def recent_block():
    ev = []
    for e in (R["rules"].get("timeline") or []):
        ev.append((e.get("date", ""), fld(e, "event"), src_of(e), "th"))
    for e in (R["history"].get("events") or []):
        t = fld(e, "title")
        ev.append((e.get("date", ""), t + (". " if LANG == "en" else " ") + fld(e, "what"), src_of(e), "th" if e.get("thailand") else ""))
    ev = [x for x in ev if x[0] and x[0] <= TODAY]
    seen, uniq = set(), []
    for x in sorted(ev, key=lambda x: x[0], reverse=True):
        k = (x[0], x[1][:40])
        if k not in seen:
            seen.add(k)
            uniq.append(x)
    if not uniq:
        return ""
    items = "".join(f'<li class="{c}"><time>{E(d)}</time><div><p>{E(t)}{cite(s)}</p></div></li>' for d, t, s, c in uniq[:8])
    return (f'<h2>{T("Latest", "ล่าสุด")} <small>{T("Thai events in green", "เหตุการณ์ในไทยเป็นสีเขียว")}</small></h2><ol class="tl">{items}</ol>'
            f'<p><a href="{U("history/")}">{T("All of it, 1976 on", "ทั้งหมด ตั้งแต่ปี 1976")}</a> · <a href="{U("rules/")}#timeline">{T("Thailand only", "เฉพาะประเทศไทย")}</a></p>')


# ------------------------------------------------------------------ ramp
def ramp():
    Uu = F["usdt"]
    q = RAMP.get("question") or {}
    out = []
    for s in RAMP.get("situations") or []:
        rows = []
        for r in s.get("routes", []):
            rows.append(f'<div class="cardx route"><h3>{E(two(r, "name"))}</h3>'
                        + "".join(f'<p class="small"><b>{E(lab)}</b> {E(two(r, k))}</p>' for k, lab in
                                  (("needs", T("Needs:", "ต้องมี:")), ("cost", T("Cost:", "ค่าใช้จ่าย:")), ("limits", T("Limits:", "วงเงิน:")), ("risk", T("Risk:", "ความเสี่ยง:"))) if two(r, k))  # stylecheck: allow — field labels
                        + f'<p class="small">{cite(r.get("refs") or [])}{"".join(aff(i) for i in r.get("aff", []))}</p></div>')
        out.append(f'<section id="{E(s["id"])}"><h2><span class="pill {E(s.get("pill_cls", ""))}" style="vertical-align:middle">{E(two(s, "pill"))}</span> {E(two(s, "title"))}</h2>'
                   f'<p class="lede">{E(two(s, "lede"))}</p><div class="grid2">{"".join(rows)}</div></section>')
    checklist = "".join(f'<li>{E(two(c, "text"))}</li>' for c in RAMP.get("checklist", []))
    notes = "".join(f'<div class="note {E(x.get("cls", ""))}"><b>{E(two(x, "head"))}</b> {E(two(x, "text"))}{cite(x.get("refs") or [])}</div>' for x in RAMP.get("notes", []))
    body = exit_head("ramp/", E(two(q, "lede")) if q else "")
    body += section(f"""
{live_board()}
{notes}
{"".join(out)}
<h2 id="calc">{T("The calculator", "เครื่องคำนวณ")}</h2>
<p>{T("One amount, each route's costs. Where a provider publishes a fee, its field starts there; a field at zero is one for you to fill. Every field can be changed.", "จำนวนเงินเดียวกัน คิดค่าใช้จ่ายของแต่ละเส้นทาง ช่องที่ผู้ให้บริการเผยแพร่ค่าธรรมเนียมจะตั้งต้นจากค่านั้น ช่องที่เป็นศูนย์คือช่องให้คุณกรอกเอง แก้ไขได้ทุกช่อง")}</p>
{calc_block()}
<h2>{T("The spread", "ส่วนต่าง")}</h2>
<p>{T(f"Selling USDT on Bitkub has fetched a median {pct(Uu['vs_tt_median'])} more baht than a dollar wired into a Thai bank at the banks' buying rate, over {n(Uu['days'])} days.",
      f"การขาย USDT บน Bitkub ได้เงินบาทมากกว่าเงินดอลลาร์ที่โอนเข้าธนาคารไทยตามอัตรารับซื้อของธนาคาร ค่ามัธยฐาน {pct(Uu['vs_tt_median'])} ตลอด {n(Uu['days'])} วัน")}{cite("bitkub", "bot")}</p>
{figure("usdt", T("Bitkub USDT/THB daily close against the Thai banks' average buying rate for a dollar transfer. Fees on either side are not in the chart; the calculator adds them.", "ราคาปิดรายวัน USDT/THB บน Bitkub เทียบอัตรารับซื้อเงินโอนดอลลาร์เฉลี่ยของธนาคารไทย ไม่รวมค่าธรรมเนียม เครื่องคำนวณด้านบนรวมให้"))}
<h2>{T("Before sending", "ก่อนกดส่ง")}</h2><ol>{checklist}</ol>
{disclose()}
{subscribe()}
""")
    page(T("Ramp", "แลกบาท"), body, "ramp/", T("How to turn crypto into Thai baht as a foreigner: visiting, living here without a Thai bank, or banked here; routes, costs, limits, risks.",  # stylecheck: allow — topic nouns in the page description
                                                "วิธีแลกคริปโตเป็นเงินบาทสำหรับชาวต่างชาติ: มาเยือน อยู่ที่นี่แต่ไม่มีบัญชีธนาคาร หรือมีบัญชีแล้ว เส้นทาง ค่าใช้จ่าย วงเงิน ความเสี่ยง"),  # stylecheck: allow — topic nouns in the page description
         scripts=("i18n.js", "live.js", "calc.js"))


def calc_block():
    Uu, X, B = F["usdt"], F["fx"], F["btc"]
    base = {"usdt_bid": Uu["last"]["bitkub"], "mid": X["mid"], "tt": X["tt"], "btc_bid": B["thb"], "date": Uu["last"]["date"]}
    return (f'<script type="application/json" id="ratebase">{json.dumps(base)}</script>'
            f'<script type="application/json" id="routes">{json.dumps(ROUTES, ensure_ascii=False)}</script>'
            f'<div class="panel" id="calcbox"><div class="row"><div class="field" style="flex:1 1 10rem;margin:0"><input id="camt" inputmode="decimal" placeholder=" " value="1000">'
            f'<label for="camt">{T("USDT to turn into baht", "จำนวน USDT ที่จะแลกเป็นบาท")}</label></div></div><div id="croutes"></div><div id="cbars" style="margin-top:1rem"></div></div>')


# ------------------------------------------------------------------ markets
def markets():
    Uu, P, B, S, K, X = F["usdt"], F["premium"], F["btc"], F["stable"], F["bitkub"], F["fx"]
    board = "".join(
        f'<tr><td><b>{E(b["sym"])}</b></td><td class="r">{b["last"]:,.{2 if b["last"] >= 1 else 6}f}</td>'
        f'<td class="r" style="color:{"#2fd27f" if b["chg"] >= 0 else "#ff5a5f"}">{pct(b["chg"])}</td><td class="r">{thb(b["thb_vol"])}</td></tr>'
        for b in K["top"][:24])
    world = "".join(
        f'<tr><td class="r">{c["rank"]}</td><td><b>{E(c["sym"])}</b> <span class="mute small">{E(c["name"])}</span></td>'
        f'<td class="r">{c["thb"]:,.{2 if c["thb"] >= 1 else 6}f}</td>'
        f'<td class="r" style="color:{"#2fd27f" if (c["chg24"] or 0) >= 0 else "#ff5a5f"}">{pct(c["chg24"] or 0)}</td>'
        f'<td class="r">{pct(c["chg1y"] or 0, 0) if c["chg1y"] is not None else "—"}</td></tr>'
        for c in F["world"][:30])
    yrs = "".join(f'<tr><td>{y}</td><td class="r">{pct(v["median"])}</td><td class="r">{pct(v["p10"])}</td><td class="r">{pct(v["p90"])}</td><td class="r">{v["days"]}</td></tr>'
                  for y, v in P["by_year"].items())
    uy = "".join(f'<tr><td>{y}</td><td class="r">{pct(v["vs_tt"])}</td><td class="r">{pct(v["vs_mid"])}</td><td class="r">{v["days"]}</td></tr>'
                 for y, v in Uu["by_year"].items())
    G = F.get("global") or {}
    body = exit_head("markets/", T(
        f"Bitcoin cost {thb(B['first_thb'])} on Bitkub in May 2018 and {thb(B['thb'])} on {B['date']}: {B['multiple_since_first']}× in baht, {pct(B['from_ath_pct'], 1)} from the {B['ath_date']} high.",
        f"บิตคอยน์ราคา {thb(B['first_thb'])} บน Bitkub เมื่อ พ.ค. 2018 และ {thb(B['thb'])} เมื่อ {B['date']}: {B['multiple_since_first']} เท่าในสกุลบาท {pct(B['from_ath_pct'], 1)} จากจุดสูงสุดเมื่อ {B['ath_date']}") + cite("bitkub"))
    gl = ""
    if G:
        gl = T(f"Total market value ${G['cap_usd'] / 1e12:.2f} trillion; bitcoin {G['btc_dom']}% of it, ether {G['eth_dom']}%; {n(G['coins'])} coins tracked.",
               f"มูลค่าตลาดรวม {G['cap_usd'] / 1e12:.2f} ล้านล้านดอลลาร์ บิตคอยน์ {G['btc_dom']}% อีเธอร์ {G['eth_dom']}% ติดตาม {n(G['coins'])} เหรียญ")
    body += section(f"""
{live_board()}
<h2>{T("Bitcoin in baht", "บิตคอยน์ในสกุลบาท")}</h2>
{figure("btc_thb", T("Bitkub BTC/THB daily close, log scale. Halvings in green.", "ราคาปิดรายวัน BTC/THB บน Bitkub สเกลลอการิทึม เส้นสีเขียวคือการลดรางวัลครึ่งหนึ่ง (halving)") + cite("bitkub"))}
<h2>{T("The Thai premium", "ส่วนต่างราคาไทย")} <small>{T("is bitcoin dearer here?", "บิตคอยน์ในไทยแพงกว่าไหม")}</small></h2>
<p>{T(f"Bitkub's daily close sits within 1% of the world price on <b>{P['within_1pct']:.0f}%</b> of {n(P['days'])} days. The median gap is <b>{pct(P['median'])}</b>; 80% of days fall between {pct(P['p10'])} and {pct(P['p90'])}. {P['hot_year']['year']} ran hottest, median {pct(P['hot_year']['median'])}.",
      f"ราคาปิดรายวันบน Bitkub ห่างจากราคาโลกไม่เกิน 1% ใน <b>{P['within_1pct']:.0f}%</b> ของ {n(P['days'])} วัน ค่ามัธยฐานของส่วนต่างคือ <b>{pct(P['median'])}</b> และ 80% ของวันอยู่ระหว่าง {pct(P['p10'])} ถึง {pct(P['p90'])} ปี {P['hot_year']['year']} ร้อนแรงที่สุด ค่ามัธยฐาน {pct(P['hot_year']['median'])}")}{cite("bitkub", "binance", "bot")}</p>
{figure("premium", T("World price = Binance BTC/USDT close × the Bank of Thailand mid rate for the same day, carried over weekends and Thai bank holidays. A daily close is one trade, so single days swing; the median is the reading.",
                     "ราคาโลก = ราคาปิด BTC/USDT บน Binance × อัตรากลางของ ธปท. วันเดียวกัน (วันหยุดใช้อัตราวันทำการก่อนหน้า) ราคาปิดคือการซื้อขายครั้งเดียว รายวันจึงแกว่ง ให้อ่านที่ค่ามัธยฐาน"))}
{table([T("Year", "ปี"), T("Median ›", "มัธยฐาน ›"), T("10th pct ›", "เปอร์เซ็นไทล์ 10 ›"), T("90th pct ›", "เปอร์เซ็นไทล์ 90 ›"), T("Days ›", "วัน ›")], [yrs])}
<h2>{T("USDT to baht", "USDT เป็นบาท")} <small>{T("the off-ramp's own price", "ราคาของทางออกเอง")}</small></h2>
<p>{T(f"One USDT sold on Bitkub fetched a median <b>{pct(Uu['vs_tt_median'])}</b> more baht than the Thai banks' average buying rate for a one-dollar transfer, above it on <b>{Uu['beat_tt_share']:.0f}%</b> of {n(Uu['days'])} days. Over the last year that is about <b>{thb(Uu['year_thb_per_10k'])}</b> more per 10,000 dollars, before any fees on either side. Against the interbank mid rate the median gap is {pct(Uu['vs_mid_median'])}: USDT trades at the dollar, and the bank's own margin ({pct(Uu['bank_margin_median'], sign=False)} below mid, median) is the difference.",
      f"การขาย 1 USDT บน Bitkub ได้เงินบาทมากกว่าอัตรารับซื้อเงินโอน 1 ดอลลาร์เฉลี่ยของธนาคารไทย ค่ามัธยฐาน <b>{pct(Uu['vs_tt_median'])}</b> และสูงกว่าใน <b>{Uu['beat_tt_share']:.0f}%</b> ของ {n(Uu['days'])} วัน ในหนึ่งปีที่ผ่านมาคิดเป็นราว <b>{thb(Uu['year_thb_per_10k'])}</b> ต่อ 10,000 ดอลลาร์ ก่อนหักค่าธรรมเนียมทั้งสองฝั่ง เมื่อเทียบกับอัตรากลางระหว่างธนาคาร ส่วนต่างค่ามัธยฐานคือ {pct(Uu['vs_mid_median'])}: USDT ซื้อขายที่ราคาดอลลาร์ และส่วนต่างที่เห็นคือกำไรของธนาคารเอง ({pct(Uu['bank_margin_median'], sign=False)} ต่ำกว่าอัตรากลาง ค่ามัธยฐาน)")}{cite("bitkub", "bot")}</p>
{figure("usdt", T("Bitkub USDT/THB daily close against the BOT average buying-transfer rate (the rate Thai banks pay for incoming dollars), and the BOT mid rate. Wire fees and exchange fees are not in this chart; the calculator on Ramp adds them.",
                  "ราคาปิดรายวัน USDT/THB บน Bitkub เทียบอัตรารับซื้อเงินโอนเฉลี่ยของ ธปท. (อัตราที่ธนาคารไทยจ่ายให้เงินดอลลาร์ที่โอนเข้า) และอัตรากลาง ไม่รวมค่าโอนและค่าธรรมเนียมศูนย์ซื้อขาย เครื่องคำนวณในหน้าแลกบาทรวมให้"))}
{table([T("Year", "ปี"), T("vs bank buying ›", "เทียบอัตรารับซื้อ ›"), T("vs mid ›", "เทียบอัตรากลาง ›"), T("Days ›", "วัน ›")], [uy])}
<h2>{T("Bitkub now", "Bitkub ตอนนี้")} <small>{T("24 hours, baht volume on the own book", "24 ชั่วโมง มูลค่าเป็นบาทในสมุดคำสั่งของ Bitkub เอง")}</small></h2>
<p>{T(f"{K['pairs']} pairs trade against baht. USDT carries <b>{K['usdt_share']:.0f}%</b> of the volume: the dollar trade in and out of baht is the biggest thing on the exchange. {K['shared']} pairs report a second, larger volume that includes liquidity routed from elsewhere; the figures here use the own-book number.",
      f"มี {K['pairs']} คู่ที่ซื้อขายกับเงินบาท USDT คิดเป็น <b>{K['usdt_share']:.0f}%</b> ของมูลค่า: การแลกดอลลาร์เข้าออกเงินบาทคือกิจกรรมที่ใหญ่ที่สุดบนศูนย์ซื้อขายนี้ มี {K['shared']} คู่ที่รายงานมูลค่าอีกชุดซึ่งรวมสภาพคล่องจากที่อื่น ตัวเลขในหน้านี้ใช้มูลค่าในสมุดคำสั่งของ Bitkub เอง")}{cite("bitkub")}</p>
{figure("bitkub_board", T("Stablecoin pairs in green.", "คู่สเตเบิลคอยน์เป็นสีเขียว"))}
{table([T("Pair", "คู่"), T("Last ฿ ›", "ล่าสุด ฿ ›"), T("24h ›", "24 ชม. ›"), T("Volume ฿ ›", "มูลค่า ฿ ›")], [board])}
<h2>{T("The world, in baht", "ตลาดโลกในสกุลบาท")}</h2>
<p>{gl}{cite("coingecko")}</p>
{figure("world_caps", T("Market capitalisation in baht, CoinGecko.", "มูลค่าตลาดในสกุลบาท จาก CoinGecko"))}
{table(["#", T("Coin", "เหรียญ"), "฿ ›", T("24h ›", "24 ชม. ›"), T("1y ›", "1 ปี ›")], [world])}
<h2>{T("Stablecoins", "สเตเบิลคอยน์")}</h2>
{figure("stable_total", T("Dollar-pegged stablecoins in circulation, weekly. DefiLlama.", "สเตเบิลคอยน์ที่ผูกกับดอลลาร์ที่หมุนเวียน รายสัปดาห์ จาก DefiLlama") + cite("llama"))}
<h2>{T("The dollar in baht", "ดอลลาร์ในสกุลบาท")}</h2>
<p>{T(f"Every baht figure on this site moves with this line. Low {X['min'][0]:.2f} ({X['min'][1]}), high {X['max'][0]:.2f} ({X['max'][1]}).",
      f"ตัวเลขเงินบาททุกตัวในเว็บนี้ขยับตามเส้นนี้ ต่ำสุด {X['min'][0]:.2f} ({X['min'][1]}) สูงสุด {X['max'][0]:.2f} ({X['max'][1]})")}{cite("bot")}</p>
{figure("fx", T("Bank of Thailand daily weighted-average interbank mid rate.", "อัตรากลางถัวเฉลี่ยถ่วงน้ำหนักระหว่างธนาคารรายวัน ธนาคารแห่งประเทศไทย"))}
<p class="small"><a href="{U('data/')}">{T("Download the series", "ดาวน์โหลดข้อมูล")}</a> · CC BY 4.0</p>
""")
    ld = {"@context": "https://schema.org", "@type": "Dataset", "name": "Offrampt: bitcoin and USDT in baht, the Thai premium and the off-ramp spread",
          "description": "Daily Bitkub closes against Binance and the Bank of Thailand reference rate, 2018 on, with the computed premium and spread.",
          "url": SITE_URL + "/markets/", "license": "https://creativecommons.org/licenses/by/4.0/", "dateModified": TODAY, "creator": fleet.publisher_ld(FLEET),
          "distribution": [{"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": SITE_URL + "/data/series.json"},
                           {"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": SITE_URL + "/data/facts.json"}]}
    page(T("Markets", "ตลาด"), body, "markets/", T("Bitcoin and USDT in baht since 2018: the Thai premium, the off-ramp spread against a bank wire, Bitkub's board, stablecoins.",
                                                   "บิตคอยน์และ USDT ในสกุลบาทตั้งแต่ปี 2018: ส่วนต่างราคาไทย ส่วนต่างการแลกเทียบเงินโอนธนาคาร กระดาน Bitkub สเตเบิลคอยน์"),
         scripts=("i18n.js", "live.js"), jsonld=ld)


# ------------------------------------------------------------------ networks
NETS = [
    ("Bitcoin", "BTC", "1…, 3…, bc1q…, bc1p…", "BTC only", "เฉพาะ BTC",
     "Native bitcoin. Exchanges also offer BTC on other chains (as BTCB, WBTC); those are different assets on different networks.",
     "บิตคอยน์ดั้งเดิม ศูนย์ซื้อขายบางแห่งมี BTC บนเชนอื่น (BTCB, WBTC) ซึ่งเป็นสินทรัพย์คนละตัวบนคนละเครือข่าย", "#ffb13b"),
    ("Ethereum", "ETH", "0x… (40 hex)", "USDT, USDC, ETH", "USDT, USDC, ETH",
     "The same 0x address works on every EVM chain below. The address does not name the network; the sender's menu does.",
     "ที่อยู่ 0x เดียวกันใช้ได้กับทุกเชน EVM ด้านล่าง ที่อยู่ไม่ได้บอกว่าเป็นเครือข่ายไหน เมนูของผู้ส่งเป็นตัวกำหนด", "#8ea2ff"),
    ("Tron", "TRX", "T… (34)", "USDT (TRC-20)", "USDT (TRC-20)",
     "Where most USDT moves. Fees are paid in TRX or 'energy'; a wallet with no TRX can hold USDT and still be unable to send it.",
     "เครือข่ายที่ USDT เคลื่อนไหวมากที่สุด ค่าธรรมเนียมจ่ายเป็น TRX หรือ energy กระเป๋าที่ไม่มี TRX ถือ USDT ได้แต่ส่งออกไม่ได้", "#ff5a5f"),
    ("BNB Smart Chain", "BNB", "0x…", "USDT (BEP-20), USDC", "USDT (BEP-20), USDC",
     "Binance's EVM chain. Same address shape as Ethereum, different network.", "เชน EVM ของ Binance ที่อยู่หน้าตาเหมือน Ethereum แต่เป็นคนละเครือข่าย", "#f3ba2f"),
    ("Solana", "SOL", "base58, 32–44", "USDC, USDT", "USDC, USDT",
     "No checksum in the address, so a typo can still look valid.", "ที่อยู่ไม่มี checksum พิมพ์ผิดหนึ่งตัวก็ยังดูเหมือนถูกต้อง", "#19fb9b"),
    ("Base", "ETH", "0x…", "USDC", "USDC", "Coinbase's layer 2 on Ethereum. Same 0x address as Ethereum.", "เลเยอร์ 2 ของ Coinbase บน Ethereum ใช้ที่อยู่ 0x เดียวกับ Ethereum", "#2f6bff"),
    ("Arbitrum", "ETH", "0x…", "USDC, USDT", "USDC, USDT", "Ethereum layer 2. Same 0x address.", "เลเยอร์ 2 ของ Ethereum ใช้ที่อยู่ 0x เดียวกัน", "#28a0f0"),
    ("TON", "TON", "EQ…, UQ… (48)", "USDT", "USDT",
     "Telegram's chain. Exchanges often need a memo (comment) on deposits.", "เชนของ Telegram ศูนย์ซื้อขายมักต้องการ memo (คอมเมนต์) ตอนฝาก", "#34a6ff"),
    ("XRP Ledger", "XRP", "r… (25–35)", "XRP, RLUSD", "XRP, RLUSD",
     "Exchanges need a destination tag; a deposit without it lands in the exchange's pool, not your account.",
     "ศูนย์ซื้อขายต้องการ destination tag ถ้าไม่ใส่ เงินจะเข้ากองรวมของศูนย์ซื้อขาย ไม่เข้าบัญชีของคุณ", "#b4c0cc"),
    ("Lightning", "BTC", "lnbc…, name@domain", "BTC", "BTC",
     "Payments on top of bitcoin, settled in seconds. An invoice is for one amount and expires.", "การชำระเงินซ้อนบนบิตคอยน์ เสร็จในไม่กี่วินาที ใบแจ้งหนี้ (invoice) ใช้ได้ครั้งเดียวและหมดอายุ", "#ffd166"),
]


def checker():
    return (f'<div class="panel"><div class="field"><textarea id="addr" placeholder=" " spellcheck="false" autocomplete="off"></textarea>'
            f'<label for="addr">{T("Address, invoice or payment name", "ที่อยู่ ใบแจ้งหนี้ หรือชื่อรับเงิน")}</label></div>'
            f'<div class="out" id="addrout" aria-live="polite">{T("Waiting for an address.", "รอที่อยู่")}</div></div>')


def networks():
    S, fees = F["stable"], F["fees"]
    rows = "".join(f'<tr><td><b style="color:{c}">{E(nm)}</b></td><td>{E(t)}</td><td><code>{E(a)}</code></td><td>{E(T(ce, ct))}</td><td class="small">{E(T(ne, nt))}</td></tr>'
                   for nm, t, a, ce, ct, ne, nt, c in NETS)
    st_rows = []
    for a in S["top"][:8]:
        ch = " · ".join(f'{E(c)} {p:.0f}%' for c, v, p in a["chains"][:4])
        st_rows.append(f'<tr><td><b>{E(a["symbol"])}</b> <span class="mute small">{E(a["name"])}</span></td><td class="r">${a["usd"] / 1e9:,.1f}B</td><td class="r">{a["share"]:.1f}%</td><td class="small">{ch}</td></tr>')
    fee_thb = fees["median_last_year"] * fees["vb_typical"] * F["btc"]["thb"] / 1e8
    body = exit_head("networks/", T(
        f"The same coin travels on many networks. USDT alone sits on {S['top'][0]['chain_count']} of them; {S['usdt_tron_share']:.0f}% is on Tron. The network has to match at both ends, or the coins arrive somewhere the receiver cannot reach.",
        f"เหรียญเดียวกันเดินทางได้หลายเครือข่าย USDT อย่างเดียวอยู่บน {S['top'][0]['chain_count']} เครือข่าย โดย {S['usdt_tron_share']:.0f}% อยู่บน Tron เครือข่ายต้องตรงกันทั้งสองฝั่ง ไม่อย่างนั้นเหรียญจะไปถึงที่ที่ผู้รับเข้าไม่ได้") + cite("llama"))
    body += section(f"""
<div class="note red"><b>{T("THE MISTAKE.", "ความผิดพลาดที่พบบ่อย")}</b> {T("A sender picks a network from a menu. The receiver's address has to be on that network. A 0x address is valid on Ethereum, BNB Smart Chain, Base, Arbitrum and a dozen more, so the address alone never says which one. Coins sent on a network the receiving exchange does not support can sit in an address nobody there watches.",
    "ผู้ส่งเลือกเครือข่ายจากเมนู ที่อยู่ของผู้รับต้องอยู่บนเครือข่ายนั้น ที่อยู่ 0x ใช้ได้ทั้งบน Ethereum, BNB Smart Chain, Base, Arbitrum และอีกหลายสิบเชน ตัวที่อยู่เองจึงไม่บอกว่าเป็นเครือข่ายไหน เหรียญที่ส่งบนเครือข่ายที่ศูนย์ซื้อขายปลายทางไม่รองรับ อาจค้างอยู่ในที่อยู่ที่ไม่มีใครดูแล")}</div>
<h2>{T("Address checker", "ตัวตรวจที่อยู่")}</h2>
<p>{T("Paste one. The checker reads the format and the checksum, and names the networks that format belongs to. It runs in this page's script.",
      "วางที่อยู่ลงไป ตัวตรวจจะอ่านรูปแบบและ checksum แล้วบอกว่ารูปแบบนั้นเป็นของเครือข่ายใด การตรวจทำงานในสคริปต์ของหน้านี้")}</p>
{checker()}
<h2>{T("Which network", "เครือข่ายไหน")}</h2>
{table([T("Network", "เครือข่าย"), T("Coin", "เหรียญ"), T("Address looks like", "หน้าตาที่อยู่"), T("Stablecoins", "สเตเบิลคอยน์"), T("Note", "หมายเหตุ")], [rows])}
<h2>{T("Where the stablecoins are", "สเตเบิลคอยน์อยู่ที่ไหน")}</h2>
{figure("usdt_chains", T("USDT supply by chain, weekly, DefiLlama. Tron took the lead in 2021 and holds it.", "ปริมาณ USDT แยกตามเชน รายสัปดาห์ จาก DefiLlama Tron ขึ้นนำในปี 2021 และยังนำอยู่") + cite("llama"))}
{table([T("Stablecoin", "สเตเบิลคอยน์"), T("Supply ›", "ปริมาณ ›"), T("Share ›", "สัดส่วน ›"), T("Largest networks", "เครือข่ายหลัก")], st_rows)}
<h2>{T("Fees", "ค่าธรรมเนียม")}</h2>
<p>{T(f"A typical bitcoin payment is about {fees['vb_typical']} virtual bytes. The median fee rate over the last year was <b>{fees['median_last_year']} sat/vB</b> (a sat is one hundred-millionth of a bitcoin), so a payment cost roughly {thb(fee_thb, 2)} at today's price. Exchanges charge their own withdrawal fee on top, often more than the network's.",
      f"การโอนบิตคอยน์ทั่วไปมีขนาดราว {fees['vb_typical']} virtual byte ค่ามัธยฐานของอัตราค่าธรรมเนียมในหนึ่งปีที่ผ่านมาคือ <b>{fees['median_last_year']} sat/vB</b> (1 sat เท่ากับหนึ่งในร้อยล้านบิตคอยน์) การโอนหนึ่งครั้งจึงราว {thb(fee_thb, 2)} ที่ราคาวันนี้ ศูนย์ซื้อขายเก็บค่าถอนของตัวเองเพิ่ม ซึ่งมักสูงกว่าค่าเครือข่าย")}{cite("mempool", "bitkub")}</p>
{figure("fees", T("Median fee rate per block × 141 vbytes × the day's Bitkub price. Log scale.", "อัตราค่าธรรมเนียมมัธยฐานต่อบล็อก × 141 vbyte × ราคา Bitkub วันนั้น สเกลลอการิทึม"))}
<div class="tiles">
{tile(T("USDT supply", "ปริมาณ USDT"), '$%.0fB' % (S["top"][0]["usd"] / 1e9), T("all networks", "ทุกเครือข่าย"), "go")}
{tile(T("USDC supply", "ปริมาณ USDC"), '$%.0fB' % (S["top"][1]["usd"] / 1e9), T("all networks", "ทุกเครือข่าย"), "blue")}
{tile(T("Bitcoin hashrate", "แฮชเรตบิตคอยน์"), '%.2f <small>ZH/s</small>' % (fees["hashrate"] / 1e21), T("tries per second, network-wide, ×10²¹", "จำนวนครั้งที่ลองต่อวินาทีทั้งเครือข่าย ×10²¹"))}
</div>
""")
    page(T("Networks", "เครือข่าย"), body, "networks/", T("Which network: Bitcoin, Ethereum, Tron, BNB, Solana, Base, TON, XRP. An address checker, stablecoins by chain, fees in baht.",
                                                          "เครือข่ายไหน: Bitcoin, Ethereum, Tron, BNB, Solana, Base, TON, XRP ตัวตรวจที่อยู่ สเตเบิลคอยน์แยกตามเชน ค่าธรรมเนียมเป็นบาท"),
         scripts=("i18n.js", "sha.js", "addr.js"))


# ------------------------------------------------------------------ how
def how():
    sup, S = F["supply"], F["stable"]
    both = S["top"][0]["share"] + S["top"][1]["share"]
    body = exit_head("how/", T("Five ideas carry the whole thing: a hash, a key, a chain of blocks, a rule for who adds the next block, and a token that stands for something else. Each has a working model below.",
                               "ห้าแนวคิดที่แบกทั้งระบบไว้: แฮช กุญแจ ห่วงโซ่ของบล็อก กติกาว่าใครได้เพิ่มบล็อกถัดไป และโทเคนที่แทนสิ่งอื่น แต่ละข้อมีแบบจำลองให้ลองด้านล่าง"))
    sel = "font:inherit;background:var(--bg2);color:var(--ink);border:1px solid #2a3544;border-radius:10px;padding:.4rem"
    body += section(f"""
<h2>1 · {T("A hash", "แฮช")} <small>{T("a fingerprint for any data", "ลายนิ้วมือของข้อมูลใดก็ได้")}</small></h2>
<p>{T("SHA-256 turns any input into 256 bits. Change one character and about half the bits flip, with no pattern a person or a computer can use to go backwards. Bitcoin names blocks and transactions by their hashes.",
      "SHA-256 แปลงข้อมูลใดก็ได้เป็น 256 บิต เปลี่ยนตัวอักษรเดียว บิตจะพลิกราวครึ่งหนึ่ง โดยไม่มีรูปแบบที่คนหรือคอมพิวเตอร์ใช้ย้อนกลับได้ บิตคอยน์ตั้งชื่อบล็อกและธุรกรรมด้วยแฮชของมัน")}{cite("fips180")}</p>
<div class="panel"><div class="field"><input id="hin" placeholder=" " value="offrampt"><label for="hin">{T("Type anything", "พิมพ์อะไรก็ได้")}</label></div>
<div class="out" id="hout"></div><canvas id="hbits" width="1024" height="120" style="width:100%;height:auto;margin-top:.6rem;border-radius:10px"></canvas>
<p class="small mute" id="hflip"></p></div>
<h2>2 · {T("A key", "กุญแจ")} <small>{T("a number only you know", "ตัวเลขที่มีแค่คุณรู้")}</small></h2>
<p>{T("A wallet is a large random number, the private key. Multiplying a fixed point on a curve by that number gives the public key; hashing the public key gives the address. Going forward takes microseconds; going back from address to key has no known method short of guessing among 2<sup>256</sup> possibilities. The twelve or twenty-four words of a seed phrase encode that number. Anyone holding the words holds the coins.",
      "กระเป๋าคือเลขสุ่มขนาดใหญ่ เรียกว่ากุญแจส่วนตัว (private key) นำจุดคงที่บนเส้นโค้งมาคูณด้วยเลขนั้นจะได้กุญแจสาธารณะ และแฮชกุญแจสาธารณะจะได้ที่อยู่ ทางไปใช้เวลาไม่กี่ไมโครวินาที ทางกลับจากที่อยู่ไปหากุญแจไม่มีวิธีที่รู้จัก นอกจากเดาจาก 2<sup>256</sup> ความเป็นไปได้ คำ 12 หรือ 24 คำของ seed phrase (ชุดคำกู้คืน) คือเลขนั้นในรูปคำ ใครถือคำเหล่านี้ คนนั้นถือเหรียญ")}</p>
<div class="note red"><b>SEED PHRASE.</b> <!-- stylecheck: allow — a fact about seed phrases, not advice -->{T("A support agent, an exchange, a wallet app, a person on a call: none of them needs the words to help with anything. A request for them is the scam.",
    "เจ้าหน้าที่ ศูนย์ซื้อขาย แอปกระเป๋า หรือคนที่โทรมา ไม่มีใครต้องใช้คำเหล่านี้เพื่อช่วยอะไรเลย การขอคำเหล่านี้คือการหลอกลวง")}</div>
<h2>3 · {T("A chain", "ห่วงโซ่")} <small>{T("each block names the one before it", "แต่ละบล็อกอ้างถึงบล็อกก่อนหน้า")}</small></h2>
<p>{T("A block holds transactions and the hash of the previous block. Change an old transaction and that block's hash changes, which breaks the next block's reference, and every block after it.",
      "บล็อกหนึ่งเก็บธุรกรรมและแฮชของบล็อกก่อนหน้า แก้ธุรกรรมเก่าเมื่อใด แฮชของบล็อกนั้นเปลี่ยน การอ้างอิงของบล็อกถัดไปก็พัง และพังต่อไปทุกบล็อกหลังจากนั้น")}</p>
<h2>4 · {T("Who adds the next block", "ใครได้เพิ่มบล็อกถัดไป")}</h2>
<p>{T("<b>Proof of work</b> (bitcoin): whoever first finds a number that makes the block's hash start with enough zeros. The only way is to try. Try it here: each extra zero multiplies the average tries by 16.",
      "<b>Proof of work</b> (บิตคอยน์): ใครหาเลขที่ทำให้แฮชของบล็อกขึ้นต้นด้วยศูนย์มากพอได้ก่อน คนนั้นได้ไป วิธีเดียวคือลองไปเรื่อยๆ ลองได้ที่นี่: ศูนย์เพิ่มหนึ่งตัว จำนวนครั้งเฉลี่ยคูณ 16")}</p>
<div class="panel"><div class="row"><label for="mz">{T("Zeros", "จำนวนศูนย์")}</label>
<select id="mz" style="{sel}"><option>1</option><option>2</option><option selected>3</option><option>4</option><option>5</option></select>
<button class="go" id="mine" data-hr="{F['fees']['hashrate'] / 1e18:,.0f}">{T("Mine a block", "ขุดบล็อก")}</button></div>
<div class="out" id="mout" style="margin-top:.6rem">{T('A block with the text "offrampt", the previous hash, and a nonce to search.', 'บล็อกที่มีข้อความ "offrampt" แฮชก่อนหน้า และ nonce ที่ต้องค้นหา')}</div></div>
<p>{T("<b>Proof of stake</b> (Ethereum since September 2022): validators lock up coins, the protocol picks one to propose each block, and a validator that cheats loses part of its stake.",
      "<b>Proof of stake</b> (Ethereum ตั้งแต่กันยายน 2022): ผู้ตรวจสอบ (validator) ล็อกเหรียญไว้ โปรโตคอลสุ่มเลือกคนเสนอแต่ละบล็อก และผู้ที่โกงจะถูกริบเหรียญบางส่วน")}</p>
<h2>5 · {T("A token that stands for something", "โทเคนที่แทนสิ่งอื่น")}</h2>
<p>{T(f"A stablecoin is a token whose issuer holds reserves (cash, short Treasury bills) and redeems tokens for dollars. USDT (Tether) and USDC (Circle) are the two largest; together {both:.0f}% of the ${S['total_usd'] / 1e9:.0f} billion in circulation. The token is only as good as the issuer's reserves and its willingness to redeem; an issuer can also freeze tokens at an address, and does, at police request.",
      f"สเตเบิลคอยน์คือโทเคนที่ผู้ออกถือทุนสำรอง (เงินสด ตั๋วเงินคลังระยะสั้น) และรับไถ่ถอนเป็นดอลลาร์ USDT (Tether) และ USDC (Circle) ใหญ่ที่สุดสองอันดับ รวมกัน {both:.0f}% ของ {S['total_usd'] / 1e9:.0f} พันล้านดอลลาร์ที่หมุนเวียนอยู่ โทเคนดีได้เท่าที่ทุนสำรองและความเต็มใจไถ่ถอนของผู้ออก ผู้ออกยังอายัดโทเคนในที่อยู่หนึ่งได้ และทำจริงเมื่อตำรวจร้องขอ")}{cite("llama")}</p>
<h2>{T("The 21 million", "21 ล้านเหรียญ")}</h2>
<p>{T(f"Bitcoin's reward started at 50 coins per block and halves every 210,000 blocks, about four years. The sum of that series is {sup['cap']:,.8f} coins; the last fraction arrives around 2140.",
      f"รางวัลของบิตคอยน์เริ่มที่ 50 เหรียญต่อบล็อก และลดลงครึ่งหนึ่งทุก 210,000 บล็อก ราวสี่ปี ผลรวมของอนุกรมนี้คือ {sup['cap']:,.8f} เหรียญ เศษสุดท้ายจะออกราวปี 2140")}{cite("whitepaper")}</p>
{figure("supply", T("Coins in existence, millions. Real dates through the 2024 halving; later ones assume ten-minute blocks.", "จำนวนเหรียญที่มีอยู่ หน่วยล้าน ใช้วันที่จริงถึง halving ปี 2024 หลังจากนั้นสมมติบล็อกละสิบนาที"))}
""")
    page(T("How", "กลไก"), body, "how/", T("How crypto works: hashing, keys and seed phrases, blocks, mining and staking, stablecoins, the 21 million, with working models.",
                                            "คริปโตทำงานอย่างไร: แฮช กุญแจและ seed phrase บล็อก การขุดและ staking สเตเบิลคอยน์ 21 ล้านเหรียญ พร้อมแบบจำลองให้ลอง"),
         scripts=("i18n.js", "sha.js", "how.js"))


# ------------------------------------------------------------------ tools
def tools():
    body = exit_head("tools/", T("Three tools for the moment before sending: the address checker, the off-ramp calculator, and a baht converter on live prices.",
                                 "เครื่องมือสามอย่างสำหรับช่วงก่อนกดส่ง: ตัวตรวจที่อยู่ เครื่องคำนวณการแลก และตัวแปลงเป็นบาทด้วยราคาสด"))
    body += section(f"""
{live_board()}
<h2>{T("Address checker", "ตัวตรวจที่อยู่")}</h2>
{checker()}
<p class="small mute">{T("Formats and checksums: bitcoin base58 and bech32/bech32m; EVM mixed-case checksums; Tron, XRP and TON checks.", "รูปแบบและ checksum: บิตคอยน์ base58 และ bech32/bech32m, EVM แบบตัวพิมพ์ผสม, Tron, XRP และ TON")}{cite("bip173", "bip350", "eip55")}</p>
<h2>{T("Baht converter", "แปลงเป็นบาท")}</h2>
<div class="panel"><div class="row">
<div class="field" style="flex:1 1 10rem;margin:0"><input id="cvamt" inputmode="decimal" placeholder=" " value="100"><label for="cvamt">{T("Amount", "จำนวน")}</label></div>
<div class="field" style="flex:0 1 9rem;margin:0"><select id="cvasset"><option value="usdt">USDT</option><option value="btc">BTC</option><option value="usd">{T("US dollar", "ดอลลาร์สหรัฐ")}</option></select><label for="cvasset">{T("Of", "สกุล")}</label></div>
</div><div class="out" id="cvout" style="margin-top:.7rem"></div></div>
<h2 id="calc">{T("Off-ramp calculator", "เครื่องคำนวณการแลก")}</h2>
<p>{T("Each route turns the same amount into baht with its own costs. Where a provider publishes a fee, its field starts there; a field at zero is one for you to fill.",
      "แต่ละเส้นทางแลกจำนวนเงินเดียวกันเป็นบาทโดยมีค่าใช้จ่ายของตัวเอง ช่องที่ผู้ให้บริการเผยแพร่ค่าธรรมเนียมจะตั้งต้นจากค่านั้น ช่องที่เป็นศูนย์คือช่องให้คุณกรอกเอง")}</p>
{calc_block()}
{disclose()}
""")
    page(T("Tools", "เครื่องมือ"), body, "tools/", T("Crypto-to-baht tools: an address checker for BTC, EVM, Tron, Solana, XRP and TON; an off-ramp calculator; a live baht converter.",
                                                     "เครื่องมือแลกคริปโตเป็นบาท: ตัวตรวจที่อยู่ BTC, EVM, Tron, Solana, XRP, TON เครื่องคำนวณการแลก และตัวแปลงเป็นบาทด้วยราคาสด"),
         scripts=("i18n.js", "live.js", "sha.js", "addr.js", "calc.js"))


# ------------------------------------------------------------------ support
def qr_svg(text):
    import qrcode
    q = qrcode.QRCode(border=1, error_correction=qrcode.constants.ERROR_CORRECT_M)
    q.add_data(text)
    q.make(fit=True)
    m = q.get_matrix()
    k = len(m)
    rects = "".join(f'<rect x="{x}" y="{y}" width="1" height="1"/>' for y, row in enumerate(m) for x, v in enumerate(row) if v)
    return f'<svg viewBox="0 0 {k} {k}" role="img" aria-label="QR" shape-rendering="crispEdges" style="width:100%;height:auto"><g fill="#000">{rects}</g></svg>'


def support():
    addrs = MONEY.get("receive") or {}
    blocks = []
    for key, label, ne, nt in (("btc", "Bitcoin", "network: Bitcoin", "เครือข่าย: Bitcoin"), ("lightning", "Lightning", "a Lightning address", "Lightning address"),
                               ("evm", "USDC · USDT · ETH", "network: Base, Arbitrum or Ethereum; same 0x address", "เครือข่าย: Base, Arbitrum หรือ Ethereum ใช้ที่อยู่ 0x เดียวกัน"),
                               ("tron", "USDT · Tron", "network: Tron (TRC-20)", "เครือข่าย: Tron (TRC-20)"), ("sol", "Solana", "network: Solana", "เครือข่าย: Solana")):
        a = addrs.get(key)
        if a:
            qr = qr_svg(("bitcoin:" + a) if key == "btc" else a)
            blocks.append(f'<div class="cardx"><h3>{E(label)}</h3><p class="small mute">{E(T(ne, nt))}</p>'
                          f'<div style="background:#fff;border-radius:12px;padding:10px;max-width:220px">{qr}</div>'
                          f'<p><code style="word-break:break-all">{E(a)}</code></p></div>')
    crypto = (f'<h2>{T("In crypto", "เป็นคริปโต")}</h2><div class="grid3">{"".join(blocks)}</div>'
              f'<p class="small mute">{T("The address checker on Tools reads any of these.", "ตัวตรวจที่อยู่ในหน้าเครื่องมืออ่านที่อยู่เหล่านี้ได้ทั้งหมด")}</p>') if blocks else ""
    refs = [v for v in (MONEY.get("referral") or {}).values() if v]
    body = head(None, "Support", "สนับสนุน", "What keeps the lights on", "สิ่งที่ทำให้ไฟยังติดอยู่", "hero.jpg",
                T("The site is free to read and free to copy under CC BY 4.0. It is paid for three ways: referral links, sponsors, and tips.",
                  "อ่านฟรีและคัดลอกได้ภายใต้ CC BY 4.0 ค่าใช้จ่ายของเว็บมาจากสามทาง: ลิงก์แนะนำ ผู้สนับสนุน และทิป"))
    body += section(f"""
{crypto}
<h2>{T("Sponsors", "ผู้สนับสนุน")}</h2>
{fleet.support_html(roster=FLEET, contact=False, self_id=SELF)}
<h2>{T("Referral links", "ลิงก์แนะนำ")}</h2>
<p>{T(f"Where a provider runs a referral programme and a link is on file, its row carries a button marked ↗. {len(refs)} on file today.",
      f"เมื่อผู้ให้บริการมีโปรแกรมแนะนำและมีลิงก์บันทึกไว้ แถวนั้นจะมีปุ่มที่มีเครื่องหมาย ↗ วันนี้มี {len(refs)} ลิงก์")}</p>
{disclose()}
""")
    page(T("Support", "สนับสนุน"), body, "support/", T("How Offrampt is paid for: referral links, sponsors and tips in crypto.", "ค่าใช้จ่ายของ Offrampt มาจากไหน: ลิงก์แนะนำ ผู้สนับสนุน และทิปเป็นคริปโต"))


# ------------------------------------------------------------------ research-driven pages
def rules():
    RR = R["rules"]
    order = {"in force": 0, "announced": 1, "proposed": 2, "replaced": 3, "expired": 4}
    items = sorted(RR.get("rules") or [], key=lambda r: (order.get(r.get("status", ""), 5), r.get("date", "")))
    cards = []
    for r in items:
        stc = {"in force": "go", "announced": "blue", "proposed": "amber"}.get(r.get("status", ""), "")
        ttl, alt = (r.get("title_th") or r.get("title"), r.get("title")) if LANG == "th" else (r.get("title"), r.get("title_th"))
        cards.append(f'<div class="cardx" id="{E(r.get("id", ""))}"><span class="pill {stc}">{E(st_label(r.get("status", "")))}</span>'
                     f'<span class="pill">{E(r.get("date", ""))}</span>{conf(r.get("confidence"))}<h3>{E(ttl or "")}</h3>'
                     + (f'<p class="small" style="color:var(--go);margin:.1rem 0">{E(alt)}</p>' if alt and alt != ttl else "")
                     + f'<p class="small mute">{E(fld(r, "body"))}</p><p>{E(fld(r, "what"))}{cite(src_of(r))}</p>'
                     + (f'<p class="small"><b>{T("For a foreigner:", "สำหรับชาวต่างชาติ:")}</b> {E(fld(r, "for_foreigners"))}</p>' if r.get("for_foreigners") else "") + "</div>")
    op_rows = "".join(f'<tr><td><b>{E(o.get("name", ""))}</b>' + (f'<br><span class="th small mute">{E(o["name_th"])}</span>' if o.get("name_th") else "")
                      + f'</td><td>{E(fld(o, "licence"))}</td><td>{E(o.get("since", ""))}</td><td>{E(st_label(o.get("status", "")))}</td>'
                      f'<td class="small">{E(fld(o, "notes"))}{cite(src_of(o))}</td></tr>' for o in RR.get("operators") or [])
    bl_rows = "".join(f'<tr><td><b>{E(b.get("name", ""))}</b></td><td>{E(b.get("date", ""))}</td><td class="small">{E(fld(b, "action"))}{cite(src_of(b))}</td></tr>' for b in RR.get("blocked") or [])
    tax_cards = "".join(f'<div class="cardx"><span class="pill">{E(t.get("date", ""))}</span><span class="pill">{E(st_label(t.get("status", "")))}</span>{conf(t.get("confidence"))}'
                        f'<h3>{E(fld(t, "title"))}</h3><p>{E(fld(t, "what"))}{cite(src_of(t))}</p>'
                        + (f'<p class="small"><b>{T("Example:", "ตัวอย่าง:")}</b> {E(fld(t, "example"))}</p>' if t.get("example") else "") + "</div>" for t in RR.get("tax") or [])
    bank_cards = "".join(f'<div class="cardx"><span class="pill">{E(b.get("date", ""))}</span>{conf(b.get("confidence"))}'
                         f'<h3>{E(fld(b, "title"))}</h3><p>{E(fld(b, "what"))}{cite(src_of(b))}</p>'
                         + (f'<p class="small"><b>{T("For a foreigner:", "สำหรับชาวต่างชาติ:")}</b> {E(fld(b, "for_foreigners"))}</p>' if b.get("for_foreigners") else "") + "</div>" for b in RR.get("banking") or [])
    tl = sorted(RR.get("timeline") or [], key=lambda e: e.get("date", ""))
    tl_items = "".join(f'<li class="th"><time>{E(e.get("date", ""))}</time><div><p>{E(fld(e, "event"))}{conf(e.get("confidence"))}{cite(src_of(e))}</p></div></li>' for e in tl)
    oq = (RR.get("open_questions_th") if LANG == "th" else None) or RR.get("open_questions") or []
    body = exit_head("rules/", T(f"Crypto is legal to hold and trade in Thailand through businesses the SEC licenses. The rules below set who may run an exchange, what a foreigner can open, what the Revenue Department taxes, and why a bank freezes an account. As of {RR.get('as_of', TODAY)}.",
                                 f"คริปโตถือและซื้อขายได้ถูกกฎหมายในไทย ผ่านธุรกิจที่ ก.ล.ต. ออกใบอนุญาต กฎด้านล่างกำหนดว่าใครเปิดศูนย์ซื้อขายได้ ชาวต่างชาติเปิดอะไรได้ กรมสรรพากรเก็บภาษีอะไร และทำไมธนาคารจึงอายัดบัญชี ข้อมูล ณ {RR.get('as_of', TODAY)}"))
    body += section(f"""
<p class="small mute">{T("Summaries of public law and official notices, with their sources. Not legal or tax advice; the source is the authority.", "สรุปจากกฎหมายและประกาศทางการ พร้อมแหล่งที่มา ไม่ใช่คำแนะนำทางกฎหมายหรือภาษี แหล่งที่มาคือหลักฐานที่ใช้อ้างอิง")}</p>
<h2>{T("The rules", "กฎ")}</h2><div class="grid2">{"".join(cards)}</div>
<h2 id="tax">{T("Tax", "ภาษี")}</h2><div class="grid2">{tax_cards}</div>
<h2 id="banks">{T("Banks and accounts", "ธนาคารและบัญชี")}</h2><div class="grid2">{bank_cards}</div>
<h2 id="licensed">{T("Licensed operators", "ผู้ประกอบธุรกิจที่ได้รับอนุญาต")}</h2>
{table([T("Operator", "ผู้ประกอบการ"), T("Licence", "ใบอนุญาต"), T("Since", "ตั้งแต่"), T("Status", "สถานะ"), T("Notes", "หมายเหตุ")], [op_rows])}
{("<h2 id='blocked'>" + T("Blocked and named", "ถูกปิดกั้นและถูกระบุชื่อ") + "</h2>" + table([T("Platform", "แพลตฟอร์ม"), T("Date", "วันที่"), T("Action", "การดำเนินการ")], [bl_rows])) if bl_rows else ""}
<h2 id="timeline">{T("Thailand, dated", "ประเทศไทย ตามลำดับเวลา")}</h2><ol class="tl">{tl_items}</ol>
{("<h2>" + T("Open questions", "คำถามที่ยังเปิดอยู่") + "</h2><ul>" + "".join(f"<li>{E(x)}</li>" for x in oq) + "</ul>") if oq else ""}
{subscribe()}
""")
    page(T("Rules", "กฎ"), body, "rules/", T("Thai crypto rules for foreigners: the SEC decree, licensed exchanges, blocked platforms, tax on foreign income and crypto, bank accounts and freezes, TouristDigiPay.",
                                              "กฎคริปโตของไทยสำหรับชาวต่างชาติ: พ.ร.ก. สินทรัพย์ดิจิทัล ศูนย์ซื้อขายที่ได้รับอนุญาต แพลตฟอร์มที่ถูกปิดกั้น ภาษีเงินได้จากต่างประเทศและคริปโต บัญชีธนาคารและการอายัด TouristDigiPay"),
         scripts=("i18n.js",))


def cards_page():
    P = R["products"]
    th_order = {"available": 0, "unclear": 1, "not available": 2}
    cards = sorted(P.get("cards") or [], key=lambda c: (th_order.get(c.get("thailand", ""), 3), c.get("name", "")))
    crow = []
    FL = {"issue": T("issue", "ออกบัตร"), "annual": T("annual", "รายปี"), "fx": "FX", "atm": "ATM", "topup": T("top-up", "เติมเงิน")}
    for c in cards:
        th_ = c.get("thailand", "")
        cls = {"available": "go", "not available": "red"}.get(th_, "amber")
        fees = (c.get("fees_th") if LANG == "th" else None) or c.get("fees") or {}
        fee_txt = " · ".join(f"{FL.get(k, k)}: {v}" for k, v in fees.items() if v)
        crow.append(f'<tr data-th="{E(th_)}"><td><b>{E(c.get("name", ""))}</b><br><span class="small mute">{E(fld(c, "issuer"))}</span></td>'
                    f'<td><span class="pill {cls}">{E(st_label(th_))}</span>{conf(c.get("confidence"))}<br><span class="small mute">{E(fld(c, "thailand_evidence"))}</span></td>'
                    f'<td class="small">{E(fld(c, "custody"))}<br>{E(fld(c, "physical"))}</td>'
                    f'<td class="small">{E(fee_txt)}</td><td class="small">{E(fld(c, "assets"))}</td>'
                    f'<td class="small">{cite(src_of(c))}{aff(c.get("id", ""))}</td></tr>')
    erow = []
    for x in P.get("exchanges") or []:
        lic = x.get("thai_licence", "")
        cls = "go" if lic.startswith("licensed") else "red" if "blocked" in lic else "amber"
        erow.append(f'<tr><td><b>{E(x.get("name", ""))}</b></td><td><span class="pill {cls}">{E(fld(x, "thai_licence"))}</span>{conf(x.get("confidence"))}</td>'
                    f'<td class="small">{E(fld(x, "foreigner_signup"))}</td><td class="small">{E(fld(x, "thb_withdrawal"))} {E(fld(x, "thb_fee"))}</td>'
                    f'<td class="small">{E(fld(x, "trading_fee"))}</td><td class="small">{E(fld(x, "networks"))}</td>'
                    f'<td class="small">{cite(src_of(x))}{aff(x.get("id", "")) if cls == "go" else ""}</td></tr>')
    rrow = "".join(f'<div class="cardx"><h3>{E(fld(r, "name"))}</h3>{conf(r.get("confidence"))}<p>{E(fld(r, "what"))}</p>'
                   f'<p class="small"><b>{T("Cost:", "ค่าใช้จ่าย:")}</b> {E(fld(r, "cost"))}</p><p class="small"><b>{T("For a foreigner:", "สำหรับชาวต่างชาติ:")}</b> {E(fld(r, "for_foreigners"))}{cite(src_of(r))}</p></div>'
                   for r in P.get("other_rails") or [])
    wrow = "".join(f'<tr><td><b>{E(w.get("name", ""))}</b></td><td>{E(fld(w, "kind"))}</td><td class="r">{E(str(w.get("price_usd", "")))}</td>'
                   f'<td class="small">{E(fld(w, "ships_to_thailand"))}</td><td class="small">{cite(src_of(w))}{aff(w.get("id", ""))}</td></tr>' for w in P.get("wallets") or [])
    atm = P.get("atms") or {}
    body = exit_head("cards/", T("A crypto card spends stablecoins or bitcoin as baht at any shop that takes Visa or Mastercard, and draws cash at a Thai ATM, with no Thai bank account behind it. Which ones issue to people living in Thailand is the question; the table answers it card by card, with the page it came from.",
                                 "บัตรคริปโตใช้สเตเบิลคอยน์หรือบิตคอยน์จ่ายเป็นเงินบาทได้ทุกร้านที่รับ Visa หรือ Mastercard และกดเงินสดจากตู้ ATM ในไทยได้ โดยไม่ต้องมีบัญชีธนาคารไทย คำถามคือใบไหนออกให้คนที่อยู่ในไทย ตารางตอบทีละใบ พร้อมหน้าที่เป็นที่มา"))
    fl = "".join(f'<button aria-pressed="{"true" if k == "all" else "false"}" data-f="{k}">{E(v)}</button>' for k, v in
                 (("all", T("All", "ทั้งหมด")), ("available", T("Available in Thailand", "ใช้ได้ในไทย")), ("unclear", T("Unclear", "ไม่ชัดเจน")), ("not available", T("Not available", "ใช้ไม่ได้"))))
    body += section(f"""
<div class="row" role="group" aria-label="{T('Filter cards', 'กรองบัตร')}">{fl}</div>
<h2>{T("Cards", "บัตร")}</h2>
{table([T("Card", "บัตร"), T("Thailand", "ในไทย"), T("Custody · form", "การถือครอง · รูปแบบ"), T("Fees", "ค่าธรรมเนียม"), T("Funded by", "เติมด้วย"), ""], crow, attrs=' id="cardtable"')}
<h2>{T("Exchanges", "ศูนย์ซื้อขาย")}</h2>
<p>{T("Licensed Thai exchanges pay baht to a Thai bank account in the holder's own name. Foreign exchanges are not licensed here; the SEC has blocked some of them.",
      "ศูนย์ซื้อขายไทยที่ได้รับอนุญาตจ่ายเงินบาทเข้าบัญชีธนาคารไทยที่เป็นชื่อของเจ้าของบัญชีเท่านั้น ศูนย์ซื้อขายต่างประเทศไม่ได้รับอนุญาตในไทย และ ก.ล.ต. ได้ปิดกั้นบางแห่งแล้ว")}</p>
{table([T("Exchange", "ศูนย์ซื้อขาย"), T("Thai licence", "ใบอนุญาตไทย"), T("Foreigners", "ชาวต่างชาติ"), T("Baht out", "ถอนเป็นบาท"), T("Trading fee", "ค่าซื้อขาย"), T("USDT networks", "เครือข่าย USDT"), ""], erow)}
<h2>{T("Other rails", "ช่องทางอื่น")}</h2><div class="grid2">{rrow}</div>
<h2>{T("Wallets", "กระเป๋า")}</h2>
{table([T("Wallet", "กระเป๋า"), T("Kind", "ประเภท"), "USD ›", T("Ships to Thailand", "ส่งมาไทย"), ""], [wrow])}
{("<h2>" + T("Crypto ATMs", "ตู้ ATM คริปโต") + "</h2><p>" + E(fld(atm, "thailand_crypto_atms")) + cite(src_of(atm)) + "</p>") if atm else ""}
{disclose()}
<script>(function(){{var bs=document.querySelectorAll('[data-f]');bs.forEach(function(b){{b.addEventListener('click',function(){{
bs.forEach(function(x){{x.setAttribute('aria-pressed',x===b)}});var f=b.dataset.f;
document.querySelectorAll('#cardtable tbody tr').forEach(function(r){{r.hidden=!(f==='all'||r.dataset.th===f)}})}})}})}})();</script>
""")
    page(T("Cards", "บัตร"), body, "cards/", T("Crypto debit cards that work in Thailand, Thai and foreign exchanges, Wise and other rails, hardware wallets: fees, eligibility, sources.",
                                                "บัตรเดบิตคริปโตที่ใช้ในไทยได้ ศูนย์ซื้อขายไทยและต่างประเทศ Wise และช่องทางอื่น กระเป๋าฮาร์ดแวร์: ค่าธรรมเนียม คุณสมบัติ แหล่งที่มา"),
         scripts=("i18n.js",))


def scams():
    S = R["scams"]  # stylecheck: allow — code
    srows = "".join(f'<tr><td>{E(str(s.get("year", "")))}</td><td>{E(fld(s, "metric"))}</td><td class="r">{s.get("value", 0):,}</td><td>{E(fld(s, "unit"))}</td>'
                    f'<td class="small">{E(fld(s, "scope"))}{cite(src_of(s))}</td></tr>'
                    for s in sorted(S.get("stats") or [], key=lambda s: str(s.get("year"))) if isinstance(s.get("value"), (int, float)))
    tcards = []
    for t in S.get("types") or []:
        ttl, alt = (t.get("name_th") or t.get("name"), t.get("name")) if LANG == "th" else (t.get("name"), t.get("name_th"))
        sg = (t.get("signs_th") if LANG == "th" else None) or t.get("signs") or []
        tcards.append(f'<div class="cardx"><h3>{E(ttl or "")}</h3>' + (f'<p style="color:var(--red);margin:.1rem 0">{E(alt)}</p>' if alt and alt != ttl else "")
                      + f'<p>{E(fld(t, "how"))}{cite(src_of(t))}</p>' + ("<ul class='small'>" + "".join(f"<li>{E(x)}</li>" for x in sg) + "</ul>" if sg else "") + "</div>")
    cases = sorted(S.get("cases") or [], key=lambda c: c.get("date", ""), reverse=True)
    citems = "".join(f'<li><time>{E(c.get("date", ""))}</time><div><b>{E(fld(c, "title"))}</b><p>{E(fld(c, "what"))}{conf(c.get("confidence"))}{cite(src_of(c))}</p></div></li>' for c in cases)
    chrows = []
    for c in S.get("channels") or []:
        ttl, alt = (c.get("name_th") or c.get("name"), c.get("name")) if LANG == "th" else (c.get("name"), c.get("name_th"))
        chrows.append(f'<div class="cardx"><h3>{E(ttl or "")}</h3>' + (f'<p style="color:var(--go);margin:.1rem 0">{E(alt)}</p>' if alt and alt != ttl else "")
                      + f'<p class="small">{E(fld(c, "how"))}</p>' + (f'<p class="small"><a href="{E(c["url"])}" rel="noopener" style="word-break:break-all">{E(c["url"])}</a></p>' if c.get("url") else "") + "</div>")
    body = exit_head("scams/", T("Most crypto losses in Thailand are not hacks. They are a person persuaded to send, and a bank account frozen because baht arrived from someone else's loss.",  # stylecheck: allow — facts about losses
                                 "ความเสียหายจากคริปโตในไทยส่วนใหญ่ไม่ได้มาจากการแฮ็ก แต่มาจากคนที่ถูกโน้มน้าวให้โอน และบัญชีธนาคารที่ถูกอายัดเพราะเงินบาทที่เข้ามาเป็นเงินจากความเสียหายของคนอื่น"), "red")
    body += section(f"""
<h2>{T("Numbers", "ตัวเลข")}</h2>{table([T("Year", "ปี"), T("Measure", "ตัวชี้วัด"), T("Value ›", "ค่า ›"), T("Unit", "หน่วย"), T("Scope", "ขอบเขต")], [srows])}
<h2>{T("How they work", "กลโกงทำงานอย่างไร")}</h2><div class="grid2">{"".join(tcards)}</div>
<h2>{T("Where to report", "แจ้งที่ไหน")}</h2><div class="grid3">{"".join(chrows)}</div>
<h2>{T("Cases", "คดี")}</h2><ol class="tl">{citems}</ol>
""")
    page(T("Scams", "กลโกง"), body, "scams/", T("Crypto scams in Thailand: call-centre gangs, fake investment, pig butchering, mule accounts and P2P freezes, address poisoning; the numbers and where to report.",  # stylecheck: allow — topic nouns in the page description
                                                 "กลโกงคริปโตในไทย: แก๊งคอลเซ็นเตอร์ หลอกลงทุน หมูตู้ บัญชีม้า การอายัดจาก P2P การวางยาที่อยู่ ตัวเลข และช่องทางแจ้งความ"),
         scripts=("i18n.js",))


ERAS = {"prehistory": ("Before bitcoin", "ก่อนบิตคอยน์"), "genesis": ("Genesis", "จุดกำเนิด"), "altcoins": ("Altcoins", "เหรียญทางเลือก"),
        "ico": ("The ICO wave", "คลื่น ICO"), "defi": ("DeFi and NFTs", "DeFi และ NFT"), "crash": ("The crashes", "การล่มสลาย"),
        "institutions": ("Institutions", "สถาบันการเงินเข้ามา"), "now": ("Now", "ปัจจุบัน")}


def history():
    ev = sorted(R["history"].get("events") or [], key=lambda e: e.get("date", ""))
    out, cur = [], None
    for e in ev:
        era = e.get("era", "")
        if era != cur:
            if out:
                out.append("</ol>")
            out.append(f'<p class="era">{E(T(*ERAS.get(era, (era, era))))}</p><ol class="tl">')
            cur = era
        out.append(f'<li class="{"th" if e.get("thailand") else ""}"><time>{E(e.get("date", ""))}</time><div><b>{E(fld(e, "title"))}</b>'
                   f'<p>{E(fld(e, "what"))}{conf(e.get("confidence"))}{cite(src_of(e))}</p></div></li>')
    if out:
        out.append("</ol>")
    body = exit_head("history/", T(f"From public-key cryptography to spot ETFs and stablecoin law: {len(ev)} dated events, with the Thai ones in green. The picture is a chain: the bitcoin genesis block's hash, then each tile the double SHA-256 of the one before.",
                                   f"จากการเข้ารหัสแบบกุญแจสาธารณะถึง ETF และกฎหมายสเตเบิลคอยน์: {len(ev)} เหตุการณ์ตามวันที่ เหตุการณ์ในไทยเป็นสีเขียว ภาพด้านบนคือห่วงโซ่: แฮชของบล็อกแรกของบิตคอยน์ แล้วแต่ละช่องคือ SHA-256 สองชั้นของช่องก่อนหน้า"))
    body += section(figure("btc_thb", T("Bitcoin in baht on Bitkub since 2018.", "บิตคอยน์ในสกุลบาทบน Bitkub ตั้งแต่ปี 2018") + cite("bitkub")) + "".join(out))
    page(T("History", "ประวัติ"), body, "history/", T("The history of crypto from Diffie-Hellman and DigiCash to bitcoin, Ethereum, stablecoins, the crashes, the ETFs and Thailand's rules.",
                                                      "ประวัติคริปโตตั้งแต่ Diffie-Hellman และ DigiCash ถึงบิตคอยน์ อีเธอเรียม สเตเบิลคอยน์ การล่มสลาย ETF และกฎของไทย"),
         scripts=("i18n.js",))


def words_page():
    W = sorted(R["words"].get("words") or [], key=lambda w: w.get("en", "").lower())
    items = []
    for w in W:
        wid = re.sub(r"[^a-z0-9]+", "-", w.get("en", "").lower()).strip("-")
        first, second = (w.get("th", ""), w.get("en", "")) if LANG == "th" else (w.get("en", ""), w.get("th", ""))
        items.append(f'<div id="{E(wid)}"><dt>{E(first)}<span class="th2">{E(second)}</span><span class="ro">{E(w.get("roman", ""))}</span></dt>'
                     f'<dd>{E(fld(w, "def"))}{cite(src_of(w))}</dd></div>')
    body = exit_head("words/", T(f"{len(W)} words, in English and in the Thai the SEC, the Bank of Thailand and the Thai press use, with a romanisation for reading aloud.",
                                 f"{len(W)} คำ ทั้งภาษาอังกฤษและภาษาไทยแบบที่ ก.ล.ต. ธนาคารแห่งประเทศไทย และสื่อไทยใช้ พร้อมคำอ่านอักษรโรมัน"))
    body += section(f'<dl class="words">{"".join(items)}</dl>')
    page(T("Words", "ศัพท์"), body, "words/", T("Crypto and Thai money words in English and Thai: สินทรัพย์ดิจิทัล, คริปโทเคอร์เรนซี, บัญชีม้า, พร้อมเพย์ and more, defined plainly.",
                                                 "ศัพท์คริปโตและการเงินไทย อังกฤษ-ไทย: สินทรัพย์ดิจิทัล คริปโทเคอร์เรนซี บัญชีม้า พร้อมเพย์ และอื่นๆ อธิบายแบบเข้าใจง่าย"),
         scripts=("i18n.js",))


# ------------------------------------------------------------------ sources, data, machine files
def sources_page():
    items = "".join(f'<li id="s{i + 1}"><b>{E(s.get("title") or s["url"])}</b>'
                    + (f' — {E(s.get("publisher", ""))}' if s.get("publisher") else "")
                    + (f' · {E(str(s.get("date", "")))}' if s.get("date") else "")
                    + f'<br><a href="{E(s["url"])}" rel="noopener" class="small" style="word-break:break-all">{E(s["url"])}</a></li>'
                    for i, s in enumerate(SRC_LIST))
    body = head(None, "Sources", "แหล่งที่มา", f"{len(SRC_LIST)} of them, numbered", f"{len(SRC_LIST)} แหล่ง เรียงตามหมายเลข", "band-history.jpg")
    body += section(f'<ol class="small" style="line-height:1.5">{items}</ol>')
    page(T("Sources", "แหล่งที่มา"), body, "sources/", T("Every source cited on Offrampt, numbered.", "แหล่งที่มาทั้งหมดที่อ้างถึงใน Offrampt เรียงตามหมายเลข"))


def data_page():
    files = [("facts.json", "Every computed number on the site", "ตัวเลขทุกตัวที่คำนวณในเว็บนี้"),
             ("series.json", "Daily series: BTC and ETH in baht, the premium, USDT against the bank rates, fees, USD/THB", "ข้อมูลรายวัน: BTC และ ETH ในสกุลบาท ส่วนต่างราคา USDT เทียบอัตราธนาคาร ค่าธรรมเนียม USD/THB"),
             ("rules.json", "Thai rules, operators, tax, banking, timeline", "กฎของไทย ผู้ประกอบการ ภาษี ธนาคาร ลำดับเวลา"),
             ("products.json", "Cards, exchanges, rails, wallets", "บัตร ศูนย์ซื้อขาย ช่องทาง กระเป๋า"),
             ("history.json", "The history, dated", "ประวัติตามวันที่"), ("scams.json", "Scam statistics, types, cases, channels", "สถิติกลโกง ประเภท คดี ช่องทางแจ้ง"),  # stylecheck: allow — data file label
             ("words.json", "The glossary, English and Thai", "อภิธานศัพท์ อังกฤษและไทย")]
    rows = "".join(f'<tr><td><a href="{BASE}data/{f}"><code>{f}</code></a></td><td>{E(T(de, dt_))}</td></tr>' for f, de, dt_ in files if (DATA / "research" / f).exists() or f in ("facts.json", "series.json"))
    body = head(None, "Data", "ข้อมูล", "Everything the pages are built from", "ทุกอย่างที่ใช้สร้างหน้าเว็บ", "band-markets.jpg",
                T("CC BY 4.0: copy it, chart it, build on it, and name Offrampt (offrampt.net) as the source.", "CC BY 4.0: คัดลอก ทำกราฟ ต่อยอดได้ โดยระบุ Offrampt (offrampt.net) เป็นแหล่งที่มา"))
    body += section(table([T("File", "ไฟล์"), T("What", "เนื้อหา")], [rows]) + f'<p>{T("Live rates, refreshed every fifteen minutes:", "อัตราสด อัปเดตทุกสิบห้านาที:")} <a href="{RATES}">{RATES}</a></p>')
    page(T("Data", "ข้อมูล"), body, "data/", T("Offrampt's data files: bitcoin and USDT in baht, the premium, Thai rules, cards, scams, glossary. CC BY 4.0.", "ไฟล์ข้อมูลของ Offrampt: บิตคอยน์และ USDT ในสกุลบาท ส่วนต่างราคา กฎของไทย บัตร กลโกง อภิธานศัพท์ CC BY 4.0"))  # stylecheck: allow — topic nouns in the page description


def agents_page():
    body = head(None, "For agents", "สำหรับเอเจนต์", "Machine-readable", "สำหรับเครื่องอ่าน", "band-tools.jpg")
    body += section(T(f'<p>Read <a href="{BASE}llms.txt">llms.txt</a> first. The data files are in <a href="{U("data/")}">/data/</a>. Live rates as JSON: <a href="{RATES}">{RATES}</a>. Every page carries schema.org JSON-LD and an hreflang pair. Licence CC BY 4.0: cite offrampt.net.</p>',
                      f'<p>เริ่มที่ <a href="{BASE}llms.txt">llms.txt</a> ไฟล์ข้อมูลอยู่ที่ <a href="{U("data/")}">/data/</a> อัตราสดเป็น JSON: <a href="{RATES}">{RATES}</a> ทุกหน้ามี JSON-LD ของ schema.org และคู่ hreflang สัญญาอนุญาต CC BY 4.0: อ้างอิง offrampt.net</p>'))
    page(T("For agents", "สำหรับเอเจนต์"), body, "for-agents/", T("How machines can read Offrampt.", "วิธีที่เครื่องอ่าน Offrampt"))


def not_found():
    doors = "".join(door(h) for h, *_r in EXITS)
    body = band("hero.jpg", sign(None, "Wrong exit", "ผิดทางออก", "That page is not on this road", "หน้านั้นไม่อยู่บนถนนสายนี้", tab="404"), "short") + section(f'<div class="doors">{doors}</div>')
    page("404", body, "404/")
    d = SITE / ("th" if LANG == "th" else "") / "404"
    shutil.move(d / "index.html", d.parent / "404.html")
    d.rmdir()


def machine_files():
    pages = [""] + [h for h, *_r in EXITS] + ["support/", "sources/", "data/", "for-agents/"]
    urls = "".join(f'<url><loc>{SITE_URL}/{p}{h}</loc><lastmod>{TODAY}</lastmod>'
                   f'<xhtml:link rel="alternate" hreflang="en" href="{SITE_URL}/{h}"/><xhtml:link rel="alternate" hreflang="th" href="{SITE_URL}/th/{h}"/></url>'
                   for h in pages for p in ("", "th/"))
    write(SITE / "sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">' + urls + "</urlset>")
    write(SITE / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n")
    Uu, P = F["usdt"], F["premium"]
    write(SITE / "llms.txt", f"""# {NAME}

> {TAG_EN}
> {TAG_TH}

{SITE_URL}/ (English) · {SITE_URL}/th/ (Thai)  ·  built {TODAY}  ·  CC BY 4.0, cite offrampt.net

## Computed findings
- USDT sold on Bitkub vs Thai banks' average buying rate for a dollar transfer: median {pct(Uu['vs_tt_median'])} over {Uu['days']} days ({Uu['from']} to {Uu['to']}); above the bank rate on {Uu['beat_tt_share']}% of days
- Bitcoin on Bitkub vs Binance x Bank of Thailand mid: median {pct(P['median'])}; within 1% on {P['within_1pct']}% of {P['days']} days; hottest year {P['hot_year']['year']} (median {pct(P['hot_year']['median'])})
- USDT = {F['bitkub']['usdt_share']}% of Bitkub's own-book baht volume (24h to {F['fetched']['bitkub_ticker']['at'][:10]})
- Stablecoins in circulation: ${F['stable']['total_usd'] / 1e9:.1f}B; USDT on Tron {F['stable']['usdt_tron_share']}%
- Bitcoin in baht: {thb(F['btc']['thb'])} on {F['btc']['date']}; high {thb(F['btc']['ath_thb'])} on {F['btc']['ath_date']}

## Pages
""" + "".join(f"- {SITE_URL}/{h} · {SITE_URL}/th/{h} — {en} / {th}: {se}\n" for h, en, th, se, st_, _i in EXITS) + f"""
## Data
- {SITE_URL}/data/facts.json
- {SITE_URL}/data/series.json
- {SITE_URL}/data/rules.json · products.json · history.json · scams.json · words.json (English with _th fields)
- live: {RATES}

Nothing here is advice about money, tax or law.

""" + fleet.llms_section(SELF, roster=FLEET))
    write(SITE / "icon.svg", '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect x="1" y="4" width="30" height="24" rx="5" fill="#0b6b43" stroke="#e8f2eb" stroke-width="2"/>'
          '<path d="M9 22 L21 10" stroke="#f3faf5" stroke-width="3.4" stroke-linecap="round"/><path d="M13 9 H22 V18" fill="none" stroke="#f3faf5" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/></svg>')
    write(SITE / "_headers", "/img/*\n  Cache-Control: public, max-age=604800\n/data/*\n  Access-Control-Allow-Origin: *\n")
    d = SITE / "data"
    d.mkdir(exist_ok=True)
    shutil.copy(BUILD / "facts.json", d / "facts.json")
    shutil.copy(BUILD / "series.json", d / "series.json")
    for k in R:
        if (DATA / "research" / f"{k}.json").exists():
            shutil.copy(DATA / "research" / f"{k}.json", d / f"{k}.json")


PAGES = (home, ramp, rules, cards_page, networks, markets, scams, how, history, words_page, tools, support, data_page, agents_page, not_found)


def main():
    global LANG
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True)
    shutil.copytree(IMG, SITE / "img", ignore=shutil.ignore_patterns("_*"))
    if OG.exists():
        shutil.copytree(OG, SITE / "img" / "og", ignore=shutil.ignore_patterns("*.json"))
    shutil.copytree(ROOT / "js", SITE / "js")
    for LANG in ("en", "th"):
        for fn in PAGES:
            fn()
    for LANG in ("en", "th"):
        sources_page()
    LANG = "en"
    machine_files()
    fleet.decorate(SITE, SELF, roster=FLEET)
    (SITE / ".basepath").write_text(BASE, encoding="utf-8")
    refs = MONEY.get("referral") or {}
    recv = MONEY.get("receive") or {}
    print(f"build/site ← {len(list(SITE.rglob('index.html')))} pages ({len(list((SITE / 'th').rglob('index.html')))} Thai); {len(SRC_LIST)} sources; "
          f"money: {sum(1 for v in recv.values() if v)} of {len(recv)} receiving addresses, {sum(1 for v in refs.values() if v)} referral links")


if __name__ == "__main__":
    main()
