#!/usr/bin/env python3
"""Build Eop Shareable Html.

Turns the 2026 EOP Claude dashboard page into one self-contained HTML file that
opens in any browser with no sign-in.

Usage:
  python3 -I build_eop_share.py PAGE_HTML CSV_DIR LOGO_DATAURI_TXT AS_OF_TEXT OUT_HTML

PAGE_HTML  the page text (the "text" field of the dashboard's files/index.html)
CSV_DIR    folder holding one CSV per dataset, named <dataset id>.csv:
           eop_targets, eop_commit, qb_window_sales, hubspot_eop,
           eop_tracker_detail, eop_payment_lines, eop_invoices
AS_OF_TEXT e.g. "Thursday, November 26, 2026"
"""
import json, os, sys

page_path, csv_dir, logo_path, as_of, out = sys.argv[1:6]
NEEDED = ['eop_targets', 'eop_commit', 'qb_window_sales', 'hubspot_eop', 'eop_tracker_detail', 'eop_payment_lines', 'eop_invoices']
data = {}
for k in NEEDED:
    p = os.path.join(csv_dir, k + '.csv')
    if not os.path.exists(p):
        sys.exit('missing ' + p)
    data[k] = open(p, encoding='utf-8').read()
page = open(page_path, encoding='utf-8').read()
logo = open(logo_path, encoding='utf-8').read().strip()
page = page.replace('<meta name="dash-one-writer">\n', '').replace('<meta name="dash-one-writer">', '')
page = page.replace('/_blob/77bcaa061f919a900bdd7d11c7645abd', logo)
style = page[page.index('<style>'):page.index('</style>') + 8]
rest = page[page.index('</style>') + 8:]
footer = ('  <p class="basis" style="margin-top:1.5rem">Snapshot as of ' + as_of +
          ". Refreshed each morning; reopen the link for the latest. Sources: Jesse Rosales's MY27 Custom Offers Tracker, "
          'QuickBooks and HubSpot. Prepared by Paul Hynek, CFO, Cultiva LLC. Confidential.</p>\n</div>')
k = rest.index('<script>')
pre, post = rest[:k], rest[k:]
i = pre.rstrip().rfind('</div>')
pre = pre[:i] + footer + pre[i + 6:]
rest = pre + post
shim = """<script>
(function () {
  var RAW = __RAW__;
  function parseCSV(t) {
    var L = [], row = [], f = '', q = false;
    for (var i = 0; i < t.length; i++) {
      var c = t[i];
      if (q) { if (c === '"') { if (t[i + 1] === '"') { f += '"'; i++; } else q = false; } else f += c; }
      else if (c === '"') q = true; else if (c === ',') { row.push(f); f = ''; }
      else if (c === '\\n') { row.push(f); L.push(row); row = []; f = ''; } else if (c !== '\\r') f += c;
    }
    if (f || row.length) { row.push(f); L.push(row); }
    var h = L[0] || [];
    return L.slice(1).filter(function (r) { return r.length > 1 || (r[0] || '') !== ''; }).map(function (r) { var o = {}; h.forEach(function (k, j) { o[k] = r[j] == null ? '' : r[j]; }); return o; });
  }
  var rows = {}; Object.keys(RAW).forEach(function (k) { rows[k] = parseCSV(RAW[k]); });
  var calcs = {}, draws = [], memo = {};
  function get(id) {
    if (memo[id]) return memo[id];
    if (rows[id]) return (memo[id] = rows[id]);
    var c = calcs[id]; if (!c) return [];
    return (memo[id] = c.fn.apply(null, c.inputs.map(get)));
  }
  window.dash = {
    calc: function (id, spec) { calcs[id] = spec; },
    data: function (id) { return {status: 'ok', data: get(id), refreshing: false, meta: []}; },
    draw: function (name, fn) { draws.push([name, fn]); },
    onData: function (fn) { fn(); }, setLink: function () {}, params: function () { return {}; },
    _run: function () { draws.forEach(function (d) { document.querySelectorAll('[data-draw="' + d[0] + '"]').forEach(function (el) { try { d[1](el); } catch (e) { console.error(e); } }); }); }
  };
  var MON = ['January','February','March','April','May','June','July','August','September','October','November','December'];
  window.d3 = {
    format: function () { return function (v) { return Math.round(v * 100) + '%'; }; },
    utcFormat: function (f) { return function (d) {
      var m = d.getUTCMonth(), y = d.getUTCFullYear(), day = d.getUTCDate();
      return f === '%B %Y' ? MON[m] + ' ' + y : MON[m].slice(0, 3) + ' ' + day + ', ' + y;
    }; }
  };
})();
</script>""".replace('__RAW__', json.dumps(data))
root = """:root { --cds-chart-grid: #E6EAE1; --cds-dur-slow: .3s; --cds-gap-xs: .25rem; --cds-gap-sm: .5rem; --cds-gap-md: 1rem; --cds-gap-lg: 1.5rem; --cds-pad-xs: .3rem; --cds-pad-sm: .6rem; --cds-pad-lg: 1.1rem; --cds-radius: 6px;
  --color-bad: #B0413E; --color-border-line: #DDE2D4; --color-fg: #23271F; --color-panel: #FFFFFF; --page-bg: #F6F7F2; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --cds-chart-grid: #2E352B; --color-bad: #E07A76; --color-border-line: #3A4236; --color-fg: #ECEFE7; --color-panel: #1C211A; --page-bg: #121510; } }
:root[data-theme="dark"] { --cds-chart-grid: #2E352B; --color-bad: #E07A76; --color-border-line: #3A4236; --color-fg: #ECEFE7; --color-panel: #1C211A; --page-bg: #121510; }
html, body { margin: 0; background: var(--page-bg); }
.wrap { max-width: 1200px; margin: 0 auto; padding: 24px 16px 48px; }
@media print { .wrap { max-width: none; } .card, .tile { break-inside: avoid; } }
"""
html = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>Cultiva 2026 EOP</title>\n<style>\n' + root + '</style>\n' + style + '\n</head>\n<body>\n<div class="wrap">\n' +
        shim + rest.strip() + '\n<script>dash._run();</script>\n</div>\n</body>\n</html>\n')
html = '\n'.join(l.strip() for l in html.split('\n') if l.strip())
open(out, 'w', encoding='utf-8').write(html)
print('wrote', out, len(html.encode('utf-8')), 'bytes')
