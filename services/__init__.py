# services/__init__.py
"""
Service-layer helpers for the Nashenas bot.

This package aggregates commonly used utilities so they can be imported
conveniently from `services`, for example:

    from services import logger, check_spam, clean_text
"""

from .logger import logger
from .user_utils import (
    register_user,
    get_user_info,
    block_user_local,
    is_user_blocked_local,
)
from .chat_utils import (
    join_queue,
    leave_queue,
    find_partner,
    connect_users,
    get_partner,
    end_chat,
)
from .text_utils import (
    clean_text,
    is_bad_text,
)
from .antispam import (
    check_spam,
)

__all__ = [
    "logger",
    "register_user",
    "get_user_info",
    "block_user_local",
    "is_user_blocked_local",
    "join_queue",
    "leave_queue",
    "find_partner",
    "connect_users",
    "get_partner",
    "end_chat",
    "clean_text",
    "is_bad_text",
    "check_spam",
]
