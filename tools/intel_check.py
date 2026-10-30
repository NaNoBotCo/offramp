#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""intel_check.py — check intel notes before they are published.

    python3 tools/intel_check.py data/intel/notes/<file>.json [...]
    python3 tools/intel_check.py --all

Prints ✓ per note, or each problem; exits 1 on any problem. The format is in data/intel/brief.md.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from intel import KINDS, SHAPES, SPEEDS  # noqa: E402

PAGES = {"", "ramp/", "rules/", "cards/", "scams/", "networks/", "markets/", "tools/", "how/", "history/", "words/",  # stylecheck: allow — code: the words the check looks for
         "paper/", "frozen/", "intel/", "support/", "sources/", "data/"}  # stylecheck: allow — code: the words the check looks for
HOSTS = {"hongdam.net", "chiangmaivisadesk.com", "motdang.net", "sites.motdang.net", "nanobotco.github.io", "offrampt.net"}
SIGNALS = {"btc", "usdt", "stable", "hash", "rules"}
# reader-directed advice and warnings (her word 2026-10-04: facts, no warnings)
NANNY = re.compile(r"\b(you should|you must|make sure|be careful|beware|watch out|don't|do not|avoid|we recommend|consider (?:using|moving|selling|buying))\b", re.I)  # stylecheck: allow — code: the words the check looks for
DOWN = ("↓", "↘", "↙", "⬇")


def problems(p: Path) -> list[str]:
    out = []
    try:
        n = json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"does not parse: {e}"]
    need = ("id", "date", "kind", "title_en", "title_th", "dek_en", "dek_th", "body_en", "body_th", "shape", "speed", "read_en", "read_th", "sources", "links")
    out += [f"missing {k}" for k in need if not n.get(k)]
    if out:
        return out
    if n["id"] != p.stem:
        out.append(f"id {n['id']} is not the file name {p.stem}")
    if not re.match(r"^\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*$", p.stem):
        out.append("file name is not <YYYY-MM-DD>-<slug>")
    try:
        date.fromisoformat(n["date"])
    except ValueError:
        out.append("date is not YYYY-MM-DD")
    if not p.stem.startswith(n["date"]):
        out.append("file name date and date differ")
    if n["kind"] not in KINDS:
        out.append(f"kind {n['kind']} not in {sorted(KINDS)}")
    if n["shape"] not in SHAPES:
        out.append(f"shape {n['shape']} not in {sorted(SHAPES)}")
    if n["speed"] not in SPEEDS:
        out.append(f"speed {n['speed']} not in {sorted(SPEEDS)}")
    if n.get("signal") and n["signal"] not in SIGNALS:
        out.append(f"signal {n['signal']} not in {sorted(SIGNALS)}")
    if n.get("lead_until"):
        try:
            date.fromisoformat(n["lead_until"])
        except ValueError:
            out.append("lead_until is not YYYY-MM-DD")
    if len(n["title_en"]) > 100:
        out.append(f"title_en is {len(n['title_en'])} characters; 100 at most")
    if len(n["dek_en"]) > 240:
        out.append(f"dek_en is {len(n['dek_en'])} characters; 240 at most")
    be, bt = n["body_en"], n["body_th"]
    if not (isinstance(be, list) and isinstance(bt, list)) or not 2 <= len(be) <= 5:
        out.append("body_en needs 2 to 5 paragraphs")
    elif len(be) != len(bt):
        out.append(f"body_en has {len(be)} paragraphs, body_th {len(bt)}")
    for k in ("title_th", "dek_th", "read_th"):
        if not re.search(r"[฀-๿]", n[k]):
            out.append(f"{k} has no Thai")
    if isinstance(bt, list) and not all(re.search(r"[฀-๿]", x) for x in bt):
        out.append("a body_th paragraph has no Thai")
    en_text = " ".join([n["title_en"], n["dek_en"], n["read_en"]] + (be if isinstance(be, list) else []))
    for m in NANNY.finditer(en_text):
        out.append(f"advice or warning to the reader: '{m.group(0)}'")  # stylecheck: allow — code: the words the check looks for
    if any(a in json.dumps(n, ensure_ascii=False) for a in DOWN):
        out.append("a down arrow")
    srcs = n["sources"]
    if len(srcs) < 2:
        out.append("two sources at least")
    for s in srcs:
        if not (s.get("url", "").startswith("https://") or s.get("url", "").startswith("http://")):
            out.append(f"source without a url: {s.get('title', '')[:50]}")
        if not s.get("publisher"):
            out.append(f"source without a publisher: {s.get('url', '')[:60]}")
        if not s.get("date"):
            out.append(f"source without a date: {s.get('url', '')[:60]}")
    for lk in n["links"]:
        if not (lk.get("en") and lk.get("th")):
            out.append(f"link without both labels: {lk}")
        for h in [lk.get("href"), lk.get("href_en"), lk.get("href_th")]:
            if not h:
                continue
            if h.startswith("http"):
                host = re.sub(r"^https?://([^/]+).*", r"\1", h)
                if host not in HOSTS:
                    out.append(f"link to {host}: links go to Offrampt, Hongdam, Chiang Mai Visa Desk, Mot Dang or nanobotco.github.io")
            elif h.split("#")[0] not in PAGES:
                out.append(f"link to {h}: not an Offrampt page")
    if not any(lk.get("href") or lk.get("href_en") for lk in n["links"]):
        out.append("one link at least")
    style = Path.home() / ".claude" / "bin" / "stylecheck.py"
    if style.exists():
        r = subprocess.run([sys.executable, str(style), str(p)], capture_output=True, text=True)
        if r.returncode != 0:
            out += [ln for ln in r.stdout.splitlines() if ln.strip() and "hit(s)" not in ln and "STYLE.md" not in ln]
    return out


def main(argv):
    files = sorted((ROOT / "data" / "intel" / "notes").glob("*.json")) if argv == ["--all"] else [Path(a) for a in argv]
    if not files:
        print(__doc__)
        return 2
    bad = 0
    for f in files:
        ps = problems(f)
        if ps:
            bad += 1
            print(f"✗ {f.name}")
            for x in ps:
                print(f"   {x}")
        else:
            print(f"✓ {f.name}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
