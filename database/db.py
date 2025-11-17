# database/db.py
"""
Database utilities for the Nashenas bot.

This module contains schema initialization and helper functions
for working with users, groups, and anonymous messages.
"""

import os
import sqlite3
from datetime import datetime
from typing import Any, List, Optional

# Database file name can be overridden via environment variable.
DB_NAME: str = os.getenv("DB_NAME", "database.db")


def get_connection() -> sqlite3.Connection:
    """
    Create and return a new SQLite connection.
    """
    return sqlite3.connect(DB_NAME)


def init_db() -> None:
    """
    Initialize database schema if it does not already exist.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id    INTEGER PRIMARY KEY,
            username   TEXT,
            first_name TEXT,
            last_name  TEXT,
            created_at TEXT
        )
        """
    )

    # Groups table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS groups (
            group_id   INTEGER PRIMARY KEY,
            title      TEXT,
            created_at TEXT
        )
        """
    )

    # User–group relation table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS user_groups (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id  INTEGER,
            group_id INTEGER
        )
        """
    )

    # Anonymous messages table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS anon_messages (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id   INTEGER,
            receiver_id INTEGER,
            message     TEXT,
            created_at  TEXT
        )
        """
    )

    conn.commit()
    conn.close()


# ---------------- USER FUNCTIONS ----------------


def add_user(
    user_id: int,
    username: Optional[str],
    first_name: Optional[str],
    last_name: Optional[str],
) -> None:
    """
    Insert a user into the database if they do not already exist.

    Uses INSERT OR IGNORE so duplicate user_id will not raise an error.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, username, first_name, last_name, datetime.utcnow().isoformat()),
    )

    conn.commit()
    conn.close()


def get_user(user_id: int) -> Optional[tuple]:
    """
    Retrieve a user row by user_id.

    Returns:
        A tuple representing the user row, or None if not found.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()

    conn.close()
    return result


def user_exists(user_id: int) -> bool:
    """
    Check whether a user with the given user_id is already registered.

    Used by features that require the target user to have started the bot at least once.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT 1 FROM users WHERE user_id = ? LIMIT 1", (user_id,))
    exists = cursor.fetchone() is not None

    conn.close()
    return exists


def get_user_id_by_username(username: str) -> Optional[int]:
    """
    Resolve a user_id by Telegram username.

    The input can be:
      - "@exampleuser"
      - "exampleuser"

    Returns:
        The user_id if found, otherwise None.
    """
    if not username:
        return None

    username = username.strip()

    # Strip leading @ if present
    if username.startswith("@"):
        username = username[1:]

    if not username:
        return None

    conn = get_connection()
    cursor = conn.cursor()

    # Case-insensitive lookup
    cursor.execute(
        """
        SELECT user_id FROM users
        WHERE LOWER(username) = LOWER(?)
        LIMIT 1
        """,
        (username,),
    )
    row = cursor.fetchone()

    conn.close()

    if row:
        return int(row[0])

    return None


# ---------------- GROUP FUNCTIONS ----------------


def add_group(group_id: int, title: str) -> None:
    """
    Insert a group into the database if it does not already exist.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT OR IGNORE INTO groups (group_id, title, created_at)
        VALUES (?, ?, ?)
        """,
        (group_id, title, datetime.utcnow().isoformat()),
    )

    conn.commit()
    conn.close()


def get_group(group_id: int) -> Optional[tuple]:
    """
    Retrieve a group row by group_id.

    Returns:
        A tuple representing the group row, or None if not found.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM groups WHERE group_id = ?", (group_id,))
    result = cursor.fetchone()

    conn.close()
    return result


# ---------------- RELATION USER - GROUP ----------------


def add_user_to_group(user_id: int, group_id: int) -> None:
    """
    Register a user as a member of a group.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO user_groups (user_id, group_id)
        VALUES (?, ?)
        """,
        (user_id, group_id),
    )

    conn.commit()
    conn.close()


def get_group_users(group_id: int) -> List[int]:
    """
    Get all user IDs that belong to a given group_id.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT user_id FROM user_groups WHERE group_id = ?
        """,
        (group_id,),
    )

    result = cursor.fetchall()
    conn.close()
    return [int(row[0]) for row in result]


# ---------------- ANONYMOUS MESSAGES ----------------


def add_anon_message(sender_id: int, receiver_id: int, msg: str) -> None:
    """
    Store an anonymous message from sender_id to receiver_id.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO anon_messages (sender_id, receiver_id, message, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (sender_id, receiver_id, msg, datetime.utcnow().isoformat()),
    )

    conn.commit()
    conn.close()


def get_user_messages(user_id: int) -> list[tuple[Any, ...]]:
    """
    Retrieve all anonymous messages received by the given user_id.

    Returns:
        A list of rows from the anon_messages table.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM anon_messages WHERE receiver_id = ?
        """,
        (user_id,),
    )

    result = cursor.fetchall()
    conn.close()
    return result
