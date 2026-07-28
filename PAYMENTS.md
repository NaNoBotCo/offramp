# Offrampt — getting you set up for payments

Your working notes for three money flows: **your own receiving stack**, **affiliate
income**, and the **paid consult**. All three land in the same place, so we set that up
first. This is operational setup, not investment or tax advice — confirm current terms
at each provider.

**What I can't do for you** (hard rules): create accounts, enter your passwords/KYC, hold
your seed phrase, or move funds. Those steps are marked **[you]**. Everything else I've
scaffolded or can build.

---

## Part 0 — Your receiving rail: ✅ USDT on Tron (TRC-20) — CONFIRMED 2026-07-25

Standardized. Everything points at it. Setup walkthrough: **`bybit-setup.md`**.

Pick **one stablecoin + network** to standardize on. Everything else points at it.

| Rail | Best at | Trade-off |
| --- | --- | --- |
| **USDT on Tron (TRC-20)** ← recommended | Deepest THB P2P liquidity + lowest fees; what Thai merchants actually trade → easiest to turn into baht | Tron is more centralized; USDT issuer less transparent than USDC |
| **USDC on Base** | Reputable issuer (Circle), cheap L2 fees; what many US payers send | Thinner *direct* THB P2P — you often convert to USDT to off-ramp |

**My recommendation:** receive and off-ramp on **USDT / TRC-20**, because your recurring
pain is turning crypto into *spendable baht*, and that's the rail Thai P2P runs on. When a
payer can only send USDC (common from US Coinbase), take it — the exchange converts
USDC→USDT for a few cents before you sell. For **savings you're not spending soon**, hold
USDC on a hardware wallet instead (see below).

> **Decision for you:** confirm USDT/TRC-20 as the primary rail, or tell me otherwise.
> Once set, I'll bake the exact address/network into the payment-details template and the
> consult page.

---

## Part 1 — Your receiving stack

Goal: get paid in crypto safely, then off-ramp to baht. Two wallets, one exchange.

1. **[you] A spending/off-ramp exchange account** — Bybit *or* Binance (you'll want it for
   P2P → baht anyway, and it doubles as an affiliate earner). This is where you receive,
   convert, and sell to baht. KYC required.
2. **[you] A self-custody hot wallet** — a reputable mobile wallet for receiving smaller
   amounts and funding a crypto card. You control the keys.
3. **[you] A hardware wallet for savings** — Ledger or Trezor. Anything you're *not* about
   to spend lives here, offline. (Also an affiliate line — buy through your own link once
   approved.)
4. **Standardize the ask.** Tell every payer the same thing: coin + network + address.
   I've templated this — see `payment-details.template.md` in this folder. Fill in your
   address once and reuse it.
5. **Off-ramp path** (the recurring loop): receive USDT → on the exchange, **sell P2P for
   baht** (PromptPay if you have a Thai bank) or **fund a crypto card** to spend directly.
   This is literally the [Off-ramp Thailand](content/off-ramp-thailand.md) guide.

:::safety Non-negotiable
Your **seed phrase** is your money. Write it on paper, store it offline, type it only into
your own wallet's recovery screen. No one — no exchange, no "support", not me — ever needs
it. I will never ask for it and can't hold it for you.
:::

---

## Part 2 — Affiliate income (the site's money model)

The scaffolding is done: **`affiliate_ids.local.py`** (git-ignored) is where your real
referral URLs go. Uncomment a line, paste your link, rebuild — the build reports how many
are still placeholders so nothing half-finished ships live.

**Apply in this order** (highest intent first; don't spread thin):

1. **Bybit** — [you] one account = card + exchange + P2P + referral. Instant in-app
   referral code; apply for the Affiliate program for higher %. Pays in **USDT** to your
   balance → straight into your rail.
2. **Binance** — [you] deepest THB P2P; instant referral code, Affiliate program by
   application. Pays in crypto.
3. Then, as the content already supports them: **Ledger/Trezor** (hardware), **Koinly**
   (tax, pays cash), **Wise** (fiat leg). Lower priority: OKX, Kraken, RedotPay, Gnosis Pay.

**How you actually get paid:** most crypto programs pay **in USDT to your exchange balance**
(monthly) — same rail as everything else. Koinly/Wise pay cash to a bank or PayPal. Note
each program's payout method as you sign up.

> **Decision for you:** confirm the first-two priority (Bybit + Binance), or reorder.

---

## Part 3 — The paid consult ("set up my off-ramp")

The on-brand move: **get paid in crypto for a crypto consult** — it dogfoods Offrampt and
lands in your rail. Offer a fiat fallback for people who aren't there yet.

- **Crypto invoice** (primary): flat fee in USDT to your receiving address. Zero fees, no
  processor, no custody — fully inside the bright line.
- **Fiat fallback:** ko-fi (you already have an account) or a Stripe Payment Link [you] for
  card payers. Ko-fi is fastest; note the current footer link points at Defiant's ko-fi
  (`defiantchiangmai`) — we can give Offrampt its own or reuse it.

I can build a `/consult/` page (booking + what's included + pay-in-crypto instructions)
whenever you want — it just needs three answers:

> **Decisions for you:** (1) price? (2) what's included / how long? (3) crypto-only, or add
> ko-fi fiat fallback?

---

## Status

- ✅ `affiliate_ids.local.py` scaffold created (git-ignored) — ready for real codes.
- ✅ `payment-details.template.md` — the "here's how to pay me" one-pager to fill in.
- ⏳ Waiting on your Part 0 rail confirmation + the consult answers to wire the rest.
