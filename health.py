"""
Lightweight Flask health server.
Runs in a background thread alongside the bot so autoscale deployments
(and external cronjob pings) have an HTTP endpoint to hit.

GET /health  →  200 {"status": "ok", "bot": "running"}
"""

import threading
from flask import Flask, jsonify
import datetime

app = Flask(__name__)

_start_time = datetime.datetime.utcnow()


@app.route("/health")
def health():
    uptime = (datetime.datetime.utcnow() - _start_time).total_seconds()
    return jsonify({
        "status": "ok",
        "bot": "running",
        "uptime_seconds": int(uptime),
    }), 200


@app.route("/")
def index():
    return jsonify({"status": "ok"}), 200


def start_health_server(host="0.0.0.0", port=5000):
    """Start Flask in a daemon thread — does not block the bot."""
    t = threading.Thread(
        target=lambda: app.run(host=host, port=port, debug=False, use_reloader=False),
        daemon=True,
        name="health-server",
    )
    t.start()
    print(f"[INFO] Health server listening on {host}:{port}/health")
    return t
