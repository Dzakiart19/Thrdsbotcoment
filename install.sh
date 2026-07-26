#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
#  Threads Auto Commenter — Termux Installer
#  Jalankan sekali: bash install.sh
# ============================================================

set -e
# Pastikan error tidak tersembunyi
trap 'echo -e "\n\033[0;31m[ERROR] Instalasi gagal di baris $LINENO. Baca pesan error di atas.\033[0m\n"; exit 1' ERR

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

REPO_URL="https://github.com/Dzakiart19/Thrdsbotcoment"
INSTALL_DIR="$HOME/Thrdsbotcoment"
DATA_DIR="$INSTALL_DIR/data"

echo ""
echo -e "${CYAN}${BOLD}╔══════════════════════════════════════╗${NC}"
echo -e "${CYAN}${BOLD}║   Threads Auto Commenter Installer   ║${NC}"
echo -e "${CYAN}${BOLD}╚══════════════════════════════════════╝${NC}"
echo ""

# ── 1. Update Termux packages ─────────────────────────────
echo -e "${YELLOW}[1/6] Mengupdate package Termux...${NC}"
pkg update -y -q && pkg upgrade -y -q

# ── 2. Install system dependencies ───────────────────────
echo -e "${YELLOW}[2/6] Menginstall dependensi sistem...${NC}"
pkg install -y -q python git libxml2 libxslt openssl libjpeg-turbo python-pillow

# ── 3. Clone / update repo ───────────────────────────────
echo -e "${YELLOW}[3/6] Mengunduh project dari GitHub...${NC}"
if [ -d "$INSTALL_DIR/.git" ]; then
    echo "  → Repo sudah ada, update..."
    cd "$INSTALL_DIR"
    git pull origin main --rebase
else
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# ── 4. Install Python packages ───────────────────────────
echo -e "${YELLOW}[4/6] Menginstall Python packages...${NC}"
# Catatan: JANGAN upgrade pip di Termux (dilarang)
# pydantic==1.9.2 → tidak ada strict check_fields (aman untuk instagrapi<2)
# instagrapi==1.16.0 → versi stabil terakhir sebelum pindah ke pydantic v2
pip install -q \
    "pydantic==1.9.2" \
    "instagrapi<2" \
    colorama \
    pyTelegramBotAPI \
    anticaptchaofficial \
    requests

# ── Patch instagrapi untuk Python 3.10+ compatibility ──
echo "  → Patching instagrapi untuk kompatibilitas pydantic..."
python3 - <<'PYEOF'
import site, os

patched_any = False
for sp in site.getsitepackages():
    types_file = os.path.join(sp, 'instagrapi', 'types.py')
    if not os.path.exists(types_file):
        continue
    with open(types_file, 'r') as f:
        content = f.read()
    # Tambah check_fields=False ke semua validator yang bermasalah
    import re
    new_content = re.sub(
        r'@validator\(("external_url"|"thumbnail_url"|"profile_pic_url"|"hd_profile_pic_url_info")([^)]*)\)',
        lambda m: f'@validator({m.group(1)}{m.group(2)}, check_fields=False)' if 'check_fields' not in m.group(0) else m.group(0),
        content
    )
    if new_content != content:
        with open(types_file, 'w') as f:
            f.write(new_content)
        print("  ✓ instagrapi/types.py berhasil di-patch")
        patched_any = True
    break

if not patched_any:
    print("  → Tidak ada patch yang diperlukan")
PYEOF

# ── 5. Setup direktori data ──────────────────────────────
echo -e "${YELLOW}[5/6] Menyiapkan direktori data...${NC}"
mkdir -p "$DATA_DIR/history"
touch "$DATA_DIR/proxies.txt"
touch "$DATA_DIR/posts.txt"

# Generate settings.json dari template dengan path yang benar
sed "s|DATADIR|$DATA_DIR|g" "$INSTALL_DIR/data/settings.template.json" > "$DATA_DIR/settings.json"
echo "  → settings.json dibuat di $DATA_DIR/settings.json"

# ── 6. Setup akun ────────────────────────────────────────
echo -e "${YELLOW}[6/6] Setup akun Instagram/Threads...${NC}"
echo ""

if [ -f "$DATA_DIR/accounts.txt" ] && [ -s "$DATA_DIR/accounts.txt" ]; then
    echo -e "${GREEN}  ✓ accounts.txt sudah ada, skip setup akun.${NC}"
else
    echo -e "${BOLD}  Masukkan data akun Instagram:${NC}"
    echo ""

    read -p "  Username Instagram : " IG_USER
    read -p "  Session ID         : " IG_SESSION

    # Buat session file
    DS_USER_ID=$(echo "$IG_SESSION" | cut -d'%' -f1 | cut -d':' -f1)
    SESSION_FILE="$DATA_DIR/session_${IG_USER}.json"

    python3 - <<PYEOF
import json, base64, uuid, time

session_id   = "$IG_SESSION"
username     = "$IG_USER"
ds_user_id   = session_id.split('%')[0].split(':')[0]
session_file = "$SESSION_FILE"

# Buat session file format instagrapi
session_data = {
    "uuids": {
        "phone_id":         str(uuid.uuid4()),
        "uuid":             str(uuid.uuid4()),
        "client_session_id":str(uuid.uuid4()),
        "advertising_id":   str(uuid.uuid4()),
        "android_device_id":"android-" + uuid.uuid4().hex[:16],
        "request_id":       str(uuid.uuid4()),
        "tray_session_id":  str(uuid.uuid4()),
    },
    "mid": "",
    "ig_u_rur": None,
    "ig_www_claim": None,
    "authorization_data": {
        "ds_user_id": ds_user_id,
        "sessionid": session_id,
        "should_use_header_over_cookies": True,
    },
    "cookies": {
        "sessionid": session_id,
        "ds_user_id": ds_user_id,
    },
    "last_login": time.time(),
    "device_settings": {
        "android_version": 34,
        "android_release": "14",
        "dpi": "480dpi",
        "resolution": "1344x2992",
        "manufacturer": "Google/google",
        "device": "husky",
        "model": "Pixel 8 Pro",
        "cpu": "husky",
        "app_version": "428.0.0.47.67",
        "version_code": "961145276",
        "bloks_versioning_id": "7189b949425f9bf80ea8bd880cf5a3080b292d9b1c4b38a18d112f7c4b71e7a8",
    },
    "user_agent": "Instagram 428.0.0.47.67 Android (34/14; 480dpi; 1344x2992; Google/google; Pixel 8 Pro; husky; husky; en_US; 961145276)",
    "country": "ID",
    "country_code": 62,
    "locale": "en_US",
    "timezone_offset": 25200,
    "timezone_name": "Asia/Jakarta",
    "push_disabled": False,
    "request_timeout": 1,
    "public_request_retries_count": 3,
    "public_request_retries_timeout": 5,
    "session_retry_total": 5,
    "session_retry_backoff_factor": 2,
    "session_retry_statuses": [429, 500, 502, 503, 504],
    "public_transport": None,
    "public_transport_impersonate": None,
    "tls_verify": True,
}

with open(session_file, "w") as f:
    json.dump(session_data, f, indent=2)

# Buat accounts.txt
account_line = f"{username}:SESSION_FILE:{session_file}:{session_id}"
with open("$DATA_DIR/accounts.txt", "w") as f:
    f.write(account_line + "\n")

print(f"  Session disimpan ke: {session_file}")
print(f"  accounts.txt dibuat")
PYEOF

fi

# ── Done ─────────────────────────────────────────────────
echo ""
echo -e "${GREEN}${BOLD}╔══════════════════════════════════════╗${NC}"
echo -e "${GREEN}${BOLD}║        ✓ Instalasi Selesai!          ║${NC}"
echo -e "${GREEN}${BOLD}╚══════════════════════════════════════╝${NC}"
echo ""
echo -e "  Lokasi project : ${CYAN}$INSTALL_DIR${NC}"
echo -e "  Data akun      : ${CYAN}$DATA_DIR/accounts.txt${NC}"
echo -e "  Teks komentar  : ${CYAN}$DATA_DIR/texts.txt${NC}"
echo ""
echo -e "${BOLD}  Cara menjalankan bot:${NC}"
echo -e "  ${CYAN}cd $INSTALL_DIR && python main.py${NC}"
echo ""
echo -e "${BOLD}  Cara menjalankan di background (tidak berhenti walau layar mati):${NC}"
echo -e "  ${CYAN}cd $INSTALL_DIR && nohup python main.py > data/output.log 2>&1 &${NC}"
echo ""
echo -e "${BOLD}  Cek log background:${NC}"
echo -e "  ${CYAN}tail -f $DATA_DIR/output.log${NC}"
echo ""

# Tanya mau langsung jalankan?
read -p "  Jalankan bot sekarang? (y/n): " RUN_NOW
if [[ "$RUN_NOW" == "y" || "$RUN_NOW" == "Y" ]]; then
    echo ""
    echo -e "${GREEN}  Menjalankan bot...${NC}"
    cd "$INSTALL_DIR"
    python main.py
fi
