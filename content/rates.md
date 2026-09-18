---
title: Live rates — crypto to baht, right now
description: What USDT and BTC actually fetch in Thai baht today — licensed Thai exchange bid, global fair value, and the Bank of Thailand reference, side by side with timestamps.
type: guide
updated: 2026-08-12
---

# Live rates — crypto → baht, right now

Three numbers tell you whether an off-ramp quote is fair, and this page holds all three side by side:

- **The street bid** — what Bitkub (a Thai-SEC-licensed exchange) is paying for your USDT or BTC in baht, this minute.
- **The global fair value** — the world mid-price converted at the official rate. This is the number the street bid should hover near.
- **The official reference** — the Bank of Thailand's weighted-average interbank USD/THB. Published on banking days; the date shown is the date it carries.

The gap between street and fair is the **premium**. Small and steady is normal. A quote from anyone — an exchange, a P2P counterparty, a friend of a friend — that sits far below the street bid is costing you money, and now you can see it.

<!-- RATES_BOARD -->

## How to read this before you off-ramp

1. Check the **premium**. Near zero means the Thai street price is tracking the world price — no drama today.
2. Use the **calculator** for a plain estimate of baht out. It uses the live street bid and nothing else — real proceeds also depend on the venue's fee tier and your withdrawal method.
3. Glance at the **timestamps**. Every number carries its own fetched-time. A rate without a time is a rumor.

## Sources, plainly

The board reads one small JSON feed, refreshed about every 15 minutes: Bitkub's public market API (licensed Thai street), CoinGecko (global mid), and the Bank of Thailand's official reference series. The feed is public — agents and spreadsheets welcome: `https://offrampt-rates.nanobotco.workers.dev/`

*Reference information, not financial, tax, or investment advice. Rates move continuously; this page shows you the market, it does not tell you what to do with it.*
