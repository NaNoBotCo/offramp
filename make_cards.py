#!/usr/bin/env python3
"""Generate a 1200×630 OpenGraph share card for every Offrampt page.

Highway-signage aesthetic to match the site: white ground, an exit-sign green
header bar with the OFF·RAMP wordmark + exit arrow, the page title big, a short
hook under it, and a "no local bank needed" stamp. People share the promise, not
the logo — so the title and hook carry the card.

Writes assets/cards/<slug>.png (committed); build.py copies them into docs/ and
points each page's og:image at its own card. Run before build.py.

Needs Pillow. Uses macOS system fonts with graceful fallback.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from build import collect_notes, FOR_AGENTS_MD, TODAY

ROOT = Path(__file__).resolve().parent
CARDS = ROOT / "assets" / "cards"
W, H = 1200, 630
INK = (12, 15, 20)
EXIT = (23, 163, 74)
DEEP = (15, 122, 55)
SIGNAL = (232, 133, 12)
CHAIN = (34, 88, 214)
MUTED = (90, 100, 112)
PAPER = (244, 247, 245)
WHITE = (255, 255, 255)

DISPLAY = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
BODY = "/System/Library/Fonts/Supplemental/Arial.ttf"
MONO = "/System/Library/Fonts/Menlo.ttc"

EYEBROWS = {
    "/": "THE OFF-RAMP MANUAL · THAILAND",
    "/off-ramp-thailand/": "THE CRUX · THAILAND",
    "/crypto-cards/": "SPEND IT · CRYPTO CARDS",
    "/get-paid-in-crypto/": "FUNDAMENTALS · 101",
    "/scams/": "STAY SAFE",
    "/about/": "ABOUT OFFRAMPT",
    "/disclosure/": "DISCLOSURE",
    "/for-agents/": "FOR AGENTS & BOTS 🤖",
}


def font(path, size, index=0):
    try:
        return ImageFont.truetype(path, size, index=index)
    except Exception:
        return ImageFont.load_default()


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def chrome(d, img):
    """Green header bar with the wordmark + exit arrow; lane-line motif; footer rule."""
    d.rectangle([0, 0, W, 120], fill=EXIT)
    # faint diagonal lane lines in the body
    for i in range(-2, 24):
        x = i * 70
        d.line([(x, 120), (x + 260, H)], fill=(23, 163, 74, 20), width=2)
    # wordmark
    wf = font(DISPLAY, 52)
    d.text((66, 34), "OFF", font=wf, fill=WHITE)
    offw = d.textlength("OFF", font=wf)
    # RAMP in an inset chip
    rx = 66 + offw + 12
    rw = d.textlength("RAMPT", font=wf)
    d.rounded_rectangle([rx - 10, 32, rx + rw + 10, 96], radius=10, fill=INK)
    d.text((rx, 34), "RAMPT", font=wf, fill=WHITE)
    # exit-ramp arrow (drawn — the glyph isn't in Arial): down then right, into a head
    ax = rx + rw + 34
    d.line([(ax, 40), (ax, 74)], fill=INK, width=7)
    d.line([(ax, 74), (ax + 26, 74)], fill=INK, width=7)
    d.polygon([(ax + 44, 74), (ax + 22, 62), (ax + 22, 86)], fill=INK)
    d.text((W - 250, 46), "offrampt.net", font=font(MONO, 28, index=1), fill=WHITE)


def stamp(d, text, x, y, fill):
    tf = font(DISPLAY, 30)
    tw = d.textlength(text, font=tf)
    d.rounded_rectangle([x, y, x + tw + 36, y + 52], radius=10, outline=fill, width=4)
    d.text((x + 18, y + 8), text, font=tf, fill=fill)


def render(slug, eyebrow, title, hook):
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    chrome(d, img)

    d.text((66, 168), eyebrow[:60], font=font(DISPLAY, 26), fill=EXIT)

    # title — shrink to fit up to 3 lines
    size = 84
    while size > 46:
        tf = font(DISPLAY, size)
        if len(wrap(d, title, tf, W - 132)) <= 3:
            break
        size -= 5
    tf = font(DISPLAY, size)
    y = 212
    for ln in wrap(d, title, tf, W - 132)[:3]:
        d.text((66, y), ln, font=tf, fill=INK)
        y += int(size * 1.06)

    # Hook, but never let it collide with the bottom stamp zone (starts ~H-110).
    if hook:
        hf = font(BODY, 30)
        y += 8
        room = (H - 120) - y
        max_lines = max(0, min(2, room // 40))
        for ln in wrap(d, hook, hf, W - 132)[:max_lines]:
            d.text((66, y), ln, font=hf, fill=MUTED)
            y += 40

    stamp(d, "NO LOCAL BANK NEEDED", 66, H - 92, EXIT)
    d.text((W - 250, H - 78), "never touches", font=font(MONO, 24), fill=MUTED)
    d.text((W - 250, H - 52), "your funds", font=font(MONO, 24), fill=MUTED)
    CARDS.mkdir(parents=True, exist_ok=True)
    img.save(CARDS / (slug + ".png"), "PNG")


def card_slug(route):
    return route.strip("/").replace("/", "-") or "home"


def main():
    notes = dict(collect_notes())
    notes["/for-agents/"] = ("For Agents & Bots", {
        "type": "agents",
        "description": "Machine-readable surfaces and a documented way to help your human off-ramp safely."}, FOR_AGENTS_MD)
    def trim(s, n=118):
        s = " ".join((s or "").split())
        if len(s) <= n:
            return s
        cut = s[:n].rsplit(" ", 1)[0]
        return cut.rstrip(",.;:") + "…"

    n = 0
    for route, (title, meta, _b) in notes.items():
        eb = EYEBROWS.get(route, "OFFRAMPT")
        if route == "/":
            clean_title = "Get paid in crypto, spend it like cash"
        else:
            clean_title = title.split(" — ")[0].split(" · ")[0]
        hook = trim(meta.get("intro") or meta.get("description") or "")
        render(card_slug(route), eb, clean_title, hook)
        n += 1
    print("%d share cards -> %s" % (n, CARDS))


if __name__ == "__main__":
    main()
