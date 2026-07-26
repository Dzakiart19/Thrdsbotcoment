"""
Challenge handler — uses fake_client stubs (no instagrapi needed).
"""

from enum import Enum
from fake_client import ChallengeResolveMixin


class ChallengeChoice(Enum):
    EMAIL = "email"
    SMS = "sms"
    UNKNOWN = "unknown"


__all__ = ["ChallengeResolveMixin", "ChallengeChoice"]
