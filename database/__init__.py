# nashenas_bot/database/__init__.py
"""
Database package for Nashenas bot.

This module re-exports commonly used database helpers so they can be
imported from `nashenas_bot.database` directly.
"""

from .db import (
    get_connection,
    init_db,
    add_user,
    get_user,
    user_exists,
    get_user_id_by_username,
    add_group,
    get_group,
    add_user_to_group,
    get_group_users,
    add_anon_message,
    get_user_messages,
)

__all__ = [
    "get_connection",
    "init_db",
    "add_user",
    "get_user",
    "user_exists",
    "get_user_id_by_username",
    "add_group",
    "get_group",
    "add_user_to_group",
    "get_group_users",
    "add_anon_message",
    "get_user_messages",
]
