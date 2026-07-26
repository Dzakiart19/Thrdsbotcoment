#!/usr/bin/env bash
# ============================================================
#  install.sh — Setup semua dependencies Threads Bot
#  Jalankan: bash install.sh
# ============================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${CYAN}[INFO]${NC}  $*"; }
ok()   { echo -e "${GREEN}[OK]${NC}    $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC}  $*"; }
err()  { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

echo ""
echo -e "${CYAN}============================================${NC}"
echo -e "${CYAN}   Threads Bot — Installer${NC}"
echo -e "${CYAN}============================================${NC}"
echo ""

# ── 1. Cek Python ────────────────────────────────────────────
log "Mengecek Python..."
if command -v python3 &>/dev/null; then
    PYTHON_VER=$(python3 --version 2>&1)
    ok "Ditemukan: $PYTHON_VER"
else
    err "Python3 tidak ditemukan. Install Python 3.13+ terlebih dahulu."
fi

# ── 2. Cek / Install uv ──────────────────────────────────────
log "Mengecek uv package manager..."
if command -v uv &>/dev/null; then
    UV_VER=$(uv --version 2>&1)
    ok "Ditemukan: $UV_VER"
else
    log "uv tidak ditemukan, menginstall..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    if command -v uv &>/dev/null; then
        ok "uv berhasil diinstall: $(uv --version)"
    else
        err "Gagal menginstall uv. Install manual: https://docs.astral.sh/uv/"
    fi
fi

# ── 3. Install Python packages via uv ────────────────────────
log "Menginstall Python packages dari pyproject.toml..."
uv sync
ok "Semua Python packages terinstall:"
echo ""
uv pip list 2>/dev/null | grep -E "instagrapi|flask|pillow|pytelegrambotapi|anticaptchaofficial|colorama|requests" | \
    while read -r line; do echo -e "    ${GREEN}✓${NC} $line"; done
echo ""

# ── 4. Buat direktori data yang dibutuhkan ───────────────────
log "Membuat direktori data..."
mkdir -p data/history data/thread
ok "Direktori data siap"

# ── 5. Cek settings.json ─────────────────────────────────────
log "Mengecek data/settings.json..."
if [ -f "data/settings.json" ]; then
    ok "settings.json sudah ada"
else
    if [ -f "data/settings.template.json" ]; then
        cp data/settings.template.json data/settings.json
        ok "settings.json dibuat dari template"
    else
        warn "settings.json belum ada — jalankan 'uv run python3 main.py' untuk generate otomatis"
    fi
fi

# ── 6. Cek accounts.txt ──────────────────────────────────────
log "Mengecek data/accounts.txt..."
if [ -f "data/accounts.txt" ] && [ -s "data/accounts.txt" ]; then
    ACCOUNT_COUNT=$(grep -c "." data/accounts.txt 2>/dev/null || echo 0)
    ok "accounts.txt ditemukan ($ACCOUNT_COUNT akun)"
else
    warn "data/accounts.txt kosong atau belum ada — isi sebelum menjalankan bot"
fi

# ── 7. Cek texts.txt ─────────────────────────────────────────
log "Mengecek data/texts.txt..."
if [ -f "data/texts.txt" ] && [ -s "data/texts.txt" ]; then
    TEXT_COUNT=$(grep -c "." data/texts.txt 2>/dev/null || echo 0)
    ok "texts.txt ditemukan ($TEXT_COUNT teks)"
else
    warn "data/texts.txt kosong atau belum ada — isi dengan teks komentar sebelum menjalankan bot"
fi

# ── Selesai ──────────────────────────────────────────────────
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}   Instalasi selesai!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "  Jalankan bot dengan perintah:"
echo -e "  ${CYAN}uv run python3 main.py${NC}"
echo ""
