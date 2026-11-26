#!/usr/bin/env python3
"""What the built pages say, against what compute.py computed."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "build" / "site"
F = json.loads((ROOT / "build" / "facts.json").read_text())
fails = []


def check(name, ok):
    print(f"  {'ok ' if ok else 'BAD'} {name}")
    if not ok:
        fails.append(name)


home = (SITE / "index.html").read_text()
mk = (SITE / "markets" / "index.html").read_text()
check("home prints the USDT-vs-wire median", f'{F["usdt"]["vs_tt_median"]:+.2f}%' in home)
check("markets prints the premium median", f'{F["premium"]["median"]:+.2f}%' in mk)
menu = re.findall(r'<nav aria-label="Main">(.*?)</nav>', home)
check("the menu: Baht, Paper Baht, Intel, Guides", len(menu) == 1 and menu[0].count("</a>") == 4 and all(h in menu[0] for h in ('href="/"', 'href="/paper/"', 'href="/intel/"', 'href="/#guides"')))
check("home carries the calculator sign and a tip", all(x in home for x in ('id="calcbox"', 'id="camt"', 'id="cbest"', 'id="cbars"', 'class="tip', 'src="/js/calc.js?v=')))
check("every reference page opens with a way back", all('class="invite"' in (SITE / d / "index.html").read_text() for d in ("networks", "markets", "rules", "how", "history", "words", "sources", "data", "for-agents")))
check("human pages carry no invite", not any('class="invite"' in (SITE / d / "index.html").read_text() for d in ("tools", "ramp", "cards", "scams", "support")) and 'class="invite"' not in home)
check("no downward arrows", not any(a in p.read_text() for p in SITE.rglob("*.html") for a in ("↓", "↘", "↙", "⬇", "&darr;")))
check("every page has one h-level sign or h1", all(("class=\"sign" in t or "<h1" in t) for t in (p.read_text() for p in SITE.rglob("index.html"))))
check("sources page lists what pages cite", (SITE / "sources" / "index.html").read_text().count("<li id=\"s") >= 11)
check("no page links a referral without the disclosure",
      all(("rel=\"sponsored" not in t) or ('class="disclose"' in t and ("referral links" in t or "ลิงก์แนะนำ" in t)) for t in (p.read_text() for p in SITE.rglob("index.html"))))
check("notranslate on every page", all('translate="no"' in p.read_text() and 'content="notranslate"' in p.read_text() for p in SITE.rglob("*.html")))
check("notranslate header", "X-Robots-Tag: notranslate" in (SITE / "_headers").read_text())
check("llms.txt exists", (SITE / "llms.txt").exists())
check("data files copied", (SITE / "data" / "facts.json").exists() and (SITE / "data" / "series.json").exists())
check("intel: index, a page per note, feeds and notes.json", all((SITE / p).exists() for p in ("intel/index.html", "th/intel/index.html", "intel/feed.xml", "th/intel/feed.xml", "intel/notes.json"))
      and len(list((SITE / "intel").glob("*/index.html"))) == len(json.loads((SITE / "intel" / "notes.json").read_text())["notes"]))
check("home carries paid help, Paper Baht, the intel, a follow form and the guides", all(x in home for x in ('id="help"', 'class="buy"', 'href="/paper/"', 'id="intel"', 'class="ilist"', 'id="follow"', 'id="guides"')))
for lang, file in (("en", SITE / "index.html"), ("th", SITE / "th" / "index.html")):
    h = file.read_text()
    check(f"{lang}: the sign, then help, then intel", h.index('id="calcbox"') < h.index('id="help"') < h.index('id="intel"') < h.index('id="guides"'))
check("the intel page carries the long view", 'id="long"' in (SITE / "intel" / "index.html").read_text())
check("intel feed is valid XML", __import__("xml.dom.minidom").dom.minidom.parse(str(SITE / "intel" / "feed.xml")) is not None)
check("addr checker on networks and tools", all('src="/js/addr.js?v=' in (SITE / d / "index.html").read_text() for d in ("networks", "tools")))

check("no page links a plain email address",
      not any(re.search(r'mailto:[^"?\s]*@', f.read_text(encoding="utf-8")) for f in SITE.rglob("*.html")))


if fails:
    print(f"{len(fails)} failing")
    sys.exit(1)
print("tests ok")
