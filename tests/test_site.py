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
check("four human exits in the nav", home.count('<nav aria-label="Exits">') == 1 and len(re.findall(r"<nav aria-label=\"Exits\">(.*?)</nav>", home)[0].split("</a>")) == 5)
check("home carries the calculator, the checker and a tip", all(x in home for x in ('id="calcbox"', 'id="addr"', 'class="tip"', 'src="/js/calc.js?v=', 'src="/js/addr.js?v=')))
check("every reference page opens with a way back", all('class="invite"' in (SITE / d / "index.html").read_text() for d in ("networks", "markets", "rules", "how", "history", "words", "sources", "data", "for-agents")))
check("human pages carry no invite", not any('class="invite"' in (SITE / d / "index.html").read_text() for d in ("tools", "ramp", "cards", "scams", "support")) and 'class="invite"' not in home)
check("no downward arrows", not any(a in p.read_text() for p in SITE.rglob("*.html") for a in ("↓", "↘", "↙", "⬇", "&darr;")))
check("every page has one h-level sign or h1", all(("class=\"sign" in p.read_text()) for p in SITE.rglob("index.html")))
check("sources page lists what pages cite", (SITE / "sources" / "index.html").read_text().count("<li id=\"s") >= 11)
check("no page links a referral without the disclosure",
      all(("rel=\"sponsored" not in p.read_text()) or ("referral links" in p.read_text()) for p in SITE.rglob("index.html")))
check("notranslate on every page", all('translate="no"' in p.read_text() and 'content="notranslate"' in p.read_text() for p in SITE.rglob("*.html")))
check("notranslate header", "X-Robots-Tag: notranslate" in (SITE / "_headers").read_text())
check("llms.txt exists", (SITE / "llms.txt").exists())
check("data files copied", (SITE / "data" / "facts.json").exists() and (SITE / "data" / "series.json").exists())
check("addr checker on networks and tools", all('src="/js/addr.js?v=' in (SITE / d / "index.html").read_text() for d in ("networks", "tools")))

if fails:
    print(f"{len(fails)} failing")
    sys.exit(1)
print("tests ok")
