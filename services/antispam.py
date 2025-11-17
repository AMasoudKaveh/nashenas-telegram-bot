"""
Very simple in-memory anti-spam helper.

The idea:
  - Track the timestamp of the last message for each user.
  - If the user sends a new message too quickly, treat it as spam.
"""

import time
from typing import Dict

# user_id -> last message timestamp (seconds)
user_last_message: Dict[int, float] = {}

# Minimum allowed delay between messages from the same user (in seconds)
SPAM_DELAY: float = 1.2


def check_spam(user_id: int) -> bool:
    """
    Check whether the user is sending messages too quickly.

    Args:
        user_id: Telegram user ID.

    Returns:
        True if the user is considered spamming (too fast),
        False otherwise (and the timestamp is updated).
    """
    now = time.time()
    last = user_last_message.get(user_id, 0.0)

    if now - last < SPAM_DELAY:
        return True

    user_last_message[user_id] = now
    return False
