# OffRamp — project spec

**Status:** Phase 0 not started (spec only). Created 2026-07-25.
**One line:** The manual for getting paid in crypto and turning it into spendable
local money when you don't have a local bank account.
**Owner:** NaN. Sibling to [Defiant](../defiant-site) — same expat audience,
different pain. Thailand-first, hub-expandable.

Born from a real moment: paying Defiant's owner (Thailand-based, no Thai bank) is
cheaper in crypto than through US banking — and the network confusion (native BTC
vs a Base `0x` address) nearly stranded funds. That lived pain *is* the value prop.

---

## Thesis

Location-independent people get paid in crypto easily. Turning it into money they
can actually **spend locally, without a local bank account**, is the hard part —
and it's full of expensive mistakes (wrong network, bad P2P deals, scam cards).
OffRamp is the trustworthy, bot-legible manual for that, monetized by pointing
readers at the exact tools that solve it.

---

## Money model (intent-matched affiliates — the content *is* the funnel)

The products a reader needs to cash out without a bank are the highest-paying
crypto referrals, so conversion is high and the ads aren't bolted on.

- **Crypto debit cards** — the money core. Spend/ATM crypto with no local bank;
  referrals pay well. Flagship page: region-filtered "which cards actually work in
  Thailand / your country."
- **Exchange + P2P referrals** — Binance, Bybit, Kraken, OKX pay lifetime % of
  trading fees; off-ramp guides route readers to sign up.
- **Hardware wallets** (Ledger/Trezor), **tax software** (Koinly/CoinTracker),
  **VPN**, **Wise**, **insurance** (SafetyWing — cross from Defiant).
- **Travelpayouts** marker **749581** (reuse) for travel-adjacent links.
- **Upsell later:** paid "set up my off-ramp" consult (Defiant-style) + country
  playbook PDFs + sponsored directory placement (disclosed).

## Content architecture (the rich info)

- **Get paid in crypto 101** — wallets, addresses, stablecoins vs volatile,
  networks (native BTC vs wrapped/Base, which-USDC-on-which-chain) taught so nobody
  loses funds.
- **Off-ramp without a local bank** — the crux page: P2P, crypto cards, ATMs, OTC;
  a "do I need a local bank?" matrix.
- **Country playbooks** — Thailand first (Bitkub/Satang need a Thai bank; P2P →
  PromptPay; card + ATM options), then nomad hubs (Portugal, Georgia, Mexico,
  Vietnam, Philippines, UAE). Same hub-expansion pattern as Defiant's cities.
- **Tax & compliance** — US-person crypto basics (income vs cap gains, FBAR/FATCA
  flags) + local basics. Marked general info, not advice.
- **Scams & safety** — wrong-network loss, P2P fraud, seed-phrase security.

## Free tools (SEO magnets + lead gen)

- **"Is this a real crypto address?" validator** — seed already exists (BIP-173 BTC
  checksum validator written in the Defiant session 2026-07-25); extend to
  ETH/Base; catches the `0x`-vs-`bc1` mistake that started this project.
- **Off-ramp fee calculator** — card vs P2P vs exchange for a given amount + country.
- **"Which route for my country" picker.**

## Standard requirements (baked in day one — the house style)

- Static generator → `docs/` → GitHub Pages; one self-contained repo; git from start.
- **Bot-friendly:** per-page JSON-LD (Article + FAQPage + HowTo), `llms.txt` /
  `llms-full.txt`, `/for-agents`, friendly `robots.txt`, Atom feed, sitemap,
  routes registry (single source of truth for nav/doors).
- **Wired to share:** per-page OG share cards (reuse `make_cards.py`), OG/Twitter tags.
- Wayback archiving launcher; low-vision-readable; no personal paths leaked;
  Desktop launcher; tailored `.gitignore` (affiliate IDs / secrets never committed).
- **FTC affiliate disclosure** on every page with links; per-claim sourcing marks
  (*Inference —* / plain = verified) — this is YMYL, accuracy is money.

## Bright line (keeps it legal, no license needed)

- **Inform and refer only — never touch customer funds.** The moment a site
  custodies, exchanges, or moves someone's crypto it's a money transmitter and needs
  licensing. OffRamp is information + affiliate + referral, exactly like Defiant is
  for clinics. Boundary baked into the model.
- Not financial / tax / legal advice; prominent disclaimers; "confirm with a
  licensed pro."

## Phasing

- **Phase 0** — clone the generator / bot-hospitality / share-card stack into this
  repo; lock the name (OffRamp — approved); affiliate config (real IDs where held,
  placeholders else).
- **Phase 1** — the two money pages: **crypto cards comparison** + **Thailand
  off-ramp guide**. Ship + share cards + Wayback.
- **Phase 2** — address validator + fee calculator (SEO magnets).
- **Phase 3** — more country playbooks; tax + safety pillars.
- **Phase 4** — consult upsell + playbook PDFs.

## Open decisions

- Domain (offramp.* — check availability; .to like defiant.to? .money? .guide?).
- How closely to cross-link Defiant (shared audience) vs keep separate brands.
- Which affiliate programs to apply to first (cards + one exchange = the core).
