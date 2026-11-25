#!/usr/bin/env python3
"""Lock Page: wrap an HTML page in a password screen (AES-256-GCM, PBKDF2-SHA256).

Usage: python3 -I lock_page.py INNER_HTML LOGO_DATAURI_TXT PASSWORD OUT_HTML
The page is decrypted in the visitor's browser; without the password it is unreadable.
"""
import base64, json, os, sys
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

inner_path, logo_path, password, out = sys.argv[1:5]
inner = open(inner_path, encoding='utf-8').read().encode('utf-8')
logo = open(logo_path, encoding='utf-8').read().strip()
ITER = 310000
salt, iv = os.urandom(16), os.urandom(12)
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(password.encode('utf-8'))
ct = AESGCM(key).encrypt(iv, inner, None)
blob = json.dumps({'s': base64.b64encode(salt).decode(), 'i': base64.b64encode(iv).decode(), 'c': base64.b64encode(ct).decode(), 'n': ITER})
page = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>Cultiva 2026 EOP</title>
<style>
:root { color-scheme: dark; --fg: #ECEFE7; --bg: #121510; --panel: #1C211A; --line: #3A4236; --blue: #3FA9DE; --green: #7BA93E; --bad: #E07A76; }
.box img { background: #FFFFFF; padding: 4px 10px; border-radius: 6px; }
html, body { margin: 0; background: var(--bg); color: var(--fg); font-family: Arial, Helvetica, sans-serif; }
.gate { min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 16px; box-sizing: border-box; }
.box { width: 100%; max-width: 380px; background: var(--panel); border: 1px solid var(--line); border-top: 5px solid var(--blue); border-radius: 8px; padding: 28px 24px; box-sizing: border-box; }
.box img { height: 44px; display: block; margin-bottom: 14px; }
.box h1 { font-family: 'Arial Narrow', Arial, sans-serif; color: var(--blue); font-size: 28px; margin: 0 0 4px; }
.box p { margin: 0 0 18px; font-size: 15px; opacity: .85; }
.box label { display: block; font-weight: 700; font-size: 15px; margin-bottom: 6px; }
.box input[type=password] { width: 100%; box-sizing: border-box; font-size: 17px; padding: 10px 12px; border: 1px solid var(--line); border-radius: 6px; background: var(--bg); color: var(--fg); }
.box .remember { display: flex; gap: 8px; align-items: center; font-size: 14px; margin: 12px 0 16px; }
.box button { width: 100%; font-size: 17px; font-weight: 700; padding: 11px; border: 0; border-radius: 6px; background: var(--green); color: #fff; cursor: pointer; }
.box .err { color: var(--bad); font-weight: 700; font-size: 14px; min-height: 20px; margin-top: 10px; }
</style>
</head>
<body>
<div class="gate"><form class="box" id="f" autocomplete="on">
<img src="__LOGO__" alt="Cultiva">
<h1>2026 EOP</h1>
<p>Confidential. Enter the password to view.</p>
<label for="pw">Password</label>
<input type="password" id="pw" autocomplete="current-password" autofocus required>
<label class="remember"><input type="checkbox" id="rm" checked> Remember on this device</label>
<button type="submit" id="go">Open</button>
<div class="err" id="err" role="alert"></div>
</form></div>
<script>
var LOCKED = __BLOB__;
function b64(s) { var b = atob(s), a = new Uint8Array(b.length); for (var i = 0; i < b.length; i++) a[i] = b.charCodeAt(i); return a; }
async function unlock(pw) {
  var base = await crypto.subtle.importKey('raw', new TextEncoder().encode(pw), 'PBKDF2', false, ['deriveKey']);
  var key = await crypto.subtle.deriveKey({name: 'PBKDF2', salt: b64(LOCKED.s), iterations: LOCKED.n, hash: 'SHA-256'}, base, {name: 'AES-GCM', length: 256}, false, ['decrypt']);
  var plain = await crypto.subtle.decrypt({name: 'AES-GCM', iv: b64(LOCKED.i)}, key, b64(LOCKED.c));
  return new TextDecoder().decode(plain);
}
function show(html) { document.open(); document.write(html); document.close(); }
var KEY = 'cultiva-eop-2026-pw';
(async function () {
  var saved = null; try { saved = localStorage.getItem(KEY); } catch (e) {}
  if (saved) { try { show(await unlock(saved)); return; } catch (e) { try { localStorage.removeItem(KEY); } catch (e2) {} } }
  document.getElementById('f').addEventListener('submit', async function (ev) {
    ev.preventDefault();
    var pw = document.getElementById('pw').value, err = document.getElementById('err'), go = document.getElementById('go');
    err.textContent = ''; go.disabled = true; go.textContent = 'Opening...';
    try {
      var html = await unlock(pw);
      if (document.getElementById('rm').checked) { try { localStorage.setItem(KEY, pw); } catch (e) {} }
      show(html);
    } catch (e) { err.textContent = 'That password is not right.'; go.disabled = false; go.textContent = 'Open'; }
  });
})();
</script>
</body>
</html>
""".replace('__LOGO__', logo).replace('__BLOB__', blob)
open(out, 'w', encoding='utf-8').write(page)
print('wrote', out, len(page.encode('utf-8')), 'bytes')
