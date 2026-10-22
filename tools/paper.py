# -*- coding: utf-8 -*-
"""paper.py — Paper Baht, offrampt.net/paper/ and /th/paper/.

Practice trading at live Bitkub prices (through the offrampt-rates worker's /paper/ routes).
One template (app/paper.html), one script (js/paper.js), the words below in English and Thai.

    python3 tools/paper.py <site dir>        # writes <site>/paper/index.html and <site>/th/paper/index.html
"""
import hashlib
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_URL = "https://offrampt.net"
RATES = "https://offrampt-rates.nanobotco.workers.dev/"
HONGDAM = "https://hongdam.net/"

W = {
    "name": ("Paper Baht", "บาทกระดาษ"),
    "by": ("Built by Hongdam Studio", "สร้างโดย หงส์ดำ สตูดิโอ"),
    "head": ("Paper Baht — practice trading at live Bitkub prices — Offrampt", "บาทกระดาษ — ฝึกเทรดด้วยราคาสดจาก Bitkub — Offrampt"),
    "desc": ("Trade ฿1,000,000 of paper money at live prices: eleven coins with gold among them, baht, US dollars, USDT and USDC, charts, orders at your price, a monkey to race, and yesterday on rewind.",
             "เทรดด้วยเงินกระดาษ ฿1,000,000 ที่ราคาสด: สิบเอ็ดเหรียญรวมทองคำ เงินบาท ดอลลาร์สหรัฐ USDT และ USDC กราฟ คำสั่งที่ราคาของคุณ แข่งกับลิง และย้อนเล่นเมื่อวาน"),
    "account": ("Your paper account", "บัญชีกระดาษของคุณ"),
    "total": ("Total", "รวม"),
    "sincestart": ("Since start", "ตั้งแต่เริ่ม"),
    "cash": ("Cash", "เงินสด"),
    "market": ("Market", "ตลาด"),
    "coins": ("Coins", "เหรียญ"),
    "range": ("Range", "ช่วงเวลา"),
    "r1D": ("Day", "วัน"), "r1W": ("Week", "สัปดาห์"), "r1M": ("Month", "เดือน"), "r1Y": ("Year", "ปี"),
    "controls": ("Trade, holdings, toys", "ซื้อขาย ที่ถืออยู่ ของเล่น"),
    "trade": ("Trade", "ซื้อขาย"), "mine": ("Mine", "ของฉัน"), "toys": ("Toys", "ของเล่น"), "about": ("About", "เกี่ยวกับ"),
    "buy": ("Buy", "ซื้อ"), "sell": ("Sell", "ขาย"),
    "amount": ("Amount in baht", "จำนวนเงิน (บาท)"),
    "half": ("Half", "ครึ่ง"), "all": ("All", "ทั้งหมด"),
    "when": ("When", "เมื่อไร"),
    "now": ("Now", "ตอนนี้"), "limit": ("At my price", "ที่ราคาของฉัน"), "stop": ("Stop", "สต็อป"),
    "def_now_buy": ("Buys now, at the asking price.", "ซื้อทันที ที่ราคาเสนอขาย"),
    "def_limit_buy": ("Waits, and buys when the price falls to yours.", "รอ แล้วซื้อเมื่อราคาลงมาถึงราคาของคุณ"),
    "def_stop_buy": ("Waits, and buys if the price rises to yours.", "รอ แล้วซื้อถ้าราคาขึ้นไปถึงราคาของคุณ"),
    "def_now_sell": ("Sells now, at the bid price.", "ขายทันที ที่ราคาเสนอซื้อ"),
    "def_limit_sell": ("Waits, and sells when the price rises to yours.", "รอ แล้วขายเมื่อราคาขึ้นไปถึงราคาของคุณ"),
    "def_stop_sell": ("Waits, and sells if the price falls to yours.", "รอ แล้วขายถ้าราคาลงมาถึงราคาของคุณ"),
    "price": ("Your price", "ราคาของคุณ"),
    "drag": ("Or drag the line on the chart.", "หรือลากเส้นบนกราฟ"),
    "youget": ("You get", "คุณได้"),
    "fee": ("fee", "ค่าธรรมเนียม"),
    "youhave": ("You have", "คุณมี"),
    "place": ("Place order", "ตั้งคำสั่ง"),
    "orders": ("Waiting orders", "คำสั่งที่รอ"),
    "cancel": ("Cancel", "ยกเลิก"),
    "holdings": ("Holdings", "ที่ถืออยู่"),
    "history": ("Trades", "ประวัติการซื้อขาย"),
    "nothing": ("Nothing yet.", "ยังไม่มี"),
    "value": ("Value", "มูลค่า"),
    "gain": ("Gain", "กำไร"),
    "bidask": ("Buying costs {a} · Selling gets {b}", "ราคาซื้อ {a} · ราคาขาย {b}"),
    "live": ("live", "สด"), "stale": ("waiting", "รอราคา"), "sec": ("s", " วิ"), "min": (" min", " นาที"),
    "tm_h": ("Time machine", "ไทม์แมชชีน"),
    "tm_p": ("{amt} of {coin} on {date} is {now} today.", "{amt} ใน {coin} เมื่อ {date} วันนี้เป็น {now}"),
    "tm_drag": ("Slide to pick a day.", "เลื่อนเพื่อเลือกวัน"),
    "monkey_h": ("You and the monkey", "คุณกับลิง"),
    "monkey_p": ("On your first day a monkey threw darts at the coin list and bought what it hit with ฿1,000,000.",
                 "วันแรกของคุณ ลิงปาลูกดอกใส่รายชื่อเหรียญ แล้วซื้อเหรียญที่โดนด้วยเงิน ฿1,000,000"),
    "monkey_has": ("The monkey holds", "ลิงถือ"),
    "you": ("You", "คุณ"), "monkey": ("Monkey", "ลิง"),
    "rw_h": ("Rewind", "ย้อนเวลา"),
    "rw_p": ("Play the last 24 hours of {coin} in about a minute, with ฿100,000. Buy and sell as it moves.",
             "เล่น 24 ชั่วโมงล่าสุดของ {coin} ในเวลาราวหนึ่งนาที ด้วยเงิน ฿100,000 ซื้อขายตามที่ราคาเคลื่อนไหว"),
    "rw_go": ("Start", "เริ่ม"), "rw_buy": ("Buy all", "ซื้อหมด"), "rw_sell": ("Sell all", "ขายหมด"), "rw_stop": ("End", "จบ"),
    "rw_end": ("You ended with {you}. Holding from the start: {hold}.", "คุณจบที่ {you} ถ้าถือตั้งแต่ต้น: {hold}"),
    "rw_best": ("Best", "สถิติ"),
    "rw_on": ("Rewind", "ย้อนเวลา"),
    "medals": ("Medals", "เหรียญรางวัล"),
    "reset": ("Start over with ฿1,000,000", "เริ่มใหม่ด้วย ฿1,000,000"),
    "reset_q": ("Clear this paper account and start over?", "ล้างบัญชีกระดาษนี้และเริ่มใหม่?"),
    "about_p1": ("Paper Baht is practice trading. The money is paper. The prices are Bitkub's, live, refreshed every ten seconds through the Offrampt rates service.",
                 "บาทกระดาษคือการฝึกเทรด เงินเป็นเงินกระดาษ ราคาเป็นราคาสดของ Bitkub อัปเดตทุกสิบวินาทีผ่านบริการอัตราของ Offrampt"),
    "about_p2": ("Buying pays the asking price; selling gets the bid. The gap between them is the spread. Each trade pays the fee below.",
                 "การซื้อจ่ายที่ราคาเสนอขาย การขายได้ที่ราคาเสนอซื้อ ส่วนต่างระหว่างสองราคาคือสเปรด ทุกการซื้อขายเสียค่าธรรมเนียมตามด้านล่าง"),
    "about_p3": ("The account is saved in this browser.", "บัญชีบันทึกไว้ในเบราว์เซอร์นี้"),
    "fee_l": ("Fee per trade, %", "ค่าธรรมเนียมต่อครั้ง (%)"),
    "sound_l": ("Sounds", "เสียง"),
    "credit": ("Built by Hongdam Studio, Chiang Rai.", "สร้างโดย หงส์ดำ สตูดิโอ เชียงราย"),
    "back": ("Offrampt: crypto in Thailand, and the ways out to baht", "Offrampt: คริปโตในไทย และทางออกสู่เงินบาท"),
    "calc": ("How many baht for your crypto?", "คริปโตของคุณแลกได้กี่บาท?"),
    "bought": ("Bought {q} {coin} at {px}", "ซื้อ {q} {coin} ที่ {px}"),
    "sold": ("Sold {q} {coin} at {px}: {pnl}", "ขาย {q} {coin} ที่ {px}: {pnl}"),
    "placed": ("Waiting: {side} {coin} at {px}", "รออยู่: {side} {coin} ที่ {px}"),
    "filled": ("Filled. ", "สำเร็จ "),
    "cancelled": ("Order cancelled.", "ยกเลิกคำสั่งแล้ว"),
    "e_cash": ("Not enough cash.", "เงินสดไม่พอ"),
    "e_min": ("The smallest amount is {min}.", "จำนวนขั้นต่ำ {min}"),
    "e_none": ("You hold no {coin}.", "คุณไม่มี {coin}"),
    "e_price": ("Set your price first.", "ตั้งราคาก่อน"),
    "e_noprice": ("Waiting for prices.", "กำลังรอราคา"),
    "e_chart": ("The chart is not loading. Prices and trades still work.", "กราฟโหลดไม่ได้ ราคาและการซื้อขายยังใช้ได้"),
    "m_first": ("First trade", "ซื้อขายครั้งแรก"), "m_ten": ("Ten trades", "สิบครั้ง"), "m_gold": ("Gold in the jar", "มีทองในโหล"),
    "m_five": ("Five coins at once", "ห้าเหรียญพร้อมกัน"), "m_green": ("Above ฿1,000,000", "เกิน ฿1,000,000"),
    "m_monkey": ("Ahead of the monkey", "นำลิง"), "m_rewind": ("Rewound a day", "ย้อนครบหนึ่งวัน"), "m_patient": ("Filled at my price", "ได้ที่ราคาของฉัน"),
    "medal_new": ("Medal: {m}", "ได้เหรียญ: {m}"),
    "equity": ("Your total over time", "มูลค่ารวมตามเวลา"),
    "chart_aria": ("{coin}, {range}: from {a} to {b}, high {h}, low {l}.", "{coin} {range}: จาก {a} ถึง {b} สูงสุด {h} ต่ำสุด {l}"),
    "loading": ("Loading", "กำลังโหลด"),
    "noscript": ("Paper Baht needs JavaScript.", "บาทกระดาษต้องใช้ JavaScript"),
    "fine": ("Nothing here is advice about money, tax or law.", "เนื้อหาในเว็บนี้ไม่ใช่คำแนะนำด้านการเงิน ภาษี หรือกฎหมาย"),
    "c_BTC": ("Bitcoin", "บิตคอยน์"), "c_ETH": ("Ether", "อีเธอร์"), "c_XAUT": ("Gold", "ทองคำ"), "c_USDT": ("Tether dollar", "ดอลลาร์เทเธอร์"),
    "c_SOL": ("Solana", "โซลานา"), "c_XRP": ("XRP", "XRP"), "c_DOGE": ("Dogecoin", "โดชคอยน์"), "c_BNB": ("BNB", "BNB"),
    "money": ("Money", "เงิน"),
    "pay_in": ("Pay in", "จ่ายเป็น"), "get_in": ("Get", "รับเป็น"),
    "amount_in": ("Amount in {m}", "จำนวน ({m})"),
    "no_usdt": ("{coin} has no USDT market on Bitkub.", "{coin} ไม่มีตลาด USDT บน Bitkub"),
    "m_THB": ("Baht", "บาท"), "m_USD": ("US dollars, cash", "ดอลลาร์สหรัฐ เงินสด"), "m_USDT": ("Tether (USDT)", "เทเธอร์ (USDT)"), "m_USDC": ("USD Coin (USDC)", "ยูเอสดีคอยน์ (USDC)"),
    "ms_THB": ("Baht", "บาท"), "ms_USD": ("Dollars", "ดอลลาร์"), "ms_USDT": ("USDT", "USDT"), "ms_USDC": ("USDC", "USDC"),
    "wallet": ("Your money", "เงินของคุณ"),
    "swap": ("Swap", "แลก"), "from": ("From", "จาก"), "to": ("To", "เป็น"), "flip": ("Swap the two", "สลับ"),
    "swap_go": ("Swap {a} for {m}", "แลก {a} เป็น{m}"),
    "swapped": ("Swapped {a} for {b}", "แลก {a} ได้ {b}"),
    "leg_sell_cash": ("Sell {x} to {shop} at {r}: {y}", "ขาย {x} ให้ {shop} อัตรา {r}: {y}"),
    "leg_buy_cash": ("Buy {y} from {shop} at {r}", "ซื้อ {y} จาก {shop} อัตรา {r}"),
    "leg_sell_coin": ("Sell {x} on Bitkub at {r}: {y}, fee {f}", "ขาย {x} บน Bitkub อัตรา {r}: {y} ค่าธรรมเนียม {f}"),
    "leg_buy_coin": ("Buy {y} on Bitkub at {r}, fee {f}", "ซื้อ {y} บน Bitkub อัตรา {r} ค่าธรรมเนียม {f}"),
    "change": ("{c} change back in baht", "เงินทอน {c}"),
    "same": ("Pick two different kinds of money.", "เลือกเงินสองแบบที่ต่างกัน"),
    "e_bal": ("Not enough {m}.", "{m} ไม่พอ"),
    "rt_h": ("Out and back", "แลกไปแล้วแลกกลับ"),
    "rt_p": ("฿10,000 swapped to each, then straight back to baht. The gap is the spread and the fees.", "แลก ฿10,000 ไปแต่ละแบบแล้วแลกกลับเป็นบาททันที ส่วนที่หายไปคือส่วนต่างราคาและค่าธรรมเนียม"),
    "rates_src": ("Dollar notes: the best Chiang Mai money changer, rates from thairate.com (CC BY 4.0), refreshed every fifteen minutes. USDT and USDC: Bitkub, live. Dollar notes come in whole dollars; change comes back in baht.",
                  "ธนบัตรดอลลาร์: ร้านแลกเงินที่ให้ราคาดีที่สุดในเชียงใหม่ อัตราจาก thairate.com (CC BY 4.0) อัปเดตทุกสิบห้านาที USDT และ USDC: ราคาสดจาก Bitkub ธนบัตรดอลลาร์แลกเป็นจำนวนเต็ม เงินทอนคืนเป็นบาท"),
    "show_usd": ("Tap to show in dollars", "แตะเพื่อแสดงเป็นดอลลาร์"), "show_thb": ("Tap to show in baht", "แตะเพื่อแสดงเป็นบาท"),
    "about_p4": ("The account holds baht, US dollar notes, USDT and USDC. Swaps between them go through baht, the way they do in Thailand: dollar notes at a money changer, USDT and USDC on Bitkub. Coins can be paid for in baht, or in USDT where Bitkub has a USDT market. Totals in dollars use the Bank of Thailand reference rate.",
                 "บัญชีถือเงินบาท ธนบัตรดอลลาร์สหรัฐ USDT และ USDC การแลกระหว่างกันผ่านเงินบาทเหมือนที่ทำในไทย: ธนบัตรดอลลาร์ที่ร้านแลกเงิน USDT และ USDC บน Bitkub ซื้อเหรียญได้ด้วยบาท หรือด้วย USDT ถ้า Bitkub มีตลาด USDT ยอดรวมเป็นดอลลาร์ใช้อัตราอ้างอิงของธนาคารแห่งประเทศไทย"),
    "m_swap": ("First swap", "แลกครั้งแรก"), "m_four": ("Four kinds of money", "เงินครบสี่แบบ"),
    "c_USDC": ("USD Coin", "ยูเอสดีคอยน์"),
    "c_ADA": ("Cardano", "คาร์ดาโน"), "c_KUB": ("Bitkub Coin", "บิทคับคอยน์"), "c_LINK": ("Chainlink", "เชนลิงก์"), "c_SUI": ("Sui", "ซุย"),
}

PICS = {
    "THB": '<svg class="disc" viewBox="0 0 28 28" aria-hidden="true"><rect x="2" y="7" width="24" height="14" rx="2.5" fill="#2fa66a"/><text x="14" y="17.4" text-anchor="middle" font-size="9" font-weight="800" fill="#0b0f15" font-family="system-ui">฿</text></svg>',
    "USD": '<svg class="disc" viewBox="0 0 28 28" aria-hidden="true"><rect x="2" y="7" width="24" height="14" rx="2.5" fill="#7fa56b"/><text x="14" y="17.4" text-anchor="middle" font-size="9" font-weight="800" fill="#0b0f15" font-family="system-ui">$</text></svg>',
    "USDT": '<svg class="disc" viewBox="0 0 28 28" aria-hidden="true"><circle cx="14" cy="14" r="12.5" fill="#26a17b"/><text x="14" y="18.6" text-anchor="middle" font-size="12" font-weight="800" fill="#fff" font-family="system-ui">₮</text></svg>',
    "USDC": '<svg class="disc" viewBox="0 0 28 28" aria-hidden="true"><circle cx="14" cy="14" r="12.5" fill="#2775ca"/><text x="14" y="18.6" text-anchor="middle" font-size="12" font-weight="800" fill="#fff" font-family="system-ui">$</text></svg>',
}

PLATE = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 19 L17 7" stroke="#f3faf5" stroke-width="3.4" '
         'stroke-linecap="round"/><path d="M9 6 H18 V15" fill="none" stroke="#f3faf5" stroke-width="3.4" '
         'stroke-linecap="round" stroke-linejoin="round"/></svg>')


def build(site: Path, og_en: str = "/img/og/en-tools.jpg", og_th: str = "/img/og/th-tools.jpg"):
    tpl = (ROOT / "app" / "paper.html").read_text(encoding="utf-8")
    jsv = hashlib.sha1((ROOT / "js" / "paper.js").read_bytes()).hexdigest()[:8]
    out = []
    for lang in ("en", "th"):
        i = 0 if lang == "en" else 1
        words = {k: v[i] for k, v in W.items()}
        en_url, th_url = SITE_URL + "/paper/", SITE_URL + "/th/paper/"
        canon = en_url if lang == "en" else th_url
        ld = {"@context": "https://schema.org", "@type": "WebApplication", "name": words["name"], "url": canon,
              "applicationCategory": "FinanceApplication", "operatingSystem": "Any", "inLanguage": lang,
              "description": words["desc"], "isAccessibleForFree": True,
              "offers": {"@type": "Offer", "price": "0", "priceCurrency": "THB"},
              "isPartOf": {"@type": "WebSite", "name": "Offrampt", "url": SITE_URL + "/"},
              "creator": {"@type": "Organization", "name": "Hongdam Studio", "alternateName": "หงส์ดำ", "url": HONGDAM},
              "license": "https://opensource.org/licenses/MIT"}
        rep = {
            "lang": lang, "title": html.escape(words["head"]), "desc": html.escape(words["desc"]), "canon": canon,
            "url_en": en_url, "url_th": th_url, "home": "/" if lang == "en" else "/th/",
            "other": "/th/paper/" if lang == "en" else "/paper/", "other_lang": "th" if lang == "en" else "en",
            "other_label": "ไทย" if lang == "en" else "EN", "og": SITE_URL + (og_en if lang == "en" else og_th),
            "og_locale": "en_US" if lang == "en" else "th_TH", "plate": PLATE, "rates": RATES, "hongdam": HONGDAM,
            "jsv": jsv, "ld": json.dumps(ld, ensure_ascii=False),
            "tjson": json.dumps(words, ensure_ascii=False).replace("</", "<\\/"),
        }
        page = tpl
        for m, svg in PICS.items():
            page = page.replace("{{pic:" + m + "}}", svg)
        for k, v in words.items():
            page = page.replace("{{t:" + k + "}}", html.escape(v))
        for k, v in rep.items():
            page = page.replace("{{" + k + "}}", v)
        assert "{{" not in page, page[page.index("{{"):page.index("{{") + 40]
        dest = site / ("th/paper" if lang == "th" else "paper") / "index.html"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(page, encoding="utf-8")
        out.append(dest)
    js = site / "js" / "paper.js"
    js.parent.mkdir(parents=True, exist_ok=True)
    js.write_bytes((ROOT / "js" / "paper.js").read_bytes())
    return out


if __name__ == "__main__":
    for p in build(Path(sys.argv[1] if len(sys.argv) > 1 else ROOT / "build" / "site")):
        print(p)
