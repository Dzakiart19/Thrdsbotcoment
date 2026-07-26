"""
Shared stats tracker — bot subprocess writes here, Flask reads it.
Uses atomic write (write-then-rename) to avoid partial reads.
"""
import json, os, time, threading

_STATS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "stats.json")
_lock = threading.Lock()

_state = {
    "start_time": time.time(),
    "comments_sent": 0,
    "posts_scanned": 0,
    "requirements_skip": 0,
    "errors": 0,
    "rate_limits": 0,
    "current_account": "",
    "status": "starting",          # starting | running | rate_limited | sleeping | stopped
    "recent_logs": [],             # list of {ts, level, msg}
}


def _save():
    tmp = _STATS_FILE + ".tmp"
    try:
        with open(tmp, "w") as f:
            json.dump(_state, f)
        os.replace(tmp, _STATS_FILE)
    except Exception:
        pass


def load():
    """Load stats from disk (called by Flask)."""
    try:
        with open(_STATS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return dict(_state)


def _push_log(level: str, msg: str):
    entry = {"ts": time.strftime("%H:%M:%S"), "level": level, "msg": msg}
    with _lock:
        _state["recent_logs"].append(entry)
        if len(_state["recent_logs"]) > 50:
            _state["recent_logs"] = _state["recent_logs"][-50:]
    _save()


def set_status(status: str, account: str = ""):
    with _lock:
        _state["status"] = status
        if account:
            _state["current_account"] = account
    _save()


def inc_comments():
    with _lock:
        _state["comments_sent"] += 1
    _save()


def inc_scanned():
    with _lock:
        _state["posts_scanned"] += 1
    _save()


def inc_skip():
    with _lock:
        _state["requirements_skip"] += 1
    _save()


def inc_error():
    with _lock:
        _state["errors"] += 1
    _save()


def inc_rate_limit():
    with _lock:
        _state["rate_limits"] += 1
    _save()


def log_info(msg: str):
    _push_log("info", msg)


def log_warn(msg: str):
    _push_log("warn", msg)


def log_error(msg: str):
    _push_log("error", msg)


def reset(start_time=None):
    with _lock:
        _state["start_time"] = start_time or time.time()
        _state["comments_sent"] = 0
        _state["posts_scanned"] = 0
        _state["requirements_skip"] = 0
        _state["errors"] = 0
        _state["rate_limits"] = 0
        _state["recent_logs"] = []
        _state["status"] = "starting"
    _save()
