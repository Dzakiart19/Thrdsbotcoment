# Threads Automation Tool

Automation tool for posting and replying on Instagram Threads using multiple accounts.

## Project Structure

```
├── main.py             # Entry point — launches upload_manager threads
├── upload.py           # Core engine: login, post, reply, timeline scroll
├── settings.py         # Configuration dataclass (reads/writes data/settings.json)
├── mobiles.py          # Android device fingerprint database (DEVICES list)
├── custom_challenge.py # Instagram challenge handler wrapper
├── requirements.txt    # Python dependencies
└── data/               # Runtime data (created on first run)
    ├── settings.json   # Main config — edit this before running
    ├── accounts.txt    # Instagram accounts (one per line)
    ├── proxies.txt     # Proxies (one per line, optional)
    ├── texts.txt       # Comment/post templates
    ├── search_queries.txt # Search queries for feed discovery
    ├── logs.txt        # Activity log
    ├── posts.db        # SQLite: tracks repost counts
    └── history/        # Daily success/failure logs
```

## How to Run

1. Run `python main.py` once — it creates `data/settings.json` with defaults.
2. Edit `data/settings.json` and fill in:
   - `accounts_file` — path to accounts.txt
   - `proxies_file` — path to proxies.txt (optional)
   - `text_file` — path to texts.txt
   - `threads` — number of parallel threads
   - `comments` — number of comments per account
   - `captcha_key` — Anti-Captcha API key (optional)
   - `telegram_token` / `telegram_chat_id` — Telegram notifications (optional)
3. Populate `data/accounts.txt` with credentials.
4. Run `python main.py` again to start.

## Account Format

```
username:password:email:email_password
```

Or with session cookies (IAM format):
```
username:password|<useragent>|<uuids>|<cookies>
```

## Proxy Format

```
socks5://user:pass@host:port
http://user:pass@host:port
```

## User Preferences

- Use cross-platform paths via `_DATA_DIR` (never hardcode `C:/Threads/`)
- All runtime files go under `./data/`
- Keep `custom_challenge.py` as a thin wrapper around instagrapi internals
