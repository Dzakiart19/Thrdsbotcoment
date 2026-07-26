"""
Flask server — health check + real-time monitoring dashboard.
Runs in a background daemon thread alongside the bot.

Routes:
  GET /          →  dashboard HTML
  GET /health    →  200 {"status":"ok", ...}
  GET /api/stats →  JSON stats (polled every 5s by dashboard)
  GET /api/logs  →  last 50 log entries
"""

import threading, time, datetime
from flask import Flask, jsonify, render_template_string
import stats_tracker as st

app = Flask(__name__)
_start_time = time.time()

# ─── Dashboard HTML ───────────────────────────────────────────────────────────
DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Threads Bot Monitor</title>
<style>
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background:#0d0d0d; color:#e0e0e0; font-family:'Segoe UI',system-ui,sans-serif; min-height:100vh; }
  header { background:#111; border-bottom:1px solid #222; padding:16px 24px; display:flex; align-items:center; gap:12px; }
  header h1 { font-size:18px; font-weight:600; letter-spacing:.5px; }
  .dot { width:10px; height:10px; border-radius:50%; background:#555; flex-shrink:0; }
  .dot.running { background:#22c55e; box-shadow:0 0 8px #22c55e88; animation:pulse 2s infinite; }
  .dot.rate_limited { background:#f59e0b; box-shadow:0 0 8px #f59e0b88; }
  .dot.sleeping { background:#6366f1; }
  .dot.stopped,.dot.starting { background:#ef4444; }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.5} }
  .status-text { font-size:13px; color:#888; margin-left:4px; }
  .status-text span { color:#e0e0e0; font-weight:500; text-transform:capitalize; }

  main { padding:24px; max-width:1100px; margin:0 auto; }

  /* Cards */
  .cards { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:16px; margin-bottom:24px; }
  .card { background:#161616; border:1px solid #222; border-radius:12px; padding:20px; }
  .card .label { font-size:11px; color:#555; text-transform:uppercase; letter-spacing:.8px; margin-bottom:8px; }
  .card .value { font-size:32px; font-weight:700; line-height:1; color:#fff; }
  .card .value.green { color:#22c55e; }
  .card .value.yellow { color:#f59e0b; }
  .card .value.red { color:#ef4444; }
  .card .value.purple { color:#a78bfa; }
  .card .sub { font-size:12px; color:#444; margin-top:6px; }

  /* Account bar */
  .account-bar { background:#161616; border:1px solid #222; border-radius:10px; padding:14px 18px; margin-bottom:24px; font-size:13px; color:#666; }
  .account-bar span { color:#fff; font-weight:500; }
  .account-bar .sep { margin:0 10px; }

  /* Log feed */
  .log-section h2 { font-size:13px; color:#555; text-transform:uppercase; letter-spacing:.8px; margin-bottom:12px; }
  .log-feed { background:#0a0a0a; border:1px solid #1a1a1a; border-radius:10px; padding:12px; height:360px; overflow-y:auto; display:flex; flex-direction:column-reverse; }
  .log-entry { display:flex; gap:10px; padding:5px 4px; border-bottom:1px solid #111; font-size:12px; font-family:'Cascadia Code','Fira Code',monospace; }
  .log-entry:last-child { border-bottom:none; }
  .log-entry .ts { color:#333; flex-shrink:0; }
  .log-entry .msg.info { color:#94a3b8; }
  .log-entry .msg.warn { color:#f59e0b; }
  .log-entry .msg.error { color:#ef4444; }
  .log-entry .msg.rate { color:#a78bfa; }

  /* Refresh indicator */
  .footer { text-align:center; font-size:11px; color:#333; margin-top:20px; }
  .footer span { color:#555; }
</style>
</head>
<body>
<header>
  <div class="dot" id="status-dot"></div>
  <h1>Threads Bot Monitor</h1>
  <div class="status-text">Status: <span id="status-label">loading…</span></div>
</header>
<main>
  <div class="cards">
    <div class="card">
      <div class="label">Comments Sent</div>
      <div class="value green" id="comments">—</div>
      <div class="sub">successful posts</div>
    </div>
    <div class="card">
      <div class="label">Posts Scanned</div>
      <div class="value" id="scanned">—</div>
      <div class="sub">posts evaluated</div>
    </div>
    <div class="card">
      <div class="label">Skipped</div>
      <div class="value yellow" id="skipped">—</div>
      <div class="sub">requirements not met</div>
    </div>
    <div class="card">
      <div class="label">Rate Limits</div>
      <div class="value purple" id="rate_limits">—</div>
      <div class="sub">429 hits</div>
    </div>
    <div class="card">
      <div class="label">Errors</div>
      <div class="value red" id="errors">—</div>
      <div class="sub">exceptions</div>
    </div>
    <div class="card">
      <div class="label">Uptime</div>
      <div class="value" id="uptime" style="font-size:22px">—</div>
      <div class="sub" id="uptime-since">since start</div>
    </div>
  </div>

  <div class="account-bar">
    Account: <span id="account">—</span>
    <span class="sep">|</span>
    Started: <span id="started-at">—</span>
  </div>

  <div class="log-section">
    <h2>Live Activity Feed</h2>
    <div class="log-feed" id="log-feed">
      <div class="log-entry"><span class="ts">--:--:--</span><span class="msg info">Waiting for data…</span></div>
    </div>
  </div>
</main>
<div class="footer">Auto-refreshes every <span>5s</span> &nbsp;·&nbsp; <span id="last-update">—</span></div>

<script>
function fmtUptime(secs) {
  const h = Math.floor(secs/3600), m = Math.floor((secs%3600)/60), s = Math.floor(secs%60);
  return (h>0?h+'h ':'')+m+'m '+s+'s';
}
function fmtTime(ts) {
  return new Date(ts*1000).toLocaleTimeString();
}

async function refresh() {
  try {
    const r = await fetch('/api/stats');
    const d = await r.json();

    // Status dot
    const dot = document.getElementById('status-dot');
    dot.className = 'dot ' + d.status;
    document.getElementById('status-label').textContent = d.status.replace('_',' ');

    // Cards
    document.getElementById('comments').textContent   = d.comments_sent;
    document.getElementById('scanned').textContent    = d.posts_scanned;
    document.getElementById('skipped').textContent    = d.requirements_skip;
    document.getElementById('rate_limits').textContent= d.rate_limits;
    document.getElementById('errors').textContent     = d.errors;

    const uptime = Date.now()/1000 - d.start_time;
    document.getElementById('uptime').textContent = fmtUptime(uptime);
    document.getElementById('account').textContent     = d.current_account || '—';
    document.getElementById('started-at').textContent  = fmtTime(d.start_time);

    // Log feed
    const feed = document.getElementById('log-feed');
    if (d.recent_logs && d.recent_logs.length) {
      feed.innerHTML = '';
      [...d.recent_logs].reverse().forEach(e => {
        const el = document.createElement('div');
        el.className = 'log-entry';
        const lvl = e.level === 'rate' ? 'rate' : e.level;
        el.innerHTML = `<span class="ts">${e.ts}</span><span class="msg ${lvl}">${e.msg}</span>`;
        feed.appendChild(el);
      });
    }

    document.getElementById('last-update').textContent = 'Updated ' + new Date().toLocaleTimeString();
  } catch(e) {
    document.getElementById('status-label').textContent = 'unreachable';
  }
}

refresh();
setInterval(refresh, 5000);
</script>
</body>
</html>"""


@app.route("/")
def dashboard():
    return render_template_string(DASHBOARD_HTML)


@app.route("/health")
def health():
    data = st.load()
    uptime = time.time() - _start_time
    return jsonify({
        "status": "ok",
        "bot": data.get("status", "unknown"),
        "uptime_seconds": int(uptime),
        "comments_sent": data.get("comments_sent", 0),
    }), 200


@app.route("/api/stats")
def api_stats():
    return jsonify(st.load())


@app.route("/api/logs")
def api_logs():
    data = st.load()
    return jsonify({"logs": data.get("recent_logs", [])})


def start_health_server(host="0.0.0.0", port=5000):
    """Start Flask in a daemon thread — does not block the bot."""
    t = threading.Thread(
        target=lambda: app.run(host=host, port=port, debug=False, use_reloader=False),
        daemon=True,
        name="health-server",
    )
    t.start()
    print(f"[INFO] Dashboard: http://{host}:{port}/")
    print(f"[INFO] Health:    http://{host}:{port}/health")
    return t
