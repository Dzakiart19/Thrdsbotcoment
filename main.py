"""
Entry point for the Threads automation tool.
Reads settings from ./data/settings.json (or prompts to create one),
then launches upload_manager threads as configured.

A lightweight Flask health server is started first so that:
  - Autoscale deployments pass health checks
  - External cronjob (e.g. UptimeRobot / cron-job.org) can ping /health
    to keep the container warm
"""

import os
import json
import multiprocessing
from settings import Settings
from upload import upload_manager
from health import start_health_server

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


def ensure_data_dir():
    """Create required directories if they don't exist."""
    for sub in ["", "history", "thread"]:
        os.makedirs(os.path.join(DATA_DIR, sub), exist_ok=True)


def create_default_settings():
    """Write a blank settings.json so the user can fill it in."""
    default = Settings()
    default.accounts_file = os.path.join(DATA_DIR, "accounts.txt")
    default.proxies_file  = os.path.join(DATA_DIR, "proxies.txt")
    default.text_file     = os.path.join(DATA_DIR, "texts.txt")
    default.search_query_file = os.path.join(DATA_DIR, "search_queries.txt")
    default.save()
    print(f"[INFO] Default settings written to {os.path.join(DATA_DIR, 'settings.json')}")
    print("[INFO] Edit the file, then re-run main.py.")


def main():
    # ── Start health server (non-blocking) ───────────────────────────────────
    start_health_server(host="0.0.0.0", port=5000)

    ensure_data_dir()

    settings_path = os.path.join(DATA_DIR, "settings.json")
    if not os.path.exists(settings_path):
        print(f"[INFO] settings.json not found at {settings_path}")
        create_default_settings()
        # Keep health server alive even when bot is not configured
        import time
        print("[INFO] Health server is running. Edit settings.json and restart.")
        while True:
            time.sleep(60)

    settings = Settings()
    print(f"[INFO] Loaded settings — threads={settings.threads}, comments={settings.comments}")

    # Validate required files exist
    for label, path in [
        ("accounts_file", settings.accounts_file),
        ("text_file",     settings.text_file),
    ]:
        if not path or not os.path.exists(path):
            print(f"[ERROR] {label} not found: '{path}'. Update settings.json and try again.")
            return

    processes = []
    serialized = str(settings)

    for i in range(settings.threads):
        p = multiprocessing.Process(
            target=upload_manager,
            args=(serialized, i),
            daemon=True,
        )
        p.start()
        processes.append(p)
        print(f"[INFO] Started thread #{i}")

    for p in processes:
        p.join()

    print("[INFO] All threads finished.")


if __name__ == "__main__":
    main()
