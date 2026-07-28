---
title: Get paid in crypto 101 — wallets, addresses, and networks
description: A plain-language starter for getting paid in crypto without losing it — wallets vs exchanges, addresses and networks, stablecoins vs volatile coins, and the wrong-network mistake that eats funds.
type: guide
updated: 2026-07-25
published: 2026-07-25
intro: If you're about to receive your first crypto payment, read this first. It's the fundamentals that stop you from losing money on day one — especially the address-and-network trap that started this whole site.
---

Getting paid in crypto is genuinely easy: someone sends, you receive, done. The money is
lost in the *details* — receiving on the wrong network, quoting the wrong address, or
holding a coin that drops 8% before you cash out. Here's the groundwork.

## Wallet vs exchange account — where your crypto lives

- **An exchange account** (Binance, Bybit, Kraken…) is like a bank: convenient, good for
  buying/selling, but the platform holds your keys. Great as a *cash-out* venue, not ideal
  as a *vault*.
- **A self-custody wallet** (a phone app, or a hardware wallet like %%AFF:ledger|Ledger%% or
  %%AFF:trezor|Trezor%%) means *you* hold the keys. More responsibility, more control.

A common setup: receive to your own wallet, move to an exchange only when you're ready to
off-ramp. "Not your keys, not your coins" is the old saying — take it as a nudge to not
leave everything sitting on a platform forever.

:::warn Never, ever share your seed phrase
Your **seed phrase** (12–24 words) *is* your money. No legitimate exchange, wallet,
support agent, or website will ever ask for it. Anyone who does is stealing from you.
Write it on paper, store it offline, and type it nowhere except your own wallet's recovery
screen.
:::

## Addresses and networks — the part that actually loses money

A crypto **address** is where funds go — a long string like `bc1q...` (Bitcoin) or
`0x1a2b...` (Ethereum/Base and other EVM chains). A **network** is the road the funds
travel on. The address format tells you which network it belongs to:

- `bc1...` or `1.../3...` → the **Bitcoin** network (native BTC).
- `0x...` → an **EVM** network — Ethereum, Base, Arbitrum, Polygon, BNB Chain, and more.
  Crucially, **the same `0x` address exists on all of them**, so the address alone doesn't
  tell you which EVM chain to use.

:::key The mistake this whole site was born from
Someone tried to pay in native **Bitcoin** to what was actually a **Base `0x` address** —
two different networks that don't speak to each other. Funds sent on the wrong network
usually **can't be recovered.** Before any transfer:

1. Confirm the **coin** (BTC? USDT? USDC?).
2. Confirm the **network** (Bitcoin? Ethereum? Base? Tron?).
3. Confirm the **address format matches that network.**
4. Send a **tiny test amount first**, wait for it to arrive, *then* send the rest.
:::

**Same-ticker, different-network** is the sneaky one. USDT and USDC exist on many networks
at once — USDC on Ethereum, USDC on Base, USDT on Tron, and so on. "Send me USDC" is not
enough; you need "USDC **on Base**" (or whichever). Sender and receiver must agree on the
network, not just the coin.

## Stablecoins vs volatile coins — what to be paid in

- **Stablecoins** (USDT, USDC) aim to hold ~1 US dollar. Best for getting *paid* and for
  *cashing out*, because the value won't swing between "received" and "spent."
- **Volatile coins** (BTC, ETH, …) can move a lot, fast. Hold them if you *want* that
  exposure — not by accident while you're trying to pay rent.

A practical rule: **accept payment in a stablecoin**, convert to a volatile asset later only
if you deliberately want to. It removes a whole category of "I lost 6% overnight" stress.

## Fees: gas and network costs

Moving crypto costs a small **network fee** ("gas"). It varies wildly by network — a
transfer on Ethereum mainnet can cost far more than the same transfer on Base, Tron, or the
Bitcoin Lightning network. If you're receiving stablecoins regularly, agreeing on a
**low-fee network** with whoever pays you saves real money over time. *Inference — relative
costs shift with network congestion; check before you assume.*

## A clean first-payment checklist

1. Set up a wallet (or exchange account) that supports the coin you'll be paid in.
2. Agree with the payer on **coin + network** — write it down, e.g. "USDC on Base."
3. Give them the matching **receive address**; have them send a **small test** first.
4. Confirm it arrived on a block explorer or in your wallet, then take the full payment.
5. When you're ready to spend, head to [[off-ramp-thailand|Off-ramp Thailand]] or grab a
   [[crypto-cards|crypto card]].

## FAQ

### What's the safest coin to get paid in?
For most people, a major stablecoin (USDC or USDT) on a low-fee network. It holds a steady
dollar value so your pay doesn't shrink before you cash out, and it's the easiest thing to
off-ramp.

### What happens if I send crypto on the wrong network?
Usually it's lost with no way to reverse it — there's no bank to call. That's why you always
match coin, network, and address format, and send a small test amount first. See
[[scams|Stay safe]].

### Do I need a hardware wallet?
Not to get started, but it's the safest place to hold anything you're not about to spend. A
device like a hardware wallet keeps your keys offline, away from phone malware and phishing
sites. Keep spending money on a card or exchange, savings on the device.

### What's a seed phrase and who can I give it to?
It's the 12–24 word master key to your wallet — effectively your entire balance. The answer
to "who can I give it to" is **nobody, ever.** Every request for it is a scam.

### Is USDC the same on every network?
No. USDC exists separately on Ethereum, Base, and other chains. The coin is "the same," but
you must send and receive it **on the same network** — agree on the network explicitly, not
just the coin.
