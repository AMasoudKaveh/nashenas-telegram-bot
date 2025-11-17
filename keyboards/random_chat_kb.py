from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def random_chat_keyboard() -> ReplyKeyboardMarkup:
    """
    Create the reply keyboard used during anonymous chat.

    Buttons:
      - "⏭ بعدی"      → find a new random partner
      - "❌ پایان چت" → end the current chat
    """
    keyboard = [
        [
            KeyboardButton(text="⏭ بعدی"),
            KeyboardButton(text="❌ پایان چت"),
        ]
    ]
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
    )
