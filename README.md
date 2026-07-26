# Threads Auto Commenter Bot

Bot otomatis untuk komentar di postingan Threads (Instagram), dirancang untuk menargetkan audiens **Tier 1** (US, UK, CA, AU) dengan komentar yang mempromosikan konten melalui search query yang relevan.

---

## Fitur

- ✅ **Login via Web Session** — tidak perlu username/password, cukup cookie dari browser
- ✅ **Unlimited comments** — berjalan terus tanpa batas (`cirlce_upload: true`)
- ✅ **Multi-thread** — jalankan banyak akun secara paralel
- ✅ **Search-based targeting** — komentari post dari hasil pencarian kata kunci T1
- ✅ **Auto-rotate query** — ganti kata kunci otomatis jika halaman kosong
- ✅ **Filter post cerdas** — minimum likes, views, waktu posting
- ✅ **Proxy support** — HTTP/SOCKS5 proxy per thread
- ✅ **Telegram notifikasi** — laporan statistik per akun
- ✅ **Health endpoint** — `GET /health` untuk cronjob / uptime monitor
- ✅ **Autoscale deployment** — siap deploy di Replit Autoscale

---

## Struktur Direktori

```
.
├── main.py                  # Entry point — jalankan ini
├── health.py                # Flask /health endpoint (background thread)
├── upload.py                # Logika utama bot (login, posting, komentar)
├── settings.py              # Model settings
├── fake_client.py           # Pengganti instagrapi (zero-dep, no Rust)
├── custom_challenge.py      # Challenge handler stub
├── mobiles.py               # Database device Android
├── pyproject.toml           # Dependencies (uv)
└── data/
    ├── accounts.txt         # Daftar akun (lihat format di bawah)
    ├── proxies.txt          # Daftar proxy (opsional)
    ├── texts.txt            # Teks komentar (1 baris = 1 komentar)
    ├── search_queries.txt   # Kata kunci pencarian Threads
    ├── posts.txt            # URL post untuk mode Warm 2.0 (opsional)
    ├── settings.json        # Konfigurasi bot
    └── settings.template.json
```

---

## Setup

### 1. Install dependencies

```bash
uv sync
```

### 2. Format akun (`data/accounts.txt`)

Pilih salah satu format:

#### Web Session (dari browser — paling mudah)
```
username:WEB_SESSION:ds_user_id:sessionid
```
Contoh:
```
shadowheist08:WEB_SESSION:40126635242:40126635242%3ADPa9IQ0a6yA1HC%3A28%3A...
```

#### Session File (dari instagrapi)
```
username:SESSION_FILE:/path/to/session.json:sessionid
```

#### Username & Password
```
username:password:email:email_password
```

### 3. Cara ambil Web Session dari browser

1. Buka **threads.com**, pastikan sudah login
2. Tekan **F12** → tab **Application** (Chrome) atau **Storage** (Firefox)
3. Klik **Cookies → https://www.threads.com**
4. Copy nilai:
   - `ds_user_id` — angka numerik (user ID)
   - `sessionid` — string panjang dimulai dengan angka

### 4. Konfigurasi (`data/settings.json`)

| Key | Default | Keterangan |
|---|---|---|
| `comments` | `999999` | Jumlah komentar per akun (999999 = unlimited) |
| `cirlce_upload` | `true` | Loop akun terus-menerus |
| `spam_method` | `1` | `0`=Timeline, `1`=Search trending, `2`=Search terbaru, `3`=Random, `4`=Warm 2.0 |
| `threads` | `1` | Jumlah thread paralel |
| `minimum_likes` | `5` | Skip post di bawah N likes |
| `max_time_seconds` | `86400` | Skip post lebih lama dari N detik (86400 = 24 jam) |
| `min_views_on_post` | `0` | Skip post di bawah N views |
| `max_posts_on_post` | `1` | Maksimal komentar per post per sesi |
| `proxies_file` | `data/proxies.txt` | Path file proxy |
| `telegram_token` | `""` | Bot token Telegram (opsional) |
| `telegram_chat_id` | `""` | Chat ID Telegram (opsional) |

### 5. Format proxy (`data/proxies.txt`)

```
http://user:pass@host:port
socks5://user:pass@host:port
```

---

## Menjalankan Bot

```bash
uv run python3 main.py
```

Bot akan:
1. Menjalankan health server di port `5000`
2. Login ke semua akun di `accounts.txt`
3. Mencari post berdasarkan `search_queries.txt`
4. Meninggalkan komentar dari `texts.txt` (dipilih acak)
5. Delay 60–120 detik antar komentar
6. Loop ulang setelah semua akun selesai

---

## Mode Spam (`spam_method`)

| Value | Mode | Keterangan |
|---|---|---|
| `0` | Timeline | Feed pribadi akun yang login |
| `1` | Search Trending | Cari berdasarkan kata kunci (sorted: populer) |
| `2` | Search Terbaru | Cari berdasarkan kata kunci (sorted: recent) |
| `3` | Random | Acak antara mode 1, 2, Warm 2.0 setiap akun |
| `4` | Warm 2.0 | Komentar ke post spesifik dari `posts.txt` |

---

## Health Endpoint

Bot menjalankan HTTP server di port `5000`:

```
GET /health  →  {"status": "ok", "bot": "running", "uptime_seconds": 123}
GET /        →  {"status": "ok"}
```

Gunakan URL `/health` di cronjob (cron-job.org / UptimeRobot / Better Uptime) untuk:
- Memantau apakah bot masih berjalan
- Mencegah autoscale deployment sleep (ping setiap 5 menit)

---

## Deployment (Replit Autoscale)

Sudah dikonfigurasi untuk Replit Autoscale. Klik **Publish** di Replit.

Setelah deploy, daftarkan URL production ke cronjob:
```
https://<nama-repl>.replit.app/health
```
Interval ping: **setiap 5 menit** agar container tidak sleep.

---

## Target Search Queries (T1)

File `data/search_queries.txt` berisi 80+ kata kunci yang menargetkan audiens berbahasa Inggris di negara Tier 1:
- 🇺🇸 US: `us creator`, `american creator`, `new york`, `los angeles`, `miami`
- 🇬🇧 UK: `uk creator`, `british creator`, `london`
- 🇨🇦 CA: `canadian creator`, `toronto`
- 🇦🇺 AU: `australian creator`, `sydney`
- Global: `onlyfans`, `fansly`, `trending now`, `viral us`, dll.

---

## Log

- **Console** — output real-time di terminal
- **`data/logs.txt`** — log semua request/response API
- **`data/history/DD.MM/successful_all.txt`** — akun yang berhasil
- **`data/history/DD.MM/failed.txt`** — akun yang gagal + alasan
