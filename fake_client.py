"""
Minimal drop-in replacement for instagrapi.Client.
Implements only what this bot actually uses — no pydantic, no Rust, no build steps.
Pure stdlib + requests.
"""

import json
import uuid as _uuid

BLOKS_VERSION = "7189b949425f9bf80ea8bd880cf5a3080b292d9b1c4b38a18d112f7c4b71e7a8"
DEFAULT_USER_AGENT = (
    "Instagram 428.0.0.47.67 Android "
    "(34/14; 480dpi; 1344x2992; Google/google; Pixel 8 Pro; husky; husky; en_US; 961145276)"
)


class FakeClient:
    """Lightweight instagrapi.Client replacement — no external deps."""

    def __init__(self, proxy=None):
        self._proxy = proxy
        self._uuids = {
            "phone_id":          str(_uuid.uuid4()),
            "uuid":              str(_uuid.uuid4()),
            "client_session_id": str(_uuid.uuid4()),
            "advertising_id":    str(_uuid.uuid4()),
            "android_device_id": "android-" + _uuid.uuid4().hex[:16],
            "request_id":        str(_uuid.uuid4()),
            "tray_session_id":   str(_uuid.uuid4()),
        }
        self._device = {}
        self._user_agent = DEFAULT_USER_AGENT
        self._mid = ""
        self._settings = {}
        self.last_json = {}
        self.bloks_versioning_id = BLOKS_VERSION

    # ── UUID / identity properties ───────────────────────────────────────────
    @property
    def uuid(self):
        return self._uuids.get("uuid", "")

    @property
    def phone_id(self):
        return self._uuids.get("phone_id", "")

    @property
    def mid(self):
        return self._mid

    @mid.setter
    def mid(self, value):
        self._mid = value or ""

    @property
    def user_agent(self):
        return self._user_agent

    # ── Setters ──────────────────────────────────────────────────────────────
    def set_uuids(self, uuids: dict):
        self._uuids.update(uuids)

    def set_device(self, device: dict, generate_agent: bool = False):
        self._device = device or {}
        if generate_agent and device:
            try:
                self._user_agent = (
                    f"Instagram {device.get('app_version', '428.0.0.47.67')} "
                    f"Android ({device.get('android_version', 34)}/"
                    f"{device.get('android_release', '14')}; "
                    f"{device.get('dpi', '480dpi')}; "
                    f"{device.get('resolution', '1344x2992')}; "
                    f"{device.get('manufacturer', 'Google/google')}; "
                    f"{device.get('device', 'husky')}; "
                    f"{device.get('model', 'Pixel 8 Pro')}; "
                    f"{device.get('cpu', 'husky')}; "
                    f"en_US; "
                    f"{device.get('version_code', '961145276')})"
                )
            except Exception:
                pass

    def set_user_agent(self, agent=None, generate: bool = False):
        if agent:
            self._user_agent = agent
        # if None: keep current (already set by set_device or constructor default)

    def load_settings(self, path: str):
        """Load session JSON (created by install.sh)."""
        with open(path, "r") as f:
            self._settings = json.load(f)

        if "uuids" in self._settings:
            self._uuids.update(self._settings["uuids"])
        if "device_settings" in self._settings:
            self._device = self._settings["device_settings"]
        if "user_agent" in self._settings:
            self._user_agent = self._settings["user_agent"]
        if "bloks_versioning_id" in self._settings:
            self.bloks_versioning_id = self._settings["bloks_versioning_id"]

    def login(self, username, password, email="", email_password="", relogin=False):
        """SESSION_FILE accounts cannot relogin via username/password — return False."""
        return False

    def get_settings(self) -> dict:
        """Return settings dict as expected by upload.py."""
        s = dict(self._settings)
        s.setdefault("uuids", self._uuids)
        s.setdefault("device_settings", self._device)
        s.setdefault("user_agent", self._user_agent)
        s.setdefault("timezone_offset", 25200)
        return s


# ── Exception stubs ───────────────────────────────────────────────────────────
class ChallengeRequired(Exception):
    pass


class ChallengeUnknownStep(Exception):
    pass


# ── ChallengeResolveMixin stub ────────────────────────────────────────────────
class ChallengeResolveMixin:
    """No-op stub — challenge resolution not needed for SESSION_FILE login."""

    def update(self, client):
        pass

    def challenge_resolve(self, json_data):
        pass


# ── json_value utility ────────────────────────────────────────────────────────
def json_value(data, *keys, default=None):
    try:
        for key in keys:
            data = data[key]
        return data
    except (KeyError, IndexError, TypeError):
        return default
