"""
Custom challenge handler wrapping instagrapi's ChallengeResolveMixin.
ChallengeChoice enum is defined here because instagrapi doesn't expose it publicly.
"""

from enum import Enum
from instagrapi.mixins.challenge import ChallengeResolveMixin


class ChallengeChoice(Enum):
    EMAIL = "email"
    SMS = "sms"
    UNKNOWN = "unknown"


__all__ = ["ChallengeResolveMixin", "ChallengeChoice"]
