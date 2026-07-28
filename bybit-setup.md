# Bybit — click-by-click setup

Your first exchange account: **receive USDT, off-ramp to baht, and earn the site's top
affiliate**, all in one place. Rail is **USDT on Tron (TRC-20)**.

**What I can't do for you:** create the account, enter your password, or complete identity
verification — those involve your credentials and ID, so they're yours to click. Steps
that are yours are marked **[you]**. I've done everything around them.

Bybit's menu labels shift over time; where a label has moved, look for the nearest match.
*(The UI specifics below are inference — confirm as you go.)*

---

## Before you start — the 60-second regulatory reality check

Bybit is a large global exchange, **not licensed by the Thai SEC** — in 2024 the Thai SEC
named several offshore exchanges (Bybit among them) for operating without a local license,
and in-country access can be geo-restricted. *(Inference — confirm current status.)* Plenty
of expats use it anyway via the app; just go in informed.

- If you have a **Thai ID + Thai bank**, the licensed alternative is **Binance TH (by Gulf
  Binance)** — SEC-registered, integrates PromptPay directly. Tell me and I'll write that
  one instead.
- If you **don't** (the whole reason Offrampt exists), Bybit + its card is the pragmatic
  pick. Continue below.

---

## Part A — Create the account **[you]**

1. Go to **bybit.com** (or install the Bybit app from the official App Store / Play Store
   listing — check the developer is "Bybit").
2. Sign up with **"Continue with Google" → skunkhaus@gmail.com** (your usual login).
3. **Lock down the Google account first** — since it now unlocks Bybit, make sure that
   Gmail has its own 2-factor turned on. Everything downstream depends on it.
4. In Bybit: **Account & Security → Two-Factor Authentication → Google Authenticator**
   (an authenticator app, **not SMS** — SIM-swap is a real attack). Save the backup code
   offline.

## Part B — Verify your identity (KYC) **[you]**

You need this to deposit, withdraw, use P2P, and get the card.

1. **Profile → Identity Verification** (a.k.a. KYC), Level 1.
2. Have your **passport** ready; follow the prompts (photo of the ID + a selfie).
3. Enter your own details — I can't do this part. Approval is usually minutes, sometimes
   a few hours.

## Part C — Get your USDT / TRC-20 receiving address

This is the address you'll paste into `payment-details.template.md` and hand to payers.

1. **Assets → Deposit** (or "Deposit" on the app home).
2. Search and select **USDT**.
3. **Chain type → TRC20** (Tron). ⚠️ This must say TRC20 — the same USDT on a different
   chain is a different address and can't be mixed.
4. **Copy the address** (it starts with **`T…`**). This is your receiving address.
5. Paste it into `payment-details.template.md` (the "starts with T…" blank).
6. **Test it:** have your first payer send **1 USDT** first. Confirm it lands in your Bybit
   Assets, *then* have them send the rest. Always.

## Part D — Turn USDT into baht (the off-ramp loop)

Two ways, depending on the Thai-bank question:

- **Have a Thai bank?** → **Buy/Sell Crypto → P2P Trading → Sell → USDT → THB**, pick a
  merchant paying by **PromptPay** with a high completion rate and thousands of trades.
  Release the crypto **only after the baht actually lands** in your bank app — never on a
  screenshot.
- **No Thai bank?** → apply for the **Bybit Card** (Cards section; needs KYC), fund it from
  your USDT balance, and spend / withdraw baht at ATMs. This is your no-bank spending rail.
  (Cash P2P — meeting a merchant for physical baht — is the option for larger lumps.)

Full detail lives in your own guide: `content/off-ramp-thailand.md`.

## Part E — Turn on the affiliate (earn from Offrampt)

1. Open the **Referral** program (Profile menu → "Referral" / "Invite Friends").
2. Copy your **invite link** (it has your code in it).
3. Open **`affiliate_ids.local.py`**, uncomment the `bybit` and `bybit_card` lines, and
   paste your link into both. Save.
4. For higher commission, apply to the **Affiliate program** (Profile → "Affiliate" /
   `bybit.com/en-US/affiliates`) — it needs approval; the plain referral works immediately
   in the meantime.
5. Rebuild so the site uses your real links:

```bash
python3 make_cards.py && python3 build.py
```

(run from the repo root)

The build prints how many affiliate links are still placeholders — watch that number drop.

---

## Security checklist (do all five)

- [ ] Gmail (skunkhaus@) has its own 2FA — it's the master key now.
- [ ] Bybit 2FA is an **authenticator app**, not SMS. Backup code saved offline.
- [ ] KYC done with your passport.
- [ ] A **1 USDT test deposit** landed before any real payment.
- [ ] You keep only a **spending float** on Bybit — savings go to a self-custody / hardware
      wallet (Part 1 of `PAYMENTS.md`). Exchanges can freeze balances.

**Never** type your wallet seed phrase into Bybit or anywhere else — Bybit is custodial and
never needs it. Anyone asking for a seed phrase is stealing from you.

---

## When you're done, tell me

Paste nothing sensitive — just say "Bybit's live" and I'll:
- confirm the rebuild picked up your affiliate links, and
- move on to the **/consult/ page** (I'll need: price, what's included, crypto-only or add
  ko-fi).
