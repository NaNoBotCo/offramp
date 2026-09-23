/* how.js — the hash and the mining models on How. MIT. */
(function () {
  var O = window.OFR, t = O.t || function (e) { return e; };
  var hin = document.getElementById("hin"), hout = document.getElementById("hout"), cv = document.getElementById("hbits"), hf = document.getElementById("hflip");
  var prev = null;
  function bits(b) { var o = []; for (var i = 0; i < b.length; i++) for (var k = 7; k >= 0; k--) o.push((b[i] >> k) & 1); return o; }
  function draw() {
    var h = O.sha256(O.utf8(hin.value)), bs = bits(h);
    hout.textContent = O.hex(h);
    var c = cv.getContext("2d"), w = cv.width / 64, hh = cv.height / 4, flips = 0;
    c.fillStyle = "#05070c"; c.fillRect(0, 0, cv.width, cv.height);
    for (var i = 0; i < 256; i++) {
      var x = (i % 64) * w, y = Math.floor(i / 64) * hh, f = prev && prev[i] !== bs[i];
      if (f) flips++;
      c.fillStyle = f ? (bs[i] ? "#ffb13b" : "#ff5a5f") : (bs[i] ? "#2fd27f" : "#121925");
      c.fillRect(x + 1, y + 1, w - 2, hh - 2);
    }
    hf.textContent = prev ? t(flips + " of 256 bits changed from the last input (amber and red). Half is 128.", flips + " จาก 256 บิตเปลี่ยนไปจากข้อความก่อนหน้า (สีเหลืองอำพันและสีแดง) ครึ่งหนึ่งคือ 128") : t("256 bits: green is 1, dark is 0. Change the text.", "256 บิต: สีเขียวคือ 1 สีเข้มคือ 0 ลองเปลี่ยนข้อความดู");
    prev = bs;
  }
  if (hin) { hin.addEventListener("input", draw); draw(); }

  var btn = document.getElementById("mine"), mz = document.getElementById("mz"), mo = document.getElementById("mout");
  if (!btn) return;
  var prevHash = "000000000019d6689c085ae165831e934ff763ae46a2a6c172b3f1b60a8ce26f", busy = false;
  btn.addEventListener("click", function () {
    if (busy) return;
    busy = true; btn.disabled = true;
    var z = +mz.value, target = "0".repeat(z), nonce = 0, t0 = performance.now();
    function step() {
      var end = performance.now() + 30;
      while (performance.now() < end) {
        var h = O.hex(O.sha256(O.utf8("offrampt|" + prevHash + "|" + nonce)));
        if (h.slice(0, z) === target) {
          var ms = performance.now() - t0;
          mo.textContent = t("Found after " + (nonce + 1).toLocaleString() + " tries in " + (ms / 1000).toFixed(2) + " s.", "เจอหลังลอง " + (nonce + 1).toLocaleString() + " ครั้ง ใน " + (ms / 1000).toFixed(2) + " วินาที") + "\nnonce " + nonce + "\nhash  " + h +
            "\n\n" + t("Average for " + z + " zero" + (z > 1 ? "s" : "") + ": " + Math.pow(16, z).toLocaleString() + " tries.", "ค่าเฉลี่ยสำหรับศูนย์ " + z + " ตัว: " + Math.pow(16, z).toLocaleString() + " ครั้ง") +
            (btn.dataset.hr ? t(" The bitcoin network was making " + btn.dataset.hr + " quintillion tries a second when this page was built.", " ตอนสร้างหน้านี้ เครือข่ายบิตคอยน์ลอง " + btn.dataset.hr + " ล้านล้านล้านครั้งต่อวินาที") : "");
          prevHash = h; busy = false; btn.disabled = false; return;
        }
        nonce++;
      }
      mo.textContent = t("Trying… ", "กำลังลอง… ") + nonce.toLocaleString() + t(" hashes", " แฮช");
      setTimeout(step, 0);
    }
    step();
  });
})();
