# services/user_utils.py
"""
Utility functions for working with users.

This module provides:
  - Simple helpers to register a user in the database based on a Message.
  - A thin wrapper around `get_user` from the database layer.
  - A very basic in-memory block/unblock mechanism (not persisted).
"""

from typing import Optional, Set, Tuple, Any

from aiogram.types import Message

from database.db import get_user, add_user


def register_user(message: Message) -> None:
    """
    Store the user in the database if they are not already stored.

    Args:
        message: Incoming message from which the user object is read.
    """
    user = message.from_user

    add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )


def get_user_info(user_id: int) -> Optional[Tuple[Any, ...]]:
    """
    Retrieve user information from the database.

    Args:
        user_id: Telegram user ID.

    Returns:
        The database row for this user, or None if not found.
    """
    return get_user(user_id)


# For now, the block/unblock system is kept simple and in-memory only.
# If you later want persistent blocking, extend this module and `db.py`.

_blocked_users: Set[int] = set()


def block_user_local(user_id: int) -> None:
    """
    Block a user in memory (NOT persisted to the database).

    Args:
        user_id: Telegram user ID to block.
    """
    _blocked_users.add(user_id)


def is_user_blocked_local(user_id: int) -> bool:
    """
    Check whether a user is blocked in the in-memory block list.

    Args:
        user_id: Telegram user ID.

    Returns:
        True if the user is blocked in memory, False otherwise.
    """
    return user_id in _blocked_users
