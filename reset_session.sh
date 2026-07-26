#!/data/data/com.termux/files/usr/bin/bash
# Update session calestia_laurent dengan session ID baru
# Jalankan: bash reset_session.sh

INSTALL_DIR="/data/data/com.termux/files/home/Thrdsbotcoment"
DATA_DIR="$INSTALL_DIR/data"

SESSION_ID="46964210485%3AMLoEMgfUJNbtik%3A1%3AAYi_T4709ism_g_sE-MOYb05kN1lToVTDeccZGRoHw"
USERNAME="calestia_laurent"
SESSION_FILE="$DATA_DIR/session_${USERNAME}.json"

echo "→ Mengupdate session $USERNAME..."

python3 - <<PYEOF
import json, uuid, time

session_id   = "$SESSION_ID"
ds_user_id   = session_id.split('%')[0].split(':')[0]
session_file = "$SESSION_FILE"

data = {
    "uuids": {
        "phone_id":          str(uuid.uuid4()),
        "uuid":              str(uuid.uuid4()),
        "client_session_id": str(uuid.uuid4()),
        "advertising_id":    str(uuid.uuid4()),
        "android_device_id": "android-" + uuid.uuid4().hex[:16],
        "request_id":        str(uuid.uuid4()),
        "tray_session_id":   str(uuid.uuid4()),
    },
    "mid": "amMkfgABAAESu0hhmPAort2glKRR",
    "authorization_data": {
        "ds_user_id": ds_user_id,
        "sessionid":  session_id,
        "should_use_header_over_cookies": True,
    },
    "cookies": {
        "sessionid":  session_id,
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
    "timezone_offset": 25200,
}

with open(session_file, "w") as f:
    json.dump(data, f, indent=2)
print(f"  ✓ Session JSON diupdate: {session_file}")

# Update accounts.txt
account_line = f"$USERNAME:SESSION_FILE:{session_file}:{session_id}"
with open("$DATA_DIR/accounts.txt", "w") as f:
    f.write(account_line + "\n")
print("  ✓ accounts.txt diupdate")
PYEOF

echo ""
echo "✓ Selesai! Jalankan bot:"
echo "  cd $INSTALL_DIR && python main.py"
