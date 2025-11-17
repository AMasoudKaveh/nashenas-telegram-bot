from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Create the main reply keyboard for the bot.

    Buttons:
      - "💬 چت ناشناس"           → start random anonymous chat
      - "📨 پیام ناشناس"         → generate personal anonymous link
      - "به مخاطب خاصم وصلم کن" → send an anonymous message to a specific user
      - "ℹ️ راهنما"              → show help
      - "📜 قوانین"              → show rules
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="💬 چت ناشناس"),
                KeyboardButton(text="📨 پیام ناشناس"),
            ],
            [
                KeyboardButton(text="به مخاطب خاصم وصلم کن"),
            ],
            [
                KeyboardButton(text="ℹ️ راهنما"),
                KeyboardButton(text="📜 قوانین"),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="یکی از گزینه‌ها رو انتخاب کن…",
    )
    return keyboard
