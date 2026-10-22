/* addr.js — read an address: its format, its checksum, and the networks that format belongs to. MIT. */
(function (G) {
  var B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";
  var XRP = "rpshnaf39wBUDNEGHJKLM4PQRST7VWXYZ2bcdeCg65jkm8oFqi1tuvAxyz";
  var EVM = "Ethereum, BNB Smart Chain, Base, Arbitrum, Optimism, Polygon, Avalanche C-Chain, Linea, Scroll, zkSync";

  function b58(s, alpha) {
    var n = 0n;
    for (var i = 0; i < s.length; i++) {
      var d = alpha.indexOf(s[i]);
      if (d < 0) return null;
      n = n * 58n + BigInt(d);
    }
    var bytes = [];
    while (n > 0n) { bytes.unshift(Number(n & 255n)); n >>= 8n; }
    for (i = 0; i < s.length && s[i] === alpha[0]; i++) bytes.unshift(0);
    return new Uint8Array(bytes);
  }
  function check58(s, alpha) {
    var b = b58(s, alpha || B58);
    if (!b || b.length < 5) return null;
    var body = b.slice(0, -4), ck = b.slice(-4), h = G.OFR.sha256(G.OFR.sha256(body));
    for (var i = 0; i < 4; i++) if (h[i] !== ck[i]) return { bad: true, bytes: b };
    return { version: body[0], payload: body.slice(1), bytes: b };
  }

  var CH = "qpzry9x8gf2tvdw0s3jn54khce6mua7l";
  function polymod(v) {
    var g = [0x3b6a57b2, 0x26508e6d, 0x1ea119fa, 0x3d4233dd, 0x2a1462b3], c = 1;
    for (var i = 0; i < v.length; i++) {
      var t = c >>> 25; c = ((c & 0x1ffffff) << 5) ^ v[i];
      for (var j = 0; j < 5; j++) if ((t >>> j) & 1) c ^= g[j];
    }
    return c >>> 0;
  }
  function bech(s) {
    if (s !== s.toLowerCase() && s !== s.toUpperCase()) return null;
    s = s.toLowerCase();
    var p = s.lastIndexOf("1");
    if (p < 1 || p + 7 > s.length) return null;
    var hrp = s.slice(0, p), data = [];
    for (var i = p + 1; i < s.length; i++) { var d = CH.indexOf(s[i]); if (d < 0) return null; data.push(d); }
    var ex = [];
    for (i = 0; i < hrp.length; i++) ex.push(hrp.charCodeAt(i) >> 5);
    ex.push(0);
    for (i = 0; i < hrp.length; i++) ex.push(hrp.charCodeAt(i) & 31);
    var pm = polymod(ex.concat(data));
    var kind = pm === 1 ? "bech32" : pm === 0x2bc830a3 ? "bech32m" : null;
    return { hrp: hrp, data: data.slice(0, -6), kind: kind };
  }
  function prog(data) {  // 5-bit groups after the version → bytes
    var acc = 0, bits = 0, out = [];
    for (var i = 1; i < data.length; i++) { acc = (acc << 5) | data[i]; bits += 5; while (bits >= 8) { bits -= 8; out.push((acc >> bits) & 255); } }
    return out;
  }
  function crc16(b) {
    var c = 0;
    for (var i = 0; i < b.length; i++) { c ^= b[i] << 8; for (var k = 0; k < 8; k++) c = (c & 0x8000) ? ((c << 1) ^ 0x1021) & 0xffff : (c << 1) & 0xffff; }
    return c;
  }
  function b64(s) {
    try { var t = atob(s.replace(/-/g, "+").replace(/_/g, "/")); var o = new Uint8Array(t.length); for (var i = 0; i < t.length; i++) o[i] = t.charCodeAt(i); return o; } catch (e) { return null; }
  }

  function r(level, title, lines) { return { level: level, title: title, lines: lines || [] }; }
  function t(en, th) { return (G.OFR && G.OFR.t) ? G.OFR.t(en, th) : en; }

  function read(raw) {
    var s = (raw || "").trim();
    if (!s) return null;
    var words = s.toLowerCase().split(/\s+/);
    if (words.length >= 12 && words.length <= 24 && words.every(function (w) { return /^[a-z]{3,8}$/.test(w); }))
      return r("red", t("This looks like a seed phrase", "นี่ดูเหมือน seed phrase (ชุดคำกู้คืน)"), [t("Twelve to twenty-four plain words are the master key to a wallet. Anyone who sees them can take everything in it.", "คำธรรมดา 12 ถึง 24 คำคือกุญแจหลักของกระเป๋า ใครเห็นคำเหล่านี้ก็เอาทุกอย่างในกระเป๋าไปได้"),
        t("Clear this box. If the words were ever typed into a website, a chat or a form, move the coins to a new wallet with new words.", "ลบข้อความในช่องนี้ ถ้าเคยพิมพ์คำเหล่านี้ลงในเว็บ แชต หรือแบบฟอร์มใด ให้ย้ายเหรียญไปกระเป๋าใหม่ที่มีชุดคำใหม่")]);
    if (/^(0x)?[0-9a-fA-F]{64}$/.test(s))
      return r("red", t("This looks like a private key", "นี่ดูเหมือนกุญแจส่วนตัว (private key)"), [t("64 hex characters is the length of a private key (or a transaction hash). A private key controls the coins; it goes into a wallet, never to a person.", "อักขระฐานสิบหก 64 ตัวคือความยาวของกุญแจส่วนตัว (หรือแฮชธุรกรรม) กุญแจส่วนตัวควบคุมเหรียญ ใช้ใส่ในกระเป๋าเท่านั้น ห้ามให้คนอื่น")]);
    if (/^[5KL][1-9A-HJ-NP-Za-km-z]{50,51}$/.test(s)) {
      var w = check58(s);
      if (w && !w.bad && w.version === 0x80) return r("red", t("This is a bitcoin private key (WIF)", "นี่คือกุญแจส่วนตัวบิตคอยน์ (WIF)"), [t("Wallet Import Format. Whoever holds this string holds the coins.", "รูปแบบ Wallet Import Format ใครถือข้อความนี้ คนนั้นถือเหรียญ")]);
    }
    // EVM
    if (/^0x[0-9a-fA-F]{40}$/.test(s)) {
      var body = s.slice(2), lower = body.toLowerCase(), mixed = body !== lower && body !== body.toUpperCase();
      var lines = [t("Networks that use this format: ", "เครือข่ายที่ใช้รูปแบบนี้: ") + EVM + ".", t("The same address exists on all of them. The sender's network menu decides where the coins go; the receiving exchange or wallet has to support that network.", "ที่อยู่เดียวกันมีอยู่บนทุกเครือข่ายเหล่านี้ เมนูเครือข่ายของผู้ส่งเป็นตัวกำหนดว่าเหรียญจะไปที่ไหน ศูนย์ซื้อขายหรือกระเป๋าปลายทางต้องรองรับเครือข่ายนั้น")];
      if (mixed) {
        var h = G.OFR.hex(G.OFR.keccak256(G.OFR.utf8(lower))), ok = true;
        for (var i = 0; i < 40; i++) {
          var c = body[i];
          if (/[a-f]/i.test(c) && ((parseInt(h[i], 16) >= 8) !== (c === c.toUpperCase()))) { ok = false; break; }
        }
        if (!ok) return r("red", t("EVM address with a broken checksum", "ที่อยู่ EVM ที่ checksum ไม่ถูกต้อง"), [t("The mixed capitals encode a checksum (EIP-55), and it does not match. A character is wrong. Copy the address again from its source.", "ตัวพิมพ์ใหญ่เล็กที่ผสมกันคือ checksum (EIP-55) และไม่ตรงกัน มีตัวอักษรผิด คัดลอกที่อยู่ใหม่จากต้นทาง")]);
        lines.unshift(t("Checksum (EIP-55 mixed case): valid.", "Checksum (EIP-55 ตัวพิมพ์ผสม): ถูกต้อง"));
      } else lines.unshift(t("All one case, so it carries no checksum: a typo would not be caught. Compare the first and last six characters with the source.", "ตัวพิมพ์แบบเดียวทั้งหมด จึงไม่มี checksum พิมพ์ผิดจะจับไม่ได้ เทียบหกตัวแรกและหกตัวท้ายกับต้นทาง"));
      return r("go", t("EVM address (0x…)", "ที่อยู่ EVM (0x…)"), lines);
    }
    if (/^[a-z0-9-]+\.eth$/i.test(s)) return r("amber", t("ENS name", "ชื่อ ENS"), [t("A name that resolves to an Ethereum address. A wallet looks it up; an exchange deposit screen usually wants the 0x address itself.", "ชื่อที่ชี้ไปยังที่อยู่ Ethereum กระเป๋าจะค้นหาให้ แต่หน้าฝากของศูนย์ซื้อขายมักต้องการที่อยู่ 0x โดยตรง")]);
    // bech32 family
    var lb = s.toLowerCase();
    if (/^(lnbc|lntb|lnbcrt)/.test(lb)) {
      var ln = bech(s);
      if (ln && ln.kind === "bech32") return r("go", t("Lightning invoice", "ใบแจ้งหนี้ Lightning"), [t("Checksum valid. A Lightning invoice is a request for one payment, usually of a set amount, and it expires.", "Checksum ถูกต้อง ใบแจ้งหนี้ Lightning คือคำขอชำระเงินหนึ่งครั้ง มักระบุจำนวนไว้ และหมดอายุได้"), t("It pays over the Lightning network, not on-chain bitcoin: the sending wallet has to speak Lightning.", "จ่ายผ่านเครือข่าย Lightning ไม่ใช่บิตคอยน์บนเชน กระเป๋าผู้ส่งต้องรองรับ Lightning")]);
      return r("red", t("Lightning invoice with a broken checksum", "ใบแจ้งหนี้ Lightning ที่ checksum ไม่ถูกต้อง"), [t("Copy it again, whole. Invoices are long and a missing character breaks them.", "คัดลอกใหม่ทั้งหมด ใบแจ้งหนี้ยาว ขาดตัวเดียวก็ใช้ไม่ได้")]);
    }
    if (/^(bc1|tb1|ltc1|bcrt1)/.test(lb)) {
      var b = bech(s);
      if (!b || !b.kind) return r("red", t("Bech32 address with a broken checksum", "ที่อยู่ Bech32 ที่ checksum ไม่ถูกต้อง"), [t("Starts like a native SegWit address but the checksum fails. One character is wrong or missing.", "ขึ้นต้นเหมือนที่อยู่ SegWit แต่ checksum ไม่ผ่าน มีตัวอักษรผิดหรือขาดไปหนึ่งตัว")]);
      var ver = b.data[0], pr = prog(b.data);
      var net = { bc: "Bitcoin", tb: t("Bitcoin testnet (no value)", "Bitcoin testnet (ไม่มีมูลค่า)"), ltc: "Litecoin", bcrt: "Bitcoin regtest" }[b.hrp] || b.hrp;
      var wantKind = ver === 0 ? "bech32" : "bech32m";
      if (b.kind !== wantKind) return r("red", t("Checksum type does not match the version", "ชนิด checksum ไม่ตรงกับเวอร์ชัน"), [t("Version " + ver + " addresses use " + wantKind + " (BIP 173 / BIP 350). This one uses " + b.kind + ".", "ที่อยู่เวอร์ชัน " + ver + " ใช้ " + wantKind + " (BIP 173 / BIP 350) แต่ที่อยู่นี้ใช้ " + b.kind)]);
      var type = ver === 0 ? (pr.length === 20 ? t("P2WPKH (bc1q…, a single key)", "P2WPKH (bc1q… กุญแจเดียว)") : pr.length === 32 ? t("P2WSH (a script)", "P2WSH (สคริปต์)") : t("version 0, unusual length", "เวอร์ชัน 0 ความยาวผิดปกติ")) : ver === 1 && pr.length === 32 ? "Taproot (bc1p…)" : "witness version " + ver;
      return r(b.hrp === "tb" || b.hrp === "bcrt" ? "amber" : "go", net + t(" address, ", " ที่อยู่ ") + type, [t("Checksum (" + b.kind + "): valid.", "Checksum (" + b.kind + "): ถูกต้อง"), b.hrp === "bc" ? t("Native bitcoin on the Bitcoin network. Not an address for BTC on BNB Chain or any wrapped bitcoin.", "บิตคอยน์ดั้งเดิมบนเครือข่าย Bitcoin ไม่ใช่ที่อยู่สำหรับ BTC บน BNB Chain หรือบิตคอยน์แบบ wrapped") : ""]);
    }
    // TON
    if (/^[EUk0][Qf][A-Za-z0-9_+\/-]{46}$/.test(s)) {
      var tb = b64(s);
      if (tb && tb.length === 36) {
        var ok2 = crc16(tb.slice(0, 34)) === ((tb[34] << 8) | tb[35]);
        if (!ok2) return r("red", t("TON address with a broken checksum", "ที่อยู่ TON ที่ checksum ไม่ถูกต้อง"), [t("The last two bytes are a CRC and they do not match. Copy it again.", "สองไบต์สุดท้ายคือ CRC และไม่ตรงกัน คัดลอกใหม่")]);
        var flag = tb[0];
        return r("go", t("TON address", "ที่อยู่ TON"), [t("Checksum (CRC16): valid. ", "Checksum (CRC16): ถูกต้อง ") + ((flag & 0x40) ? "Non-bounceable (UQ…)" : "Bounceable (EQ…)") + ((flag & 0x80) ? ", testnet." : "."),
          t("Exchanges often need a memo (comment) with a TON deposit. Without it the coins reach the exchange but not your account.", "ศูนย์ซื้อขายมักต้องการ memo (คอมเมนต์) เมื่อฝาก TON ถ้าไม่ใส่ เหรียญจะถึงศูนย์ซื้อขายแต่ไม่เข้าบัญชีของคุณ")]);
      }
    }
    // base58check family
    if (/^[1-9A-HJ-NP-Za-km-z]{25,44}$/.test(s)) {
      var x = check58(s);
      if (x && !x.bad && x.bytes.length === 25) {
        var V = { 0x00: [t("Bitcoin, legacy (1…)", "Bitcoin แบบดั้งเดิม (1…)"), "go"], 0x05: [t("Bitcoin, script (3…)", "Bitcoin แบบสคริปต์ (3…)"), "go"], 0x41: ["Tron (T…)", "go"], 0x30: ["Litecoin (L…)", "go"], 0x32: ["Litecoin script (M…)", "go"],
          0x1e: ["Dogecoin (D…)", "go"], 0x16: ["Dogecoin script (9… / A…)", "go"], 0x6f: [t("Bitcoin testnet (no value)", "Bitcoin testnet (ไม่มีมูลค่า)"), "amber"], 0xc4: [t("Bitcoin testnet script (no value)", "Bitcoin testnet สคริปต์ (ไม่มีมูลค่า)"), "amber"] }[x.version];
        if (V) {
          var extra = x.version === 0x41 ? [t("USDT on Tron is 'TRC-20' on exchange menus. Sending from Tron needs TRX (or energy) for the fee; USDT alone cannot pay it.", "USDT บน Tron คือ 'TRC-20' ในเมนูของศูนย์ซื้อขาย การส่งจาก Tron ต้องมี TRX (หรือ energy) จ่ายค่าธรรมเนียม USDT อย่างเดียวจ่ายไม่ได้")] :
            x.version === 0x00 || x.version === 0x05 ? [t("Native bitcoin on the Bitcoin network. The format is older; fees are a little higher than bc1 addresses.", "บิตคอยน์ดั้งเดิมบนเครือข่าย Bitcoin รูปแบบเก่ากว่า ค่าธรรมเนียมสูงกว่าที่อยู่ bc1 เล็กน้อย")] : [];
          return r(V[1], V[0], [t("Checksum (base58check): valid.", "Checksum (base58check): ถูกต้อง")].concat(extra));
        }
      }
      if (/^r/.test(s)) {
        var xr = check58(s, XRP);
        if (xr && !xr.bad && xr.bytes.length === 25 && xr.version === 0)
          return r("go", t("XRP Ledger address (r…)", "ที่อยู่ XRP Ledger (r…)"), [t("Checksum: valid.", "Checksum: ถูกต้อง"), t("Exchange deposits on XRP need a destination tag, a number the exchange gives you. Without it the deposit lands in the exchange's shared account.", "การฝาก XRP เข้าศูนย์ซื้อขายต้องใส่ destination tag ซึ่งเป็นตัวเลขที่ศูนย์ซื้อขายให้มา ถ้าไม่ใส่ เงินจะเข้าบัญชีรวมของศูนย์ซื้อขาย")]);
      }
      if (x && x.bad && x.bytes.length === 25 && /^[13T]/.test(s)) return r("red", t("Base58 address with a broken checksum", "ที่อยู่ Base58 ที่ checksum ไม่ถูกต้อง"), [t("It looks like a " + (s[0] === "T" ? "Tron" : "bitcoin") + " address, but the last four bytes do not match. A character is wrong.", "ดูเหมือนที่อยู่ " + (s[0] === "T" ? "Tron" : "บิตคอยน์") + " แต่สี่ไบต์สุดท้ายไม่ตรง มีตัวอักษรผิด")]);
      var sol = b58(s, B58);
      if (sol && sol.length === 32) return r("amber", t("Looks like a Solana address", "ดูเหมือนที่อยู่ Solana"), [t("Base58, 32 bytes: the Solana format. Solana addresses carry no checksum, so a typo can still read as valid. Compare the start and end with the source.", "Base58 ขนาด 32 ไบต์: รูปแบบของ Solana ที่อยู่ Solana ไม่มี checksum พิมพ์ผิดก็ยังดูถูกต้อง เทียบต้นและท้ายกับต้นทาง")]);
    }
    if (/^[a-z0-9._-]+@[a-z0-9.-]+\.[a-z]{2,}$/i.test(s))
      return r("amber", t("A Lightning address, or an email", "Lightning address หรืออีเมล"), [t("name@domain: a Lightning wallet looks this up over the web and fetches an invoice. It only works if the domain runs a Lightning service.", "ชื่อ@โดเมน: กระเป๋า Lightning จะค้นหาผ่านเว็บแล้วดึงใบแจ้งหนี้มา ใช้ได้เฉพาะเมื่อโดเมนนั้นให้บริการ Lightning")]);
    return r("red", t("Not a format this checker knows", "ตัวตรวจไม่รู้จักรูปแบบนี้"), [t("A missing character, a space or a line break in the middle puts an address outside every known format.", "ตัวอักษรที่ขาดไป ช่องว่าง หรือการขึ้นบรรทัดใหม่ตรงกลาง ทำให้ที่อยู่ไม่ตรงกับรูปแบบใดเลย")]);
  }

  G.OFR = G.OFR || {};
  G.OFR.readAddress = read;

  if (typeof document === "undefined") return;
  var box = document.getElementById("addr"), out = document.getElementById("addrout");
  if (!box || !out) return;
  function esc(t) { return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function show() {
    var v = read(box.value);
    if (!v) { out.innerHTML = t("Waiting for an address.", "รอที่อยู่"); return; }
    out.innerHTML = '<span class="pill ' + v.level + '">' + (v.level === "go" ? t("format ok", "รูปแบบถูกต้อง") : v.level === "amber" ? t("check", "ตรวจอีกครั้ง") : t("stop", "หยุด")) + "</span> <b>" + esc(v.title) + "</b>" +
      v.lines.filter(Boolean).map(function (l) { return "<br>" + esc(l); }).join("");
  }
  box.addEventListener("input", show);
  show();
})(typeof window !== "undefined" ? window : globalThis);
