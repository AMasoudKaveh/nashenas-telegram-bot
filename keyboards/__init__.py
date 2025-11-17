# nashenas_bot/keyboards/__init__.py
"""
Keyboard factories exported by the keyboards package.

Usage example:
    from nashenas_bot.keyboards import main_menu_keyboard, random_chat_keyboard
"""

from .main_menu import main_menu_keyboard
from .random_chat_kb import random_chat_keyboard

__all__ = ["main_menu_keyboard", "random_chat_keyboard"]
