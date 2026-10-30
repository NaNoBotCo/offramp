# Offrampt intel — the brief

For the session or task that writes a note. Read ~/.claude/STYLE.md first; it governs every word here.

## What a note is

One finding about crypto in Thailand, dated, with its sources, in English and Thai. It says what happened or what the data shows, then reads the trend: its **shape** (rising, falling, flat, past its peak, past its low, sudden drop, sudden jump, slow then sudden, step by step) and its **speed** (hours, days, weeks, months, years, decades). Speculating on where the shape goes, and how fast, is welcome when the note says what the guess rests on.

The lens is Nan's, in her words of 2026-10-30: "crypto is not actually crypto. Why? Because everything leaks and computers are solving hard math problems faster than people realize." The site takes the long-haul view: crypto as a tool, because banking in Thailand is hard. Hype and doom both fail the lens; a note shows the numbers and the shape and leaves the reader to act.

Readers: Thai holders from Bangkok to small towns (some living off crypto), foreigners with or without a Thai bank account, workers from Myanmar, Laos and Cambodia sending money home, and people who have never held a coin. Most read English as a second language. Plain words; a technical term gets a clause defining it at first use.

## Kinds

hack · long (the long view) · market · rule · bank · scam. Rotate: the kind used least in the last five notes goes first when two findings are equal.

## Rules for the words

- Facts, dates, numbers, sources. No warnings, cautions, safety notes, advice or imperatives to the reader ("check", "make sure", "avoid", "never", "you should"). Nan, 2026-10-04: "I mind my business."
- No promises, no "we never / we always", nothing declared on Nan's behalf. Her quoted words stay hers.
- A number is as the source gives it, with its date. Two series that count differently are named as different.
- A finding already in a note needs something new: a later date, a turn in the shape, a new number.
- Thai is written, not translated word for word: natural Thai a reader in Chiang Mai or Khon Kaen reads easily. Names of firms and coins stay in Latin letters.
- No down arrows anywhere (↓ ↘ ↙ ⬇).

## Sources

Primary first: regulators (sec.or.th, bot.or.th), company posts, papers, court and police figures, then reputable outlets (Thai and English). Open every page you cite and read it; a search snippet is not a source. Each source: title as the page gives it, url, publisher, date.

## Links

Each note links where a reader goes next: an Offrampt page (ramp/, rules/, cards/, scams/, networks/, markets/, tools/, how/, history/, words/, paper/, frozen/, intel/) and, where it fits the finding, a page of Hongdam (hongdam.net, its services and Studio), Chiang Mai Visa Desk (chiangmaivisadesk.com) or Mot Dang (motdang.net, sites.motdang.net), or Nan's explainers on nanobotco.github.io (quantum-computing, factoring). A link names the place: "Bank account opened with you, Hongdam".

## The file

`data/intel/notes/<YYYY-MM-DD>-<slug>.json`, the slug a few words of the title in lowercase with hyphens. Fields:

| field | what |
|---|---|
| id | the file name without .json |
| date | YYYY-MM-DD, Bangkok |
| order | a number; a higher one sorts first among notes of the same date |
| kind | one of the kinds above |
| title_en, title_th | a finding, not a topic: "Scam losses in Thailand: from 117 million baht a day to about 50 million" |
| dek_en, dek_th | one or two sentences under the title |
| body_en, body_th | 2 to 5 paragraphs each, the same count in both |
| quote_en, quote_th, quote_by_en, quote_by_th | optional, a quoted person's own words |
| shape, speed | from the lists above |
| read_en, read_th | the read of the shape and speed, and the guess with what it rests on |
| signal | optional: btc, usdt, stable, hash or rules, to draw the computed trend's own line |
| lead_until | optional YYYY-MM-DD: the home page's top strip shows this note until then |
| strip_en, strip_th | optional: the top strip's words, when the title alone does not say what the linked page offers |
| sources | list of {title, url, publisher, date}, two or more |
| links | list of {href, en, th} for an Offrampt path, or {href_en, href_th, en, th} for another site; "lead": true on the link the top strip opens |

`python3 tools/intel_check.py <file>` checks a note. `tools/intel_publish.sh <file>` checks it, builds, runs every gate, deploys offrampt.net and commits.
