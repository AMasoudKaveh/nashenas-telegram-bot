"""
Simple in-memory matchmaking service.

This module keeps track of:
  - users waiting for a chat
  - active two-way chat connections

Note:
    This implementation is purely in-memory. All data will be lost
    if the process restarts. For production use, consider a persistent
    storage or external state manager.
"""

from typing import Dict, Optional

# user_id -> True (presence indicates waiting for a partner)
waiting_users: Dict[int, bool] = {}

# user_id -> partner_id
active_chats: Dict[int, int] = {}


def join_queue(user_id: int) -> None:
    """
    Add a user to the waiting list for chat.

    Args:
        user_id: Telegram user ID.
    """
    waiting_users[user_id] = True


def leave_queue(user_id: int) -> None:
    """
    Remove a user from the waiting list if present.

    Args:
        user_id: Telegram user ID.
    """
    if user_id in waiting_users:
        del waiting_users[user_id]


def find_partner(user_id: int) -> Optional[int]:
    """
    Find any available partner from the waiting list.

    Args:
        user_id: Telegram user ID requesting a partner.

    Returns:
        A partner user ID if found, otherwise None.
    """
    for u in waiting_users:
        if u != user_id:
            return u
    return None


def connect_users(user1: int, user2: int) -> None:
    """
    Connect two users in an active chat and remove them from the queue.

    Args:
        user1: First user ID.
        user2: Second user ID.
    """
    active_chats[user1] = user2
    active_chats[user2] = user1
    leave_queue(user1)
    leave_queue(user2)


def get_partner(user_id: int) -> Optional[int]:
    """
    Get the partner of a user in an active chat.

    Args:
        user_id: Telegram user ID.

    Returns:
        The partner's user ID if in an active chat, otherwise None.
    """
    return active_chats.get(user_id)


def end_chat(user_id: int) -> None:
    """
    End the chat for a user and their partner, if any.

    Args:
        user_id: Telegram user ID.
    """
    partner = active_chats.get(user_id)
    if partner is not None:
        active_chats.pop(partner, None)
    active_chats.pop(user_id, None)
