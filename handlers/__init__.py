# handlers/__init__.py
"""
Router exports for the Nashenas bot.

This module aggregates all route handlers so they can be imported
conveniently from `handlers` in the main application.
"""

from .start import router as start_router
from .callbacks import router as callback_router
from .anonymous_chat import router as anonymous_chat_router
from .anonymous_message import router as anonymous_message_router
from .help_rules import help_rules_router
from .special_contact import special_contact_router

__all__ = [
    "start_router",
    "callback_router",
    "anonymous_chat_router",
    "anonymous_message_router",
    "help_rules_router",
    "special_contact_router",
]
