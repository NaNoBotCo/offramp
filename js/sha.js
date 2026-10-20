/* sha.js — SHA-256 and Keccak-256, synchronous, for the checker and the demos. MIT. */
(function (G) {
  var K = [0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2];

  function sha256(msg) {
    var l = msg.length, bl = Math.ceil((l + 9) / 64) * 64, p = new Uint8Array(bl);
    p.set(msg); p[l] = 0x80;
    var bits = l * 8;
    p[bl - 4] = (bits >>> 24) & 255; p[bl - 3] = (bits >>> 16) & 255; p[bl - 2] = (bits >>> 8) & 255; p[bl - 1] = bits & 255;
    p[bl - 5] = Math.floor(bits / 4294967296) & 255;
    var H = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19];
    var W = new Array(64);
    for (var o = 0; o < bl; o += 64) {
      for (var i = 0; i < 16; i++) W[i] = (p[o + 4 * i] << 24) | (p[o + 4 * i + 1] << 16) | (p[o + 4 * i + 2] << 8) | p[o + 4 * i + 3];
      for (i = 16; i < 64; i++) {
        var a = W[i - 15], b = W[i - 2];
        var s0 = ((a >>> 7) | (a << 25)) ^ ((a >>> 18) | (a << 14)) ^ (a >>> 3);
        var s1 = ((b >>> 17) | (b << 15)) ^ ((b >>> 19) | (b << 13)) ^ (b >>> 10);
        W[i] = (W[i - 16] + s0 + W[i - 7] + s1) | 0;
      }
      var A = H[0], B = H[1], C = H[2], D = H[3], E = H[4], F = H[5], Gg = H[6], Hh = H[7];
      for (i = 0; i < 64; i++) {
        var S1 = ((E >>> 6) | (E << 26)) ^ ((E >>> 11) | (E << 21)) ^ ((E >>> 25) | (E << 7));
        var ch = (E & F) ^ (~E & Gg);
        var t1 = (Hh + S1 + ch + K[i] + W[i]) | 0;
        var S0 = ((A >>> 2) | (A << 30)) ^ ((A >>> 13) | (A << 19)) ^ ((A >>> 22) | (A << 10));
        var mj = (A & B) ^ (A & C) ^ (B & C);
        var t2 = (S0 + mj) | 0;
        Hh = Gg; Gg = F; F = E; E = (D + t1) | 0; D = C; C = B; B = A; A = (t1 + t2) | 0;
      }
      H[0] = (H[0] + A) | 0; H[1] = (H[1] + B) | 0; H[2] = (H[2] + C) | 0; H[3] = (H[3] + D) | 0;
      H[4] = (H[4] + E) | 0; H[5] = (H[5] + F) | 0; H[6] = (H[6] + Gg) | 0; H[7] = (H[7] + Hh) | 0;
    }
    var out = new Uint8Array(32);
    for (i = 0; i < 8; i++) { out[4 * i] = H[i] >>> 24; out[4 * i + 1] = (H[i] >>> 16) & 255; out[4 * i + 2] = (H[i] >>> 8) & 255; out[4 * i + 3] = H[i] & 255; }
    return out;
  }

  var M64 = (1n << 64n) - 1n;
  var RC = [0x1n, 0x8082n, 0x800000000000808An, 0x8000000080008000n, 0x808Bn, 0x80000001n, 0x8000000080008081n,
    0x8000000000008009n, 0x8An, 0x88n, 0x80008009n, 0x8000000An, 0x8000808Bn, 0x800000000000008Bn, 0x8000000000008089n,
    0x8000000000008003n, 0x8000000000008002n, 0x8000000000000080n, 0x800An, 0x800000008000000An, 0x8000000080008081n,
    0x8000000000008080n, 0x80000001n, 0x8000000080008008n];
  var ROT = [[0, 36, 3, 41, 18], [1, 44, 10, 45, 2], [62, 6, 43, 15, 61], [28, 55, 25, 21, 56], [27, 20, 39, 8, 14]];
  function rotl(v, n) { if (!n) return v; var b = BigInt(n); return ((v << b) | (v >> (64n - b))) & M64; }
  function kf(A) {
    for (var r = 0; r < 24; r++) {
      var C = [], D = [], x, y;
      for (x = 0; x < 5; x++) C[x] = A[x] ^ A[x + 5] ^ A[x + 10] ^ A[x + 15] ^ A[x + 20];
      for (x = 0; x < 5; x++) D[x] = C[(x + 4) % 5] ^ rotl(C[(x + 1) % 5], 1);
      for (var i = 0; i < 25; i++) A[i] ^= D[i % 5];
      var B = new Array(25);
      for (x = 0; x < 5; x++) for (y = 0; y < 5; y++) B[y + 5 * ((2 * x + 3 * y) % 5)] = rotl(A[x + 5 * y], ROT[x][y]);
      for (x = 0; x < 5; x++) for (y = 0; y < 5; y++) A[x + 5 * y] = B[x + 5 * y] ^ ((~B[(x + 1) % 5 + 5 * y] & M64) & B[(x + 2) % 5 + 5 * y]);
      A[0] ^= RC[r];
    }
  }
  function keccak256(bytes) {
    var rate = 136, A = [], i;
    for (i = 0; i < 25; i++) A[i] = 0n;
    var p = new Uint8Array(Math.ceil((bytes.length + 1) / rate) * rate);
    p.set(bytes); p[bytes.length] ^= 0x01; p[p.length - 1] ^= 0x80;
    for (var o = 0; o < p.length; o += rate) {
      for (i = 0; i < rate / 8; i++) {
        var v = 0n;
        for (var b = 7; b >= 0; b--) v = (v << 8n) | BigInt(p[o + i * 8 + b]);
        A[i] ^= v;
      }
      kf(A);
    }
    var out = new Uint8Array(32);
    for (i = 0; i < 4; i++) { var w = A[i]; for (var k = 0; k < 8; k++) { out[i * 8 + k] = Number(w & 0xffn); w >>= 8n; } }
    return out;
  }
  function hex(b) { return Array.prototype.map.call(b, function (x) { return (x < 16 ? "0" : "") + x.toString(16); }).join(""); }
  function utf8(s) { return new TextEncoder().encode(s); }
  G.OFR = G.OFR || {};
  G.OFR.sha256 = sha256; G.OFR.keccak256 = keccak256; G.OFR.hex = hex; G.OFR.utf8 = utf8;
})(typeof window !== "undefined" ? window : globalThis);
